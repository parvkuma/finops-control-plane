import json
import time
from typing import Dict, List, Optional

from finops.cost_aggregator import CostAggregator


class StreamingCostIngestor:
    """
    Kafka-style streaming cost ingestion (broker-agnostic).
    """

    def __init__(
        self,
        job_budget_usd: Optional[float],
        anomaly_threshold_pct: float,
        cost_center: Optional[str],
    ):
        self.aggregator = CostAggregator(
            job_budget_usd=job_budget_usd,
            anomaly_threshold_pct=anomaly_threshold_pct,
            cost_center=cost_center,
        )
        self.historical_costs: List[float] = []

    def ingest_event(self, cost_event: Dict) -> Dict:
        self.aggregator.add_cost(cost_event)

        total = self.aggregator.total_cost()
        self.historical_costs.append(total)
        if len(self.historical_costs) > 20:
            self.historical_costs.pop(0)

        return self.aggregator.executive_summary(self.historical_costs)
