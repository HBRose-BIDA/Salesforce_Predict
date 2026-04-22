import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScoringConfig:
    username: str
    password: str
    security_token: str
    domain: str
    api_version: str
    predicted_win_field: str
    history_years: int
    min_closed_records: int


def _get(raw: dict, key: str, env_key: str, default: str | None = None) -> str:
    value = os.getenv(env_key)
    if value is not None and value != "":
        return value
    if key in raw and raw[key] is not None and raw[key] != "":
        return str(raw[key])
    if default is not None:
        return default
    raise KeyError(f"Missing required config value: {key} or {env_key}")


def load_config(config_path: Path | None = None) -> ScoringConfig:
    path = config_path or Path(__file__).resolve().parent.parent / "config.json"
    raw: dict = {}
    if path.exists():
        with path.open("r", encoding="utf-8") as file:
            raw = json.load(file)

    return ScoringConfig(
        username=_get(raw, "username", "SF_USERNAME"),
        password=_get(raw, "password", "SF_PASSWORD"),
        security_token=_get(raw, "security_token", "SF_SECURITY_TOKEN"),
        domain=_get(raw, "domain", "SF_DOMAIN", "login"),
        api_version=_get(raw, "api_version", "SF_API_VERSION", "60.0"),
        predicted_win_field=_get(
            raw,
            "predicted_win_field",
            "SF_PREDICTED_WIN_FIELD",
            "Predicted_Win_Probability__c",
        ),
        history_years=int(_get(raw, "history_years", "SF_HISTORY_YEARS", "3")),
        min_closed_records=int(_get(raw, "min_closed_records", "SF_MIN_CLOSED_RECORDS", "50")),
    )
