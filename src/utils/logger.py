import logging
import json
import sys
import uuid
from datetime import datetime
from typing import Optional

try:
    from kafka import KafkaProducer
except ImportError:
    KafkaProducer = None


class JsonFormatter(logging.Formatter):
    def __init__(self, job_id, env, run_id, trace_id, span_id):
        super().__init__()
        self.job_id = job_id
        self.env = env
        self.run_id = run_id
        self.trace_id = trace_id
        self.span_id = span_id

    def format(self, record):
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "job_id": self.job_id,
            "env": self.env,
            "run_id": self.run_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "message": record.getMessage(),
        }

        if hasattr(record, "metrics"):
            payload["metrics"] = record.metrics

        if hasattr(record, "context"):
            payload["context"] = record.context

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload)


class KafkaLogHandler(logging.Handler):
    def __init__(self, brokers, topic):
        super().__init__()
        if not KafkaProducer:
            raise ImportError("kafka-python not installed")

        self.producer = KafkaProducer(
            bootstrap_servers=brokers.split(","),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        self.topic = topic

    def emit(self, record):
        try:
            msg = json.loads(self.format(record))
            self.producer.send(self.topic, msg)
        except Exception:
            self.handleError(record)


class MetricsAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        metrics = kwargs.pop("metrics", None)
        context = kwargs.pop("context", None)

        if metrics or context:
            extra = kwargs.setdefault("extra", {})
            if metrics:
                extra["metrics"] = metrics
            if context:
                extra["context"] = context

        return msg, kwargs


def get_logger(
    name: str,
    env: str = "dev",
    job_id: Optional[str] = None,
    level: str = "INFO",
    enable_kafka: bool = False,
    kafka_brokers: Optional[str] = None,
    kafka_topic: Optional[str] = None,
):
    logger = logging.getLogger(name)

    if logger.handlers:
        return MetricsAdapter(logger, {})

    run_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    span_id = str(uuid.uuid4())
    job_id = job_id or name

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = JsonFormatter(job_id, env, run_id, trace_id, span_id)

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if enable_kafka and kafka_brokers and kafka_topic:
        kh = KafkaLogHandler(kafka_brokers, kafka_topic)
        kh.setFormatter(formatter)
        logger.addHandler(kh)

    logger.propagate = False
    return MetricsAdapter(logger, {})
