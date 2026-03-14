"""Evaluation engine for scoring agent task results."""

from dataclasses import dataclass

from agentbench.adapters.base import AgentResult
from agentbench.sandbox import Sandbox
from agentbench.schema import EvalType, Task


@dataclass
class EvalScore:
    """Score from evaluating an agent's task result."""

    task_id: str
    agent_name: str
    # Overall score 0-1
    score: float
    # Per-criterion scores (for composite/llm-judge)
    details: dict[str, float]
    # Whether the auto tests passed
    auto_passed: bool | None = None
    # LLM judge narrative (if applicable)
    judge_narrative: str = ""
    # pass^k: success rate over k trials
    pass_at_k: float | None = None


class Evaluator:
    """Evaluates agent results against task criteria."""

    def evaluate(
        self,
        task: Task,
        result: AgentResult,
        sandbox: Sandbox,
    ) -> EvalScore:
        """Score an agent's result on a task."""
        eval_type = task.evaluation.type

        if eval_type == EvalType.AUTO:
            return self._eval_auto(task, result, sandbox)
        elif eval_type == EvalType.LLM_JUDGE:
            return self._eval_llm_judge(task, result, sandbox)
        elif eval_type == EvalType.COMPOSITE:
            return self._eval_composite(task, result, sandbox)
        else:
            return self._eval_human_placeholder(task, result)

    def _eval_auto(self, task: Task, result: AgentResult, sandbox: Sandbox) -> EvalScore:
        """Run automated tests and score based on pass rate."""
        auto_cfg = task.evaluation.auto
        if not auto_cfg:
            return EvalScore(
                task_id=task.id, agent_name=result.agent_name,
                score=0.0, details={}, auto_passed=False,
            )

        try:
            test_result = sandbox.run_command(
                auto_cfg.command,
                timeout=task.evaluation.timeout_seconds,
            )
            passed = test_result.returncode == 0
            # Parse pytest output for pass rate if available
            score = 1.0 if passed else self._parse_pass_rate(test_result.stdout)
        except Exception:
            passed = False
            score = 0.0

        return EvalScore(
            task_id=task.id,
            agent_name=result.agent_name,
            score=score,
            details={"auto_pass_rate": score},
            auto_passed=passed,
        )

    def _eval_llm_judge(self, task: Task, result: AgentResult, sandbox: Sandbox) -> EvalScore:
        """Use an LLM to judge the quality of the agent's output."""
        judge_cfg = task.evaluation.llm_judge
        if not judge_cfg:
            return EvalScore(
                task_id=task.id, agent_name=result.agent_name,
                score=0.0, details={},
            )

        # Collect output files from workspace
        output_content = self._collect_workspace_outputs(sandbox)

        # Build judge prompt
        judge_prompt = self._build_judge_prompt(
            task_prompt=task.prompt,
            rubric=judge_cfg.rubric,
            agent_output=result.stdout,
            workspace_files=output_content,
            reference=judge_cfg.reference_answer,
        )

        # Call LLM judge
        scores = self._call_llm_judge(judge_prompt, judge_cfg.model)

        avg_score = sum(scores.values()) / max(len(scores), 1) / 10.0  # normalize to 0-1

        return EvalScore(
            task_id=task.id,
            agent_name=result.agent_name,
            score=avg_score,
            details=scores,
            judge_narrative=str(scores),
        )

    def _eval_composite(self, task: Task, result: AgentResult, sandbox: Sandbox) -> EvalScore:
        """Combine auto and LLM-judge scores."""
        auto_score = self._eval_auto(task, result, sandbox)
        judge_score = self._eval_llm_judge(task, result, sandbox)

        # Weight: 60% auto, 40% judge
        combined = auto_score.score * 0.6 + judge_score.score * 0.4

        details = {**auto_score.details, **judge_score.details}
        details["auto_weight"] = 0.6
        details["judge_weight"] = 0.4

        return EvalScore(
            task_id=task.id,
            agent_name=result.agent_name,
            score=combined,
            details=details,
            auto_passed=auto_score.auto_passed,
            judge_narrative=judge_score.judge_narrative,
        )

    def _eval_human_placeholder(self, task: Task, result: AgentResult) -> EvalScore:
        """Placeholder for human evaluation — returns pending score."""
        return EvalScore(
            task_id=task.id,
            agent_name=result.agent_name,
            score=-1.0,  # -1 = pending human review
            details={"status": "awaiting_human_review"},
        )

    def _parse_pass_rate(self, pytest_output: str) -> float:
        """Parse pytest output to extract pass rate."""
        # Look for "X passed, Y failed" pattern
        import re
        match = re.search(r"(\d+) passed", pytest_output)
        total_match = re.search(r"(\d+) passed(?:.*?(\d+) failed)?", pytest_output)
        if total_match:
            passed = int(total_match.group(1))
            failed = int(total_match.group(2) or 0)
            total = passed + failed
            return passed / total if total > 0 else 0.0
        return 0.0

    def _collect_workspace_outputs(self, sandbox: Sandbox) -> dict[str, str]:
        """Read key output files from workspace."""
        outputs = {}
        for ext in ("*.md", "*.json", "*.txt", "*.py"):
            for f in sandbox.workspace.glob(ext):
                try:
                    outputs[f.name] = f.read_text()[:5000]  # cap at 5k chars
                except Exception:
                    pass
        return outputs

    def _build_judge_prompt(
        self,
        task_prompt: str,
        rubric: str,
        agent_output: str,
        workspace_files: dict[str, str],
        reference: str,
    ) -> str:
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
{agent_output[:3000]}
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
        """Call an LLM to judge. Returns criterion->score mapping."""
        import json

        try:
            import anthropic

            client = anthropic.Anthropic()
            response = client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text
            # Extract JSON from response
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except ImportError:
            pass  # anthropic not installed, try openai
        except Exception:
            pass

        try:
            import openai

            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
            )
            text = response.choices[0].message.content or ""
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except Exception:
            pass

        return {"error": 0.0}
