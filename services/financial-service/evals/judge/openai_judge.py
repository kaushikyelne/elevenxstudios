"""
OpenAI judge — optional future implementation.

Implements the same BaseJudge interface so it can be swapped in
with zero changes to runner.py or run_evals.py.

Usage (when ready):
    from evals.judge.openai_judge import OpenAIJudge
    judge = OpenAIJudge()

Requires: pip install openai, OPENAI_API_KEY set.
"""
from evals.judge.base import BaseJudge
from evals.models import JudgeScore, TestCase


class OpenAIJudge(BaseJudge):
    """Placeholder — swap in gpt-4o-mini when needed."""

    def score(self, message: str, test_case: TestCase) -> JudgeScore:
        raise NotImplementedError(
            "OpenAIJudge is not yet implemented. "
            "Use GeminiJudge (default) or implement this class."
        )
