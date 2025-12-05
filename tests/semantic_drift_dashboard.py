# tests/semantic_drift_dashboard.py
# ======================================================
# C-3A Semantic Drift Dashboard (CLI)
# - 讀取 state/drift_log.json
# - 輸出簡單統計 + 異常樣本
# ======================================================

import json
from pathlib import Path
from typing import Any, Dict, List
import time


BASE_DIR = Path(__file__).resolve().parents[1]
STATE_DIR = BASE_DIR / "state"
DRIFT_LOG_FILE = STATE_DIR / "drift_log.json"


def _load_drift_log() -> List[Dict[str, Any]]:
    if not DRIFT_LOG_FILE.exists():
        return []
    try:
        with open(DRIFT_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _bucket(score: float) -> str:
    if score < 0.2:
        return "0.0–0.2"
    if score < 0.4:
        return "0.2–0.4"
    if score < 0.6:
        return "0.4–0.6"
    if score < 0.8:
        return "0.6–0.8"
    return "0.8–1.0"


def main():
    entries = _load_drift_log()
    if not entries:
        print("[C-3A Dashboard] drift_log.json 為空，尚未有任何記錄。")
        print(f"檔案位置：{DRIFT_LOG_FILE}")
        return

    total = len(entries)
    print("=== C-3A Semantic Drift Dashboard (Passive Monitor) ===")
    print(f"Log file : {DRIFT_LOG_FILE}")
    print(f"Total    : {total} entries\n")

    # --- 分桶統計 ---
    buckets: Dict[str, int] = {}
    anomalies: List[Dict[str, Any]] = []

    for e in entries:
        score = float(e.get("Semantic_Drift_Score", 0.0))
        b = _bucket(score)
        buckets[b] = buckets.get(b, 0) + 1
        if e.get("Anomaly_Flag"):
            anomalies.append(e)

    print("[分布統計] Semantic Drift Score Buckets：")
    for label in ["0.0–0.2", "0.2–0.4", "0.4–0.6", "0.6–0.8", "0.8–1.0"]:
        count = buckets.get(label, 0)
        ratio = (count / total * 100.0) if total else 0.0
        print(f"  {label:7} : {count:4d} ({ratio:5.1f}%)")

    # --- 最近異常樣本 ---
    anomalies_sorted = sorted(
        anomalies, key=lambda x: x.get("timestamp", 0.0), reverse=True
    )

    print("\n[異常樣本] 最近最多 5 筆（Anomaly_Flag = True）：")
    if not anomalies_sorted:
        print("  （無標記為異常的事件）")
    else:
        for e in anomalies_sorted[:5]:
            ts = e.get("timestamp", 0.0)
            ts_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
            s = e.get("Semantic_Drift_Score")
            code = e.get("classification", {}).get("Code")
            nl = e.get("node_meta", {}).get("Original_NL", "")
            print("-" * 60)
            print(f"時間     : {ts_str}")
            print(f"分數     : {s}")
            print(f"類別 Code: {code}")
            print(f"節點 P/T : {e.get('tul_P')} / {e.get('tul_T')}")
            print(f"原始 NL  : {nl}")

    print("\n=== Dashboard 完成（純監測，未改變任何引擎狀態） ===")


if __name__ == "__main__":
    main()
