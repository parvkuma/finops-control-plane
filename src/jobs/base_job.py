import time
from abc import ABC, abstractmethod
from typing import Optional, List

from config_loader import ConfigLoader
from utils.logger import get_logger


class BaseJob(ABC):
    def __init__(
        self,
        config_path: str,
        job_name: str,
        experiment_id: Optional[str] = None,
        user_id: Optional[str] = None,
        remote_backend: Optional[str] = None,
        remote_table: Optional[str] = None,
        remote_key: Optional[str] = None,
    ):
        self.config = ConfigLoader(
            config_path=config_path,
            experiment_id=experiment_id,
            user_id=user_id,
            remote_backend=remote_backend,
            remote_table=remote_table,
            remote_key=remote_key,
        )

        self.logger = get_logger(
            name=job_name,
            env=self.config.get_env(),
            job_id=self.config.get_job_id(),
        )

        self.start_time = None
        self.rows_processed = 0
        self.gb_processed = 0.0
        self.tables: List[str] = []

    def execute(self):
        self.start_time = time.time()
        try:
            self.logger.info("Job started")
            self.pre_run()
            self.run()
            self.post_run()
            self._finalize(True)
        except Exception:
            self.logger.exception("Job failed")
            self._finalize(False)
            raise

    @abstractmethod
    def run(self):
        pass

    def pre_run(self):
        if self.config.is_feature_enabled("enable_exec_reports"):
            self.logger.info("Exec reporting enabled")

        exp = self.config.get_active_experiment()
        if exp:
            self.logger.info(f"Active experiment: {exp}")

    def post_run(self):
        pass

    def set_metrics(self, rows_processed: int, gb_processed: float, tables: Optional[List[str]] = None):
        self.rows_processed = rows_processed
        self.gb_processed = gb_processed
        self.tables = tables or []

    def _finalize(self, success: bool):
        runtime = round(time.time() - self.start_time, 2)
        self.logger.info(
            f"Job completed success={success} runtime_sec={runtime}",
            metrics={
                "rows": self.rows_processed,
                "gb": self.gb_processed,
            },
        )
