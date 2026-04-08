"""
Core evaluation runner.

Loads test cases → seeds in-memory SQLite → calls check_and_intervene()
→ heuristic score → optional LLM judge → regression delta → results JSON.

Uses asyncio.run() since check_and_intervene is async.
In-memory SQLite pattern mirrors the existing tests in tests/test_intervention.py.
"""
import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from unittest.mock import AsyncMock, patch

# ── Make app.* importable without installing the package ─────────────────────
_SERVICE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SERVICE_ROOT))

from sqlmodel import Session, SQLModel, create_engine

from app.models import Budget, Transaction, Alert
from app.engine.intervention import check_and_intervene
from app.schemas import InterventionSeverity

from evals.models import (
    TestCase, TestInput, ExpectedOutput,
    EvalResult, RunSummary, LatencyMetrics, CostMetrics,
)
from evals.scorer import build_eval_result

logger = logging.getLogger(__name__)

# ─── Helpers: Test case loading ───────────────────────────────────────────────

def load_test_cases(path: Path) -> List[TestCase]:
    with open(path) as f:
        raw = json.load(f)
    cases = []
    for item in raw:
        inp_data = item["input"]
        exp_data = item["expected"]
        cases.append(TestCase(
            id=item["id"],
            description=item["description"],
            alert_type=item["alert_type"],
            input=TestInput(
                category=inp_data["category"],
                monthly_budget=inp_data.get("monthly_budget"),
                spent_so_far=inp_data.get("spent_so_far", 0),
                days_elapsed=inp_data.get("days_elapsed", 15),
                daily_limit=inp_data.get("daily_limit"),
                is_blocked=inp_data.get("is_blocked", False),
                transaction_amount=inp_data.get("transaction_amount", 0),
                prior_today_spend=inp_data.get("prior_today_spend", 0),
                repeat_call=inp_data.get("repeat_call", False),
            ),
            expected=ExpectedOutput(
                triggered=exp_data["triggered"],
                severity=exp_data.get("severity", []),
                must_contain=exp_data.get("must_contain", []),
                must_not_contain=exp_data.get("must_not_contain", []),
                tone=exp_data.get("tone", "none"),
                has_action=exp_data.get("has_action", False),
            ),
            metadata=item.get("metadata", {}),
        ))
    return cases


# ─── Helpers: DB fixture ──────────────────────────────────────────────────────

def _make_engine():
    """Fresh in-memory SQLite engine for each test case."""
    engine = create_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(engine)
    return engine


def _seed(session: Session, case: TestCase) -> Transaction:
    """Seeds Budget + prior transactions, returns the triggering Transaction."""
    inp = case.input

    # Budget (only if monthly_budget is set)
    if inp.monthly_budget:
        budget = Budget(
            category=inp.category,
            limit_amount=inp.monthly_budget,
            spent_amount=inp.spent_so_far,
            daily_limit=inp.daily_limit,
            is_blocked=inp.is_blocked,
        )
        session.add(budget)

    # Prior-today transactions (for daily_limit_breach cases)
    if inp.prior_today_spend > 0:
        prior_tx = Transaction(
            amount=inp.prior_today_spend,
            description="prior spend today",
            category=inp.category,
            date=datetime.utcnow(),
        )
        session.add(prior_tx)

    # The triggering transaction
    tx = Transaction(
        amount=inp.transaction_amount,
        description=f"eval tx for {inp.category}",
        category=inp.category,
        date=datetime.utcnow(),
    )
    session.add(tx)
    session.commit()
    return tx


# ─── Core runner ──────────────────────────────────────────────────────────────

async def _run_case(case: TestCase, threshold: float) -> EvalResult:
    """
    Executes one test case against check_and_intervene() using in-memory SQLite.
    Mocks _fire_notification to keep evals offline.
    """
    engine = _make_engine()

    with patch("app.engine.intervention._fire_notification", new_callable=AsyncMock):
        with Session(engine) as session:
            tx = _seed(session, case)

            t0 = time.monotonic()
            result = await check_and_intervene(session, tx)
            engine_ms = (time.monotonic() - t0) * 1000

            # Adversarial: repeat_call → call again to trigger cooldown suppression
            if case.input.repeat_call:
                t0 = time.monotonic()
                result = await check_and_intervene(session, tx)
                engine_ms += (time.monotonic() - t0) * 1000

    # Extract response fields
    response_triggered = result.triggered
    response_severity = result.severity.value if result.severity else None
    response_message = result.message
    response_actions = [a.label for a in result.suggested_actions] if result.suggested_actions else []

    return build_eval_result(
        case=case,
        response_triggered=response_triggered,
        response_severity=response_severity,
        response_message=response_message,
        response_actions=response_actions,
        latency=LatencyMetrics(engine_ms=round(engine_ms, 2)),
        threshold=threshold,
    )


def run_all(
    cases: List[TestCase],
    threshold: float = 6.0,
    judge=None,
) -> List[EvalResult]:
    """Runs all test cases synchronously. Returns list of EvalResults."""
    results = []
    for case in cases:
        eval_result = asyncio.run(_run_case(case, threshold))

        # LLM judge (optional, only for triggered cases with a message)
        if judge and eval_result.response_message:
            t0 = time.monotonic()
            judge_score = judge.score(eval_result.response_message, case)
            judge_ms = (time.monotonic() - t0) * 1000

            eval_result.judge = judge_score
            eval_result.latency.judge_ms = round(judge_ms, 2)

            # Estimate cost: ~150 tokens/call × 3 runs × $0.00000035/token (flash)
            tokens = 150 * judge_score.runs
            eval_result.cost = CostMetrics(
                judge_tokens=tokens,
                judge_calls=judge_score.runs,
                cost_usd=round(tokens * 0.00000035, 6),
            )

        results.append(eval_result)
    return results


# ─── Results persistence & regression ─────────────────────────────────────────

def _get_git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(_SERVICE_ROOT),
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return "unknown"


def _load_previous_run(results_dir: Path) -> Optional[dict]:
    """Loads the most recent results JSON (by filename sort)."""
    files = sorted(results_dir.glob("*.json"), reverse=True)
    if not files:
        return None
    try:
        with open(files[0]) as f:
            return json.load(f)
    except Exception:
        return None


def build_summary(
    results: List[EvalResult],
    threshold: float,
    results_dir: Path,
) -> RunSummary:
    git_sha = _get_git_sha()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    below_threshold = sum(
        1 for r in results if r.heuristic.total < threshold
    )

    avg_heuristic = round(
        sum(r.heuristic.total for r in results) / total, 2
    ) if total else 0.0

    judge_scores = [r.judge.final_score for r in results if r.judge]
    avg_judge = round(sum(judge_scores) / len(judge_scores), 2) if judge_scores else None

    avg_latency = round(
        sum(r.latency.engine_ms + r.latency.judge_ms for r in results) / total, 2
    ) if total else 0.0

    total_cost = round(sum(r.cost.cost_usd for r in results), 6)

    # Regression delta vs previous run
    delta_score = None
    regressions: List[str] = []
    improvements: List[str] = []
    prev = _load_previous_run(results_dir)
    if prev:
        prev_avg = prev.get("avg_heuristic_score", 0)
        delta_score = round(avg_heuristic - prev_avg, 2)

        prev_scores = {r["case_id"]: r["heuristic_score"] for r in prev.get("results", [])}
        for r in results:
            prev_s = prev_scores.get(r.case_id)
            if prev_s is not None:
                diff = r.heuristic.total - prev_s
                if diff <= -1.0:
                    regressions.append(r.case_id)
                elif diff >= 1.0:
                    improvements.append(r.case_id)

    return RunSummary(
        total=total,
        passed=passed,
        failed=failed,
        below_threshold=below_threshold,
        avg_heuristic_score=avg_heuristic,
        avg_judge_score=avg_judge,
        avg_latency_ms=avg_latency,
        total_cost_usd=total_cost,
        git_sha=git_sha,
        timestamp=ts,
        threshold=threshold,
        delta_score=delta_score,
        regressions=regressions,
        improvements=improvements,
    )


def save_results(results: List[EvalResult], summary: RunSummary, results_dir: Path):
    results_dir.mkdir(parents=True, exist_ok=True)
    filename = results_dir / f"{summary.timestamp}_{summary.git_sha}.json"
    payload = {
        "timestamp": summary.timestamp,
        "git_sha": summary.git_sha,
        "avg_heuristic_score": summary.avg_heuristic_score,
        "avg_judge_score": summary.avg_judge_score,
        "avg_latency_ms": summary.avg_latency_ms,
        "total_cost_usd": summary.total_cost_usd,
        "results": [
            {
                "case_id": r.case_id,
                "alert_type": r.alert_type,
                "passed": r.passed,
                "heuristic_score": r.heuristic.total,
                "judge_score": r.judge.final_score if r.judge else None,
                "engine_ms": r.latency.engine_ms,
                "failures": r.failures,
            }
            for r in results
        ],
    }
    with open(filename, "w") as f:
        json.dump(payload, f, indent=2)
    logger.info(f"Results saved → {filename}")
    return filename
# Batch logging refinement
