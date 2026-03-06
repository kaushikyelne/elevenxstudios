# Eval Layer — MoneyLane Financial Intervention Engine

A production-grade evaluation framework for the intervention engine. Answers:
> *"Is the engine producing correct, actionable, cost-efficient, and behaviorally impactful guidance — consistently over time?"*

---

## Quick Start

```bash
cd services/financial-service

# Heuristic-only (fast, no API key needed)
python evals/run_evals.py

# With LLM-as-Judge (Gemini 2.0 Flash)
GEMINI_API_KEY=your_key python evals/run_evals.py --judge

# Strict CI gate
python evals/run_evals.py --threshold 7.0
```

---

## Directory Structure

```
evals/
├── intervention_test_cases.json  # 25 test cases
├── models.py                     # Typed dataclasses (no app.* dependency)
├── scorer.py                     # Heuristic scoring (0–10)
├── runner.py                     # In-memory SQLite executor + regression delta
├── run_evals.py                  # CLI entry point
├── judge/
│   ├── __init__.py               # get_judge() factory
│   ├── base.py                   # BaseJudge ABC
│   ├── gemini_judge.py           # Default: Gemini 2.0 Flash
│   └── openai_judge.py           # Future stub
└── results/
    └── .gitkeep                  # JSON results are gitignored
```

---

## Test Case Coverage

| Type | Count | What it covers |
|---|---|---|
| `soft_block` | 4 | category freeze trigger, all 4 real categories |
| `daily_limit_breach` | 5 | mild → severe overage, small/large budgets |
| `overspend_warning` | 8 | pace bands, severity tiers, edge days |
| No-intervention | 3 | LOW severity, no budget, within limits |
| **Adversarial** | **5** | day-1 overspend, ₹5L tx, cooldown spam, zero budget, EOM edge |

---

## Scoring System

### Heuristic (0–10, always runs)

| Dimension | Max | Logic |
|---|---|---|
| Correctness | 4 | `₹` symbol (+2), `triggered` matches expected (+2) |
| Actionability | 3 | Action verbs in `suggested_actions` labels |
| Tone | 3 | Loss-framing words in message (`waste`, `blown`, `over`, ...) |

Hard constraints (any failure = case fails regardless of score):
- `severity` must be in the expected list
- `must_contain` tokens must all be present
- `must_not_contain` tokens must all be absent

### LLM-as-Judge (`--judge` flag)

Uses **Gemini 2.0 Flash** — same model as the agent-service, reuses `GEMINI_API_KEY`.

| Dimension | Max |
|---|---|
| Correctness | 4 |
| Actionability | 3 |
| Behavioral Impact | 3 |

Design:
- `temperature=0.1` for deterministic scoring
- 3 independent runs averaged per case (reduces variance)
- JSON parse guard + markdown fence stripping
- Retry on malformed response (max 2 attempts per run)
- Reason quality check (`< 20 chars` triggers a retry)
- Gracefully skipped if no `GEMINI_API_KEY`

---

## Adding Test Cases

1. Open `evals/intervention_test_cases.json`
2. Add a new object following the existing schema
3. Set `"adversarial": true` in `metadata` for edge case tracking
4. Run `python evals/run_evals.py` to verify

---

## Results Storage

Each run writes to `evals/results/<timestamp>_<git-sha>.json`:

```json
{
  "timestamp": "2026-04-12T14-00-00",
  "git_sha": "abc1234",
  "avg_heuristic_score": 8.1,
  "avg_judge_score": 7.9,
  "avg_latency_ms": 45,
  "total_cost_usd": 0.000315,
  "results": [...]
}
```

The runner auto-detects the previous JSON and computes a delta score. Named after git SHA for full traceability.

---

## CI Integration

Add to your GitHub Actions CI workflow (`.github/workflows/`):

```yaml
- name: Run eval suite
  run: |
    cd services/financial-service
    pip install -r requirements.txt
    python evals/run_evals.py --threshold 7.0
  # exit code 1 = score dropped or regression detected → CI fails
```

### Regression Gate

After any change to `intervention.py`, `predictor.py`, or `_build_loss_framed_message`:

```bash
python evals/run_evals.py --threshold 7.0
# exit 1 → reject the change
```

---

## Cost Reference (Judge Mode)

| Model | Cost/call | Runs/case | Cost/case |
|---|---|---|---|
| Gemini 2.0 Flash | ~$0.0001 | 3 | ~$0.0003 |

**25 cases with judge ≈ $0.007 per full run** — negligible for CI.

---

## Prompt Versioning

Each test case has a `metadata.prompt_version` field. When you update the system prompt, bump the version string and re-run evals. The result JSON captures the SHA + timestamp so you can compare across versions in git history.
