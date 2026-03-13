"""
run_evals.py — CLI entry point for the MoneyLane eval suite.

Usage:
  python evals/run_evals.py
  python evals/run_evals.py --judge
  python evals/run_evals.py --judge --threshold 7.0
  python evals/run_evals.py --output evals/results/

Exit codes:
  0  All cases pass and average score >= threshold
  1  One or more failures, score below threshold, or regressions detected
"""
import argparse
import logging
import sys
from pathlib import Path

# ── sys.path setup (must come before local imports) ──────────────────────────
_EVALS_DIR = Path(__file__).resolve().parent
_SERVICE_ROOT = _EVALS_DIR.parent
sys.path.insert(0, str(_SERVICE_ROOT))
sys.path.insert(0, str(_EVALS_DIR.parent))  # so `evals.*` resolves

from evals.runner import load_test_cases, run_all, build_summary, save_results

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ─── ANSI colours ────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

_PASS = f"{GREEN}✓{RESET}"
_FAIL = f"{RED}✗{RESET}"


def _print_case(result):
    icon = _PASS if result.passed else _FAIL
    score = result.heuristic.total
    judge_str = f"  judge={result.judge.final_score:.1f}" if result.judge else ""
    latency_str = f"  {result.latency.engine_ms:.0f}ms"
    failures_str = ""
    if result.failures:
        failures_str = f"\n    {RED}↳ {'; '.join(result.failures)}{RESET}"
    print(
        f"  {icon} {result.case_id:<10} "
        f"[{result.alert_type:<22}]  "
        f"score={score:.1f}/10{judge_str}{latency_str}"
        f"{failures_str}"
    )


def _print_summary(summary, results_file):
    width = 52
    print(f"\n{BOLD}{'─' * width}{RESET}")
    print(f"{BOLD}  EVAL SUMMARY{RESET}")
    print(f"{'─' * width}")

    _row = lambda label, val: print(f"  {label:<28} {val}")

    avg_label = f"{summary.avg_heuristic_score:.2f} / 10"
    if summary.avg_judge_score is not None:
        avg_label += f"  (judge: {summary.avg_judge_score:.2f})"
    _row("Average Score:", avg_label)
    _row("Passed:", f"{summary.passed} / {summary.total}")
    _row("Failed:", f"{summary.failed} / {summary.total}")
    _row(f"Below {summary.threshold:.1f}:", f"{summary.below_threshold}")
    _row("Avg Latency:", f"{summary.avg_latency_ms:.0f} ms")

    if summary.total_cost_usd > 0:
        _row("Est. Cost (judge):", f"${summary.total_cost_usd:.5f} USD")

    if summary.delta_score is not None:
        sign = "+" if summary.delta_score >= 0 else ""
        colour = GREEN if summary.delta_score >= 0 else RED
        _row("Delta vs prev run:", f"{colour}{sign}{summary.delta_score:.2f}{RESET}")

    if summary.regressions:
        print(f"\n  {RED}Regressions (≥1pt drop):{RESET}")
        for c in summary.regressions:
            print(f"    • {c}")

    if summary.improvements:
        print(f"\n  {GREEN}Improvements (≥1pt gain):{RESET}")
        for c in summary.improvements:
            print(f"    • {c}")

    print(f"{'─' * width}")
    print(f"  Git SHA: {summary.git_sha}")
    print(f"  Results: {results_file}")
    print(f"{'─' * width}")

    pass_threshold = summary.avg_heuristic_score >= summary.threshold
    no_regressions = len(summary.regressions) == 0
    overall = pass_threshold and no_regressions and summary.failed == 0

    if overall:
        print(f"\n  {GREEN}{BOLD}✓ PASS{RESET}\n")
    else:
        print(f"\n  {RED}{BOLD}✗ FAIL{RESET}")
        if not pass_threshold:
            print(f"    Avg score {summary.avg_heuristic_score:.2f} < threshold {summary.threshold}")
        if summary.regressions:
            print(f"    Regressions detected: {summary.regressions}")
        print()

    return 0 if overall else 1


def main():
    parser = argparse.ArgumentParser(
        description="MoneyLane intervention engine eval suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--judge", action="store_true",
        help="Enable LLM-as-Judge via Gemini (requires GEMINI_API_KEY)",
    )
    parser.add_argument(
        "--threshold", type=float, default=6.0,
        help="Minimum average score to pass (default: 6.0)",
    )
    parser.add_argument(
        "--output", type=str, default="evals/results",
        help="Directory for result JSON files",
    )
    parser.add_argument(
        "--cases", type=str,
        default=str(_EVALS_DIR / "intervention_test_cases.json"),
        help="Path to test cases JSON",
    )
    args = parser.parse_args()

    results_dir = Path(args.output)
    cases_path = Path(args.cases)

    # Load test cases
    cases = load_test_cases(cases_path)
    print(f"\n{BOLD}MoneyLane Intervention Eval Suite{RESET}")
    print(f"Running {len(cases)} cases  |  threshold={args.threshold}  |  judge={'on' if args.judge else 'off'}\n")

    # Optionally load judge
    judge = None
    if args.judge:
        from evals.judge import get_judge
        judge = get_judge()
        print(f"  {CYAN}Judge: Gemini 2.0 Flash (3-run averaging, temp=0.1){RESET}\n")

    # Run
    results = run_all(cases, threshold=args.threshold, judge=judge)

    # Print per-case results
    for r in results:
        _print_case(r)

    # Build + save summary
    summary = build_summary(results, args.threshold, results_dir)
    results_file = save_results(results, summary, results_dir)

    # Print summary + return exit code
    exit_code = _print_summary(summary, results_file)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
