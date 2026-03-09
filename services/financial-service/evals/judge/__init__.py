"""Judge package — exports get_judge() factory."""
from evals.judge.gemini_judge import GeminiJudge


def get_judge():
    """Returns the default judge (Gemini). Falls back gracefully if no API key."""
    return GeminiJudge()
