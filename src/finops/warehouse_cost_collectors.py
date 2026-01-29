# warehouse_cost_collectors.py (BigQuery + Redshift)

from typing import Dict
import time


class BigQueryCostCollector:
    """
    BigQuery cost estimation based on data scanned.
    """

    def __init__(self, cost_per_tb: float = 5.0):
        self.cost_per_tb = cost_per_tb

    def estimate_query_cost(
        self,
        job_id: str,
        data_scanned_tb: float,
    ) -> Dict:
        cost = data_scanned_tb * self.cost_per_tb

        return {
            "platform": "bigquery",
            "job_id": job_id,
            "data_scanned_tb": round(data_scanned_tb, 4),
            "estimated_cost_usd": round(cost, 4),
            "timestamp": int(time.time()),
        }


class RedshiftCostCollector:
    """
    Redshift cost estimation based on node hours.
    """

    def __init__(self, cost_per_node_hour: float = 1.086):
        self.cost_per_node_hour = cost_per_node_hour

    def estimate_query_cost(
        self,
        query_id: str,
        node_hours: float,
    ) -> Dict:
        cost = node_hours * self.cost_per_node_hour

        return {
            "platform": "redshift",
            "query_id": query_id,
            "node_hours": round(node_hours, 4),
            "estimated_cost_usd": round(cost, 4),
            "timestamp": int(time.time()),
        }
