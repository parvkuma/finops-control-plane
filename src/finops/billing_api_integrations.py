from typing import Dict
import random


class AWSCostExplorerClient:
    """
    AWS Cost Explorer integration (simulated).
    """

    def get_daily_cost(
        self,
        start_date: str,
        end_date: str,
        tag_key: str,
        tag_value: str,
    ) -> Dict[str, float]:
        return {
            start_date: round(random.uniform(10, 40), 2),
            end_date: round(random.uniform(10, 40), 2),
        }


class GCPBillingClient:
    """
    GCP Billing API integration (simulated).
    """

    def get_cost_by_label(
        self,
        project_id: str,
        label_key: str,
        label_value: str,
    ) -> float:
        return round(random.uniform(15, 50), 2)


class AzureCostManagementClient:
    """
    Azure Cost Management API integration (simulated).
    """

    def get_cost_by_resource_group(
        self,
        subscription_id: str,
        resource_group: str,
    ) -> float:
        return round(random.uniform(20, 60), 2)
