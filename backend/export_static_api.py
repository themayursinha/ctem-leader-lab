import json
from pathlib import Path
from typing import Any

from main import (
    get_assets,
    get_attack_paths,
    get_business_services,
    get_exposures,
    get_maturity,
    get_prioritized_exposures,
    get_program_summary,
    get_remediation_actions,
    get_workshop_artifacts,
)


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "frontend" / "public" / "api"


def to_jsonable(value: Any):
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    return value


def write_json(name: str, value: Any):
    path = OUT_DIR / f"{name}.json"
    path.write_text(json.dumps(to_jsonable(value), indent=2) + "\n", encoding="utf-8")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json("program-summary", get_program_summary())
    write_json("maturity", get_maturity())
    write_json("business-services", get_business_services())
    write_json("assets", get_assets())
    write_json("exposures", get_exposures())
    write_json("prioritized-exposures", get_prioritized_exposures())
    write_json("attack-paths", get_attack_paths())
    write_json("remediation-actions", get_remediation_actions())
    write_json("workshop-artifacts", get_workshop_artifacts())


if __name__ == "__main__":
    main()
