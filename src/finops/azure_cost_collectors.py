from typing import Dict
import time


class AzureSynapseCostCollector:
    """
    Azure Synapse SQL & Spark cost estimation.
    """

    def __init__(
        self,
        cost_per_dwu_hour: float = 1.20,
        cost_per_vcore_hour: float = 0.32,
    ):
        self.cost_per_dwu_hour = cost_per_dwu_hour
        self.cost_per_vcore_hour = cost_per_vcore_hour

    def estimate_sql_pool_cost(
        self,
        query_id: str,
        dwu_hours: float,
    ) -> Dict:
        cost = dwu_hours * self.cost_per_dwu_hour

        return {
            "platform": "azure_synapse_sql",
            "query_id": query_id,
            "dwu_hours": round(dwu_hours, 4),
            "estimated_cost_usd": round(cost, 4),
            "timestamp": int(time.time()),
        }

    def estimate_spark_cost(
        self,
        job_id: str,
        vcore_hours: float,
    ) -> Dict:
        cost = vcore_hours * self.cost_per_vcore_hour

        return {
            "platform": "azure_synapse_spark",
            "job_id": job_id,
            "vcore_hours": round(vcore_hours, 4),
            "estimated_cost_usd": round(cost, 4),
            "timestamp": int(time.time()),
        }


class FabricCostCollector:
    """
    Microsoft Fabric cost estimation.
    """

    def __init__(self, cost_per_cu_hour: float = 0.15):
        self.cost_per_cu_hour = cost_per_cu_hour

    def estimate_job_cost(
        self,
        job_id: str,
        cu_hours: float,
    ) -> Dict:
        cost = cu_hours * self.cost_per_cu_hour

        return {
            "platform": "microsoft_fabric",
            "job_id": job_id,
            "cu_hours": round(cu_hours, 4),
            "estimated_cost_usd": round(cost, 4),
            "timestamp": int(time.time()),
        }
