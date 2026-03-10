"""
Gemini-backed LLM judge.

Uses gemini-2.0-flash (same model as the agent-service) for cost/infra reuse.

Key design decisions:
  - temperature=0.1   → deterministic scoring, not creative writing
  - 3-run averaging   → reduces Gemini's higher variance vs GPT-class models
  - strict JSON only  → enforced in prompt + parse guard with retry
  - reason quality    → retries if reason string < 20 chars (low-effort output)
  - graceful fallback → returns default_score() if GEMINI_API_KEY not set
"""
import json
import logging
import os
import time
from typing import Optional

import httpx

from evals.judge.base import BaseJudge
from evals.models import JudgeScore, TestCase

logger = logging.getLogger(__name__)

_GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
_MODEL = "gemini-2.0-flash"
_RATE_LIMIT_SECONDS = 1.0          # 1 req/sec to avoid quota errors
_JUDGE_RUNS = 3                    # number of calls to average per case
_MAX_RETRIES = 2                   # per individual call
_MIN_REASON_LEN = 20               # shorter reason = low-quality, retry


def _build_judge_prompt(message: str, test_case: TestCase) -> str:
    inp = test_case.input
    return f"""You are evaluating a financial AI assistant's intervention message.

USER CONTEXT:
- Category      : {inp.category}
- Monthly budget: ₹{inp.monthly_budget}
- Spent so far  : ₹{inp.spent_so_far}
- Days elapsed  : {inp.days_elapsed}
- Daily limit   : {f"₹{inp.daily_limit}" if inp.daily_limit else "none"}
- Account frozen: {inp.is_blocked}

AI INTERVENTION MESSAGE:
\"{message}\"

EXPECTED BEHAVIOUR:
- Should trigger   : {test_case.expected.triggered}
- Expected severity: {test_case.expected.severity}
- Expected tone    : {test_case.expected.tone}

SCORING RUBRIC — score each dimension strictly:
1. correctness (0–4)
   4 = factually accurate ₹ amounts, no hallucinated numbers
   2 = roughly correct but imprecise
   0 = wrong numbers or missing financial context

2. actionability (0–3)
   3 = clear, specific 1-tap action suggested
   1 = vague suggestion ("spend less")
   0 = no action

3. behavioral_impact (0–3)
   3 = loss-framed, emotionally compelling, likely to change behaviour
   1 = neutral / informational
   0 = does not motivate any change

final_score = correctness + actionability + behavioral_impact  (max 10)

Return ONLY valid JSON. No text outside JSON. No markdown. No explanation.
{{
  "correctness": <integer 0-4>,
  "actionability": <integer 0-3>,
  "behavioral_impact": <integer 0-3>,
  "final_score": <integer 0-10>,
  "reason": "<one concise sentence explaining the score>"
}}"""


class GeminiJudge(BaseJudge):
    """LLM-as-Judge backed by Gemini 2.0 Flash."""

    def __init__(self, api_key: Optional[str] = None, model: str = _MODEL):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self._last_call_time: float = 0.0

    # ── Public ────────────────────────────────────────────────────────────────

    def score(self, message: str, test_case: TestCase) -> JudgeScore:
        """
        Runs _JUDGE_RUNS independent evaluations and returns the averaged score.
        Returns default_score() if API key is missing or all retries fail.
        """
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set — skipping LLM judge")
            return self.default_score("GEMINI_API_KEY not configured")

        if not message:
            return self.default_score("No message to evaluate")

        raw_scores: list[JudgeScore] = []
        for run in range(_JUDGE_RUNS):
            result = self._call_with_retry(message, test_case)
            if result:
                raw_scores.append(result)

        if not raw_scores:
            return self.default_score("All judge calls failed")

        return self._average(raw_scores)

    # ── Private ───────────────────────────────────────────────────────────────

    def _call_with_retry(self, message: str, test_case: TestCase) -> Optional[JudgeScore]:
        """Single judge call with up to _MAX_RETRIES attempts."""
        prompt = _build_judge_prompt(message, test_case)
        for attempt in range(_MAX_RETRIES):
            try:
                self._rate_limit()
                raw = self._call_gemini(prompt)
                parsed = self._parse_response(raw)
                if parsed:
                    return parsed
                logger.debug(f"Judge attempt {attempt+1}: bad parse, retrying...")
            except Exception as e:
                logger.warning(f"Judge attempt {attempt+1} failed: {e}")
        return None

    def _call_gemini(self, prompt: str) -> str:
        """Makes the REST call to Gemini and returns the raw text response."""
        url = f"{_GEMINI_API_BASE}/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 256,
            },
        }
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("Empty candidates in Gemini response")

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise ValueError("Empty parts in Gemini response")

        return parts[0].get("text", "")

    def _parse_response(self, raw: str) -> Optional[JudgeScore]:
        """
        Parses Gemini's text into a JudgeScore.
        Strips markdown fences if present. Validates all required fields.
        """
        text = raw.strip()

        # Strip ```json ... ``` fences (Gemini sometimes ignores "no markdown")
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]).strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            logger.debug(f"JSON parse failed on: {text[:120]!r}")
            return None

        required = {"correctness", "actionability", "behavioral_impact",
                    "final_score", "reason"}
        if not required.issubset(data.keys()):
            logger.debug(f"Missing keys in judge response: {data.keys()}")
            return None

        reason = str(data.get("reason", ""))
        if len(reason) < _MIN_REASON_LEN:
            logger.debug(f"Low-quality reason ({len(reason)} chars): {reason!r}")
            return None

        return JudgeScore(
            correctness=float(data["correctness"]),
            actionability=float(data["actionability"]),
            behavioral_impact=float(data["behavioral_impact"]),
            final_score=float(data["final_score"]),
            reason=reason,
            runs=1,
        )

    @staticmethod
    def _average(scores: list[JudgeScore]) -> JudgeScore:
        """Averages multiple JudgeScore runs into one."""
        n = len(scores)
        return JudgeScore(
            correctness=round(sum(s.correctness for s in scores) / n, 2),
            actionability=round(sum(s.actionability for s in scores) / n, 2),
            behavioral_impact=round(sum(s.behavioral_impact for s in scores) / n, 2),
            final_score=round(sum(s.final_score for s in scores) / n, 2),
            reason=scores[-1].reason,   # last run's reason (most stable)
            runs=n,
        )

    def _rate_limit(self):
        """Ensures at least _RATE_LIMIT_SECONDS between API calls."""
        elapsed = time.monotonic() - self._last_call_time
        if elapsed < _RATE_LIMIT_SECONDS:
            time.sleep(_RATE_LIMIT_SECONDS - elapsed)
        self._last_call_time = time.monotonic()
