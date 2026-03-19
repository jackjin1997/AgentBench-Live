"""Pydantic models for structured LLM judge output."""

from __future__ import annotations

try:
    from pydantic import BaseModel, Field
except ImportError:
    # Pydantic not installed — provide stub so module can be imported
    # without pydantic; actual usage will raise at call site.
    BaseModel = None  # type: ignore[assignment,misc]
    Field = None  # type: ignore[assignment]

if BaseModel is not None:

    class CriterionScore(BaseModel):
        """Score for a single evaluation criterion."""

        name: str = Field(description="Criterion name from the rubric")
        score: int = Field(ge=1, le=10, description="Score from 1-10")
        reasoning: str = Field(description="Brief justification for the score")

    class JudgeVerdict(BaseModel):
        """Complete judge evaluation result."""

        criteria: list[CriterionScore] = Field(
            description="Scores for each rubric criterion"
        )
        overall_assessment: str = Field(
            description="Brief overall assessment of the agent's work"
        )

        def to_score_dict(self) -> dict[str, float]:
            """Convert to criterion->score mapping."""
            return {c.name: float(c.score) for c in self.criteria}

else:
    CriterionScore = None  # type: ignore[assignment,misc]
    JudgeVerdict = None  # type: ignore[assignment,misc]
