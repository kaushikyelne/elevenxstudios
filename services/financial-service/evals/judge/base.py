"""
Abstract base class for LLM judges.
Any new judge (OpenAI, Anthropic, etc.) implements this interface.
"""
from abc import ABC, abstractmethod
from evals.models import JudgeScore, TestCase


class BaseJudge(ABC):
    """Interface that all judge implementations must satisfy."""

    @abstractmethod
    def score(self, message: str, test_case: TestCase) -> JudgeScore:
        """
        Score a single intervention message against its test case.

        Args:
            message:   The intervention message produced by the engine.
            test_case: The full TestCase (for context + expected values).

        Returns:
            JudgeScore with per-dimension scores and a human-readable reason.
        """
        ...

    def default_score(self, reason: str = "Judge unavailable") -> JudgeScore:
        """Safe fallback when the judge cannot be reached."""
        return JudgeScore(
            correctness=0,
            actionability=0,
            behavioral_impact=0,
            final_score=0,
            reason=reason,
            runs=0,
        )
