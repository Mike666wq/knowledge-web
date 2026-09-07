from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from metrics import summarize


ROOT = Path(__file__).resolve().parent


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def main() -> None:
    expected = {item["id"]: item for item in read_jsonl(ROOT / "dataset.jsonl")}
    actual = {item["id"]: item for item in read_jsonl(ROOT / "sample_runs.jsonl")}
    missing = sorted(set(expected) - set(actual))
    if missing:
        raise SystemExit(f"missing run records: {missing}")
    summary = summarize([(case, actual[case_id]) for case_id, case in expected.items()])
    print(json.dumps(asdict(summary), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
