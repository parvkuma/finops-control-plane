from typing import Dict, List, Optional

from finops.cost_aggregator import CostAggregator
from finops.k8s_cost_collector import K8sCostCollector
from finops.cloud_cost_collectors import (
    SnowflakeCostCollector,
    DatabricksCostCollector,
)
from finops.warehouse_cost_collectors import (
    BigQueryCostCollector,
    RedshiftCostCollector,
)
from finops.azure_cost_collectors import (
    AzureSynapseCostCollector,
    FabricCostCollector,
)
from finops.billing_api_integrations import (
    AWSCostExplorerClient,
    GCPBillingClient,
    AzureCostManagementClient,
)


class FinOpsOrchestrator:
    """
    Master FinOps control plane.
    """

    def __init__(
        self,
        job_id: str,
        job_budget_usd: Optional[float],
        anomaly_threshold_pct: float,
        cost_center: Optional[str],
    ):
        self.job_id = job_id
        self.aggregator = CostAggregator(
            job_budget_usd=job_budget_usd,
            anomaly_threshold_pct=anomaly_threshold_pct,
            cost_center=cost_center,
        )

    def collect_batch_costs(
        self,
        aws_tag_key: Optional[str] = None,
        aws_tag_value: Optional[str] = None,
    ):
        if aws_tag_key and aws_tag_value:
            aws = AWSCostExplorerClient()
            aws_costs = aws.get_daily_cost(
                start_date="2026-01-01",
                end_date="2026-01-02",
                tag_key=aws_tag_key,
                tag_value=aws_tag_value,
            )
            for _, cost in aws_costs.items():
                self.aggregator.add_cost(
                    {
                        "platform": "aws",
                        "job_id": self.job_id,
                        "estimated_cost_usd": cost,
                    }
                )

    def get_executive_summary(
        self, historical_costs: Optional[List[float]] = None
    ) -> Dict:
        return self.aggregator.executive_summary(historical_costs)

    def is_budget_breached(self) -> bool:
        return self.aggregator.is_budget_breached()
