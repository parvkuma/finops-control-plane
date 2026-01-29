from typing import Dict
import time


class SnowflakeCostCollector:
    """
    Snowflake query cost estimation using credits.
    """

    def __init__(self, cost_per_credit: float = 3.0):
        self.cost_per_credit = cost_per_credit

    def estimate_query_cost(
        self,
        query_id: str,
        credits_used: float,
    ) -> Dict:
        cost = credits_used * self.cost_per_credit

        return {
            "platform": "snowflake",
            "query_id": query_id,
            "credits_used": round(credits_used, 4),
            "estimated_cost_usd": round(cost, 4),
            "timestamp": int(time.time()),
        }


class DatabricksCostCollector:
    """
    Databricks job cost estimation using DBU consumption.
    """

    def __init__(self, cost_per_dbu_hour: float = 0.55):
        self.cost_per_dbu_hour = cost_per_dbu_hour

    def estimate_job_cost(
        self,
        run_id: str,
        dbu_hours: float,
    ) -> Dict:
        cost = dbu_hours * self.cost_per_dbu_hour

        return {
            "platform": "databricks",
            "run_id": run_id,
            "dbu_hours": round(dbu_hours, 4),
            "estimated_cost_usd": round(cost, 4),
            "timestamp": int(time.time()),
        }
