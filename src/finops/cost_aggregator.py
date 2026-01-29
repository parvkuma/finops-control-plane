import statistics
from typing import Dict, List, Optional


class CostAggregator:
    def __init__(self, job_budget_usd: Optional[float], anomaly_threshold_pct: float, cost_center: Optional[str]):
        self.job_budget_usd = job_budget_usd
        self.anomaly_threshold_pct = anomaly_threshold_pct
        self.cost_center = cost_center
        self.costs: List[Dict] = []

    def add_cost(self, cost_record: Dict):
        self.costs.append(cost_record)

    def total_cost(self) -> float:
        return round(sum(c.get("estimated_cost_usd", 0.0) for c in self.costs), 4)

    def cost_by_platform(self) -> Dict[str, float]:
        result: Dict[str, float] = {}
        for c in self.costs:
            p = c.get("platform", "unknown")
            result[p] = result.get(p, 0.0) + float(c.get("estimated_cost_usd", 0.0))
        return {k: round(v, 4) for k, v in result.items()}

    def is_budget_breached(self) -> bool:
        return self.job_budget_usd and self.total_cost() > self.job_budget_usd

    def detect_anomaly(self, historical_costs: Optional[List[float]]) -> bool:
        if not historical_costs or len(historical_costs) < 3:
            return False
        avg = statistics.mean(historical_costs)
        if avg <= 0:
            return False
        pct = ((self.total_cost() - avg) / avg) * 100
        return pct > self.anomaly_threshold_pct

    def executive_summary(self, historical_costs: Optional[List[float]]) -> Dict:
        return {
            "total_cost_usd": self.total_cost(),
            "budget_breached": self.is_budget_breached(),
            "anomaly_detected": self.detect_anomaly(historical_costs),
            "cost_by_platform": self.cost_by_platform(),
            "cost_center": self.cost_center,
        }
