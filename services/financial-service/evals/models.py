"""
Eval layer data models.
Standalone — no dependency on app.* modules.
"""
from dataclasses import dataclass, field
from typing import List, Optional


# ─── Input / Expected ─────────────────────────────────────────────────────────

@dataclass
class TestInput:
    category: str
    monthly_budget: Optional[float]
    spent_so_far: float
    days_elapsed: int
    daily_limit: Optional[float]
    is_blocked: bool
    transaction_amount: float
    prior_today_spend: float = 0.0   # existing spend today before this tx
    repeat_call: bool = False        # adversarial: second call triggers cooldown


@dataclass
class ExpectedOutput:
    triggered: bool
    severity: List[str]              # acceptable severity values (any match = pass)
    must_contain: List[str]
    must_not_contain: List[str]
    tone: str                        # "loss_framed" | "warning" | "none"
    has_action: bool


@dataclass
class TestCase:
    id: str
    description: str
    alert_type: str
    input: TestInput
    expected: ExpectedOutput
    metadata: dict = field(default_factory=dict)


# ─── Scoring ──────────────────────────────────────────────────────────────────

@dataclass
class ScoreBreakdown:
    correctness: float   # 0–4
    actionability: float # 0–3
    tone: float          # 0–3
    total: float         # 0–10


@dataclass
class LatencyMetrics:
    engine_ms: float     # time for check_and_intervene()
    judge_ms: float = 0.0


@dataclass
class CostMetrics:
    judge_tokens: int = 0
    judge_calls: int = 0
    cost_usd: float = 0.0


@dataclass
class JudgeScore:
    correctness: float
    actionability: float
    behavioral_impact: float
    final_score: float
    reason: str
    runs: int = 1        # number of judge calls averaged


@dataclass
class EvalResult:
    case_id: str
    description: str
    alert_type: str
    passed: bool
    heuristic: ScoreBreakdown
    judge: Optional[JudgeScore]
    latency: LatencyMetrics
    cost: CostMetrics
    failures: List[str]           # human-readable failure reasons
    response_message: Optional[str]
    response_triggered: Optional[bool]
    response_severity: Optional[str]


# ─── Run Summary ──────────────────────────────────────────────────────────────

@dataclass
class RunSummary:
    total: int
    passed: int
    failed: int
    below_threshold: int
    avg_heuristic_score: float
    avg_judge_score: Optional[float]
    avg_latency_ms: float
    total_cost_usd: float
    git_sha: str
    timestamp: str
    threshold: float
    delta_score: Optional[float] = None   # vs previous run
    regressions: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
