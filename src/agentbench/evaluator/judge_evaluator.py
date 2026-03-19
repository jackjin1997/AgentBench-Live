"""LLM Judge evaluator — uses an LLM to score agent output quality."""

from __future__ import annotations

import json
import logging
import re

from agentbench.adapters.base import AgentResult
from agentbench.config import BenchmarkConfig, load_config
from agentbench.evaluator.models import EvalScore
from agentbench.evaluator.workspace import collect_workspace_outputs
from agentbench.sandbox import Sandbox
from agentbench.schema import Task

logger = logging.getLogger(__name__)

_CODE_KEYWORDS = re.compile(r"\b(def|class|import|function|return)\b")


class LLMJudgeEvaluator:
    """Evaluates agent output using an LLM judge with structured output."""

    def __init__(self, config: BenchmarkConfig | None = None):
        self._config = config or load_config()

    def evaluate(self, task: Task, result: AgentResult, sandbox: Sandbox) -> EvalScore:
        judge_cfg = task.evaluation.llm_judge
        if not judge_cfg:
            return EvalScore(
                task_id=task.id, agent_name=result.agent_name,
                score=0.0, details={},
            )

        output_content = collect_workspace_outputs(sandbox, self._config)
        judge_prompt = self._build_judge_prompt(
            task_prompt=task.prompt,
            rubric=judge_cfg.rubric,
            agent_output=result.stdout,
            workspace_files=output_content,
            reference=judge_cfg.reference_answer,
        )

        scores = self._call_llm_judge(judge_prompt, judge_cfg.model)

        if "error" in scores:
            fallback = self._heuristic_score(result, output_content)
            return EvalScore(
                task_id=task.id,
                agent_name=result.agent_name,
                score=fallback,
                details={"heuristic_score": fallback, "judge_fallback": True},
                judge_narrative="Heuristic fallback (LLM judge unavailable)",
            )

        avg_score = sum(scores.values()) / max(len(scores), 1) / 10.0

        return EvalScore(
            task_id=task.id,
            agent_name=result.agent_name,
            score=avg_score,
            details=scores,
            judge_narrative=str(scores),
        )

    def _heuristic_score(
        self, result: AgentResult, output_content: dict[str, str],
    ) -> float:
        """Compute a heuristic fallback score when the LLM judge is unavailable.

        The score is capped at 0.6 to be honest that this is not a real
        LLM evaluation.
        """
        logger.warning(
            "LLM judge unavailable; using heuristic fallback (max 0.6)"
        )
        score = 0.0

        # Longer stdout suggests the agent did meaningful work
        if len(result.stdout) > 200:
            score += 0.2

        # Workspace files created/modified by the agent
        if output_content and any(len(v) > 0 for v in output_content.values()):
            score += 0.2

        # Output contains code-like content
        combined = result.stdout + " ".join(output_content.values())
        if _CODE_KEYWORDS.search(combined):
            score += 0.1

        # Agent exited successfully
        if result.success and result.exit_code == 0:
            score += 0.1

        return min(score, 0.6)

    def _build_judge_prompt(
        self,
        task_prompt: str,
        rubric: str,
        agent_output: str,
        workspace_files: dict[str, str],
        reference: str,
    ) -> str:
        cap = self._config.eval.agent_output_cap
        files_section = "\n".join(
            f"### {name}\n```\n{content}\n```"
            for name, content in workspace_files.items()
        )
        ref_section = f"\n## Reference Answer\n{reference}" if reference else ""

        return f"""You are an expert evaluator for AI agent benchmarks.

## Task Given to Agent
{task_prompt}

## Agent's Terminal Output
```
{agent_output[:cap]}
```

## Files Produced by Agent
{files_section}
{ref_section}

## Rubric
{rubric}

## Instructions
Score each criterion listed in the rubric on a scale of 1-10.
Return a JSON object with criterion names as keys and integer scores as values.
Be strict but fair. A score of 7 means "good", 9 means "excellent", 5 means "mediocre".
"""

    def _call_llm_judge(self, prompt: str, model: str) -> dict[str, float]:
        """Call an LLM judge, preferring structured output when available."""
        max_tokens = self._config.eval.judge_max_tokens

        # Try structured output via Anthropic tool-use
        scores = self._try_anthropic_structured(prompt, model, max_tokens)
        if scores is not None:
            return scores

        # Try structured output via OpenAI response_format
        scores = self._try_openai_structured(prompt, max_tokens)
        if scores is not None:
            return scores

        # Try Google Gemini
        scores = self._try_gemini(prompt, max_tokens)
        if scores is not None:
            return scores

        logger.error("All LLM judge backends failed for model %s", model)
        return {"error": 0.0}

    def _try_anthropic_structured(
        self, prompt: str, model: str, max_tokens: int
    ) -> dict[str, float] | None:
        """Try Anthropic API with tool-use for structured output."""
        try:
            import anthropic
        except ImportError:
            return None

        judge_tool = {
            "name": "submit_scores",
            "description": "Submit evaluation scores for each rubric criterion",
            "input_schema": {
                "type": "object",
                "properties": {
                    "scores": {
                        "type": "object",
                        "description": "Criterion names as keys, integer scores (1-10) as values",
                        "additionalProperties": {"type": "integer"},
                    }
                },
                "required": ["scores"],
            },
        }

        try:
            client = anthropic.Anthropic()
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                tools=[judge_tool],
                tool_choice={"type": "tool", "name": "submit_scores"},
                messages=[{"role": "user", "content": prompt}],
            )
            # Extract scores from tool use block
            for block in response.content:
                if block.type == "tool_use" and block.name == "submit_scores":
                    raw = block.input.get("scores", {})
                    return {k: float(v) for k, v in raw.items()}

            # Fallback: parse text response
            return self._extract_json_from_text(response)
        except Exception as exc:
            logger.warning("Anthropic judge call failed: %s", exc)
            return None

    def _try_openai_structured(
        self, prompt: str, max_tokens: int
    ) -> dict[str, float] | None:
        """Try OpenAI API with JSON response_format."""
        try:
            import openai
        except ImportError:
            return None

        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            text = response.choices[0].message.content or ""
            return json.loads(text)
        except Exception as exc:
            logger.warning("OpenAI judge call failed: %s", exc)
            return None

    def _try_gemini(
        self, prompt: str, max_tokens: int
    ) -> dict[str, float] | None:
        """Try Google Gemini API for JSON scoring."""
        try:
            import google.generativeai as genai
        except ImportError:
            return None

        import os
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return None

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(
                prompt + "\n\nRespond with ONLY a JSON object, no other text.",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    response_mime_type="application/json",
                ),
            )
            text = response.text or ""
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(text[start:end])
                # Handle nested {"scores": {...}} format
                if "scores" in data and isinstance(data["scores"], dict):
                    return {k: float(v) for k, v in data["scores"].items()}
                return {k: float(v) for k, v in data.items()}
            return None
        except Exception as exc:
            logger.warning("Gemini judge call failed: %s", exc)
            return None

    @staticmethod
    def _extract_json_from_text(response) -> dict[str, float] | None:
        """Fallback: extract JSON from text response content."""
        for block in response.content:
            if hasattr(block, "text"):
                text = block.text
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    try:
                        return json.loads(text[start:end])
                    except json.JSONDecodeError:
                        pass
        return None
