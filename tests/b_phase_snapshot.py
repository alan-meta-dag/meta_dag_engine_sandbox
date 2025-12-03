import json
import time
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_DIR = BASE_DIR / "state"
SNAPSHOT_DIR = STATE_DIR / "snapshots_b_phase"

TARGET_FILES = [
    "meta_dag.state.json",
    "meta_dag_memory.json",
    "pra_log.json",
    "tul_log.json",
]


def safe_load_json(path: Path):
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"__error__": "failed_to_parse_json"}


def take_snapshot(tag: str) -> Path:
    """將 state 目錄中的關鍵檔案打包成單一 snapshot JSON。"""
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.time()
    snapshot = {
        "tag": tag,
        "timestamp": ts,
        "files": {}
    }
    for name in TARGET_FILES:
        p = STATE_DIR / name
        snapshot["files"][name] = safe_load_json(p)

    out_path = SNAPSHOT_DIR / f"snapshot_{int(ts)}_{tag}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    return out_path


if __name__ == "__main__":
    p = take_snapshot("manual")
    print(f"Snapshot written: {p}")
