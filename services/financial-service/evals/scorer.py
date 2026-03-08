"""
Heuristic scorer for intervention engine outputs.

Scores each response 0–10 across three axes:
  Correctness  (0–4): structural + factual accuracy
  Actionability (0–3): presence of clear, executable actions
  Tone          (0–3): loss-framing strength

Also validates hard constraints (must_contain / must_not_contain / severity).
"""
from typing import List, Optional
from evals.models import ScoreBreakdown, EvalResult, TestCase, LatencyMetrics, CostMetrics


# ─── Keyword banks ────────────────────────────────────────────────────────────

ACTION_WORDS = {"reduce", "limit", "set", "cut", "freeze", "adjust",
                "lower", "block", "stop", "cap", "keep"}

LOSS_FRAME_WORDS = {"waste", "wasted", "wasting", "over", "blown",
                    "losing", "lost", "extra", "additional", "exceeded"}


# ─── Public API ───────────────────────────────────────────────────────────────

def score_heuristic(
    response_message: Optional[str],
    response_triggered: bool,
    response_severity: Optional[str],
    response_actions: List[str],
    test_case: TestCase,
) -> tuple[ScoreBreakdown, List[str]]:
    """
    Returns (ScoreBreakdown, list_of_failure_reasons).
    An empty failure list means all hard constraints passed.
    """
    failures: List[str] = []
    msg = (response_message or "").lower()
    raw_msg = response_message or ""

    # ── Correctness (0–4) ────────────────────────────────────────────────────
    correctness = 0.0

    # +2: Currency symbol present (means numbers are actually in the message)
    if "₹" in raw_msg:
        correctness += 2
    elif response_triggered:
        # triggered but no ₹ — partial credit, flag it
        failures.append("message lacks ₹ symbol despite being triggered")

    # +2: triggered matches expected
    if response_triggered == test_case.expected.triggered:
        correctness += 2
    else:
        failures.append(
            f"triggered={response_triggered} but expected={test_case.expected.triggered}"
        )

    # ── Actionability (0–3) ──────────────────────────────────────────────────
    actionability = 0.0
    if response_triggered:
        if test_case.expected.has_action and response_actions:
            # Check if any action label contains an action word
            action_text = " ".join(a.lower() for a in response_actions)
            matches = sum(1 for w in ACTION_WORDS if w in action_text)
            actionability = min(matches * 1.5, 3)
            if actionability == 0:
                failures.append("suggested_actions present but lack action verbs")
        elif test_case.expected.has_action and not response_actions:
            failures.append("expected actions but suggested_actions is empty")
        elif not test_case.expected.has_action:
            actionability = 3  # no action expected, that's fine

    # ── Tone / Loss-framing (0–3) ────────────────────────────────────────────
    tone = 0.0
    if response_triggered and test_case.expected.tone == "loss_framed":
        matches = sum(1 for w in LOSS_FRAME_WORDS if w in msg)
        tone = min(matches * 1.0, 3)
        if tone == 0:
            failures.append("loss-framing words absent from triggered message")
    elif response_triggered and test_case.expected.tone == "warning":
        # Warning tone: just needs to sound directive (freeze / block / limit)
        if any(w in msg for w in {"freeze", "block", "active", "limit", "stop"}):
            tone = 3
        else:
            tone = 1
    elif not response_triggered:
        tone = 3  # no message expected → tone constraint doesn't apply

    # ── Hard constraint: severity ─────────────────────────────────────────────
    if test_case.expected.severity and response_severity:
        if response_severity.lower() not in test_case.expected.severity:
            failures.append(
                f"severity={response_severity!r} not in allowed={test_case.expected.severity}"
            )

    # ── Hard constraint: must_contain ────────────────────────────────────────
    for token in test_case.expected.must_contain:
        if token not in raw_msg:
            failures.append(f"must_contain missing: {token!r}")

    # ── Hard constraint: must_not_contain ────────────────────────────────────
    for token in test_case.expected.must_not_contain:
        if token in raw_msg:
            failures.append(f"must_not_contain violated: {token!r}")

    total = round(correctness + actionability + tone, 2)
    return ScoreBreakdown(
        correctness=correctness,
        actionability=actionability,
        tone=tone,
        total=total,
    ), failures


def build_eval_result(
    case: TestCase,
    response_triggered: bool,
    response_severity: Optional[str],
    response_message: Optional[str],
    response_actions: List[str],
    latency: LatencyMetrics,
    threshold: float = 6.0,
) -> EvalResult:
    """Assemble a full EvalResult from raw response fields."""
    breakdown, failures = score_heuristic(
        response_message=response_message,
        response_triggered=response_triggered,
        response_severity=response_severity,
        response_actions=response_actions,
        test_case=case,
    )
    passed = breakdown.total >= threshold and len(failures) == 0
    return EvalResult(
        case_id=case.id,
        description=case.description,
        alert_type=case.alert_type,
        passed=passed,
        heuristic=breakdown,
        judge=None,           # populated later by runner if --judge enabled
        latency=latency,
        cost=CostMetrics(),
        failures=failures,
        response_message=response_message,
        response_triggered=response_triggered,
        response_severity=response_severity,
    )
