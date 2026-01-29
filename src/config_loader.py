import os
import yaml
import random
import json
from typing import Dict, Any, Optional

try:
    import boto3
except ImportError:
    boto3 = None

try:
    from google.cloud import secretmanager, firestore
except ImportError:
    secretmanager = None
    firestore = None

try:
    import hvac
except ImportError:
    hvac = None

try:
    import consul
except ImportError:
    consul = None


class ConfigLoader:
    def __init__(
        self,
        config_path: str,
        experiment_id: Optional[str] = None,
        user_id: Optional[str] = None,
        remote_backend: Optional[str] = None,
        remote_table: Optional[str] = None,
        remote_key: Optional[str] = None,
    ):
        with open(config_path) as f:
            self._config = yaml.safe_load(f) or {}

        self.experiment_id = experiment_id
        self.user_id = user_id or str(random.randint(1, 100_000))

        if remote_backend and remote_key:
            remote_cfg = self._fetch_remote_config(remote_backend, remote_table, remote_key)
            if remote_cfg:
                self._deep_merge(self._config, remote_cfg)

        self._apply_env_overrides()
        self._resolve_secrets()
        self._apply_feature_flags()
        self._apply_ab_configs()

    def _deep_merge(self, base: Dict, override: Dict):
        for k, v in override.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._deep_merge(base[k], v)
            else:
                base[k] = v

    def _apply_env_overrides(self):
        env = self._config.get("env")
        overrides = self._config.get("environments", {}).get(env, {})
        self._deep_merge(self._config, overrides)

    def _fetch_remote_config(self, backend, table, key):
        if backend == "dynamodb":
            if not boto3:
                return None
            client = boto3.client("dynamodb")
            resp = client.get_item(TableName=table, Key={"config_key": {"S": key}})
            item = resp.get("Item")
            if not item:
                return None
            return json.loads(item["config_payload"]["S"])

        if backend == "firestore":
            if not firestore:
                return None
            project = os.getenv("GCP_PROJECT_ID")
            db = firestore.Client(project=project)
            doc = db.collection("platform_configs").document(key).get()
            return doc.to_dict() if doc.exists else None

        if backend == "consul":
            if not consul:
                return None
            c = consul.Consul()
            _, data = c.kv.get(key)
            return json.loads(data["Value"].decode()) if data else None

        return None

    def _resolve_secrets(self):
        for section, values in self._config.items():
            if isinstance(values, dict):
                for k, v in values.items():
                    if isinstance(v, str) and v.startswith("secret://"):
                        values[k] = self._fetch_secret(v)

    def _fetch_secret(self, uri: str) -> Optional[str]:
        backend, path = uri.replace("secret://", "").split("/", 1)

        if backend == "aws" and boto3:
            client = boto3.client("secretsmanager")
            return client.get_secret_value(SecretId=path).get("SecretString")

        if backend == "gcp" and secretmanager:
            project = os.getenv("GCP_PROJECT_ID")
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{project}/secrets/{path}/versions/latest"
            resp = client.access_secret_version(request={"name": name})
            return resp.payload.data.decode("UTF-8")

        if backend == "vault" and hvac:
            path, key = path.split("#", 1)
            client = hvac.Client(url=os.getenv("VAULT_ADDR"), token=os.getenv("VAULT_TOKEN"))
            secret = client.secrets.kv.v2.read_secret_version(path=path)
            return secret["data"]["data"].get(key)

        return None

    def _apply_feature_flags(self):
        flags = self._config.get("feature_flags", {})
        for name, cfg in flags.items():
            if not cfg.get("enabled", False):
                self._config[name] = False
                continue
            pct = cfg.get("rollout_pct", 100)
            bucket = int(self.user_id) % 100
            self._config[name] = bucket < pct

    def _apply_ab_configs(self):
        exps = self._config.get("experiments", {})
        if not self.experiment_id or self.experiment_id not in exps:
            return

        variants = exps[self.experiment_id].get("variants", {})
        keys = sorted(variants.keys())
        idx = int(self.user_id) % len(keys)
        selected = keys[idx]
        self._deep_merge(self._config, variants[selected])
        self._config["_active_experiment"] = {
            "experiment_id": self.experiment_id,
            "variant": selected,
        }

    def get_env(self): return self._config.get("env", "dev")
    def get_job_id(self): return self._config.get("job", {}).get("id")
    def get_job_budget_usd(self): return self._config.get("finops", {}).get("job_budget_usd")
    def get_anomaly_threshold_pct(self): return self._config.get("finops", {}).get("anomaly_threshold_pct", 200)
    def get_cloud_provider(self): return self._config.get("finops", {}).get("cloud", "aws")
    def get_cost_center(self): return self._config.get("job", {}).get("cost_center")
    def get_active_experiment(self): return self._config.get("_active_experiment")
    def is_feature_enabled(self, name): return bool(self._config.get(name))
