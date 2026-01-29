from typing import Dict
import time


class K8sCostCollector:
    """
    Kubernetes pod-level cost attribution.

    Uses resource usage (CPU/memory) and pricing heuristics
    to estimate cost per job / namespace.
    """

    def __init__(
        self,
        cpu_cost_per_core_hour: float = 0.031611,
        memory_cost_per_gb_hour: float = 0.004237,
    ):
        self.cpu_cost_per_core_hour = cpu_cost_per_core_hour
        self.memory_cost_per_gb_hour = memory_cost_per_gb_hour

    def estimate_job_cost(
        self,
        job_label: str,
        namespace: str,
        cpu_core_hours: float,
        memory_gb_hours: float,
    ) -> Dict:
        cpu_cost = cpu_core_hours * self.cpu_cost_per_core_hour
        memory_cost = memory_gb_hours * self.memory_cost_per_gb_hour

        return {
            "platform": "kubernetes",
            "job_id": job_label,
            "namespace": namespace,
            "cpu_core_hours": round(cpu_core_hours, 4),
            "memory_gb_hours": round(memory_gb_hours, 4),
            "estimated_cost_usd": round(cpu_cost + memory_cost, 4),
            "timestamp": int(time.time()),
        }
