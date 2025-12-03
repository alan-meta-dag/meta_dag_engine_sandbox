import json
import time
from pathlib import Path
from typing import Any, Dict

# ===========================================
# C-A Phase Runner (Audit-Only, Non-Destructive)
# Meta-DAG Engine Governance v1.2
# ===========================================

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_DIR = BASE_DIR / "state"
REPORT_DIR = STATE_DIR  # 報告直接寫在 state 下面

SNAPSHOT_DIR = STATE_DIR / "snapshots"
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def summarize_meta_dag_memory(data: Any) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "exists": data is not None,
        "raw_type": type(data).__name__,
        "node_count": 0,
        "by_type": {},
    }
    if isinstance(data, dict):
        # 常見格式: {"nodes": [...]}
        nodes = data.get("nodes") or data.get("memory") or []
    elif isinstance(data, list):
        nodes = data
    else:
        nodes = []

    summary["node_count"] = len(nodes)

    for n in nodes:
        if isinstance(n, dict):
            t = n.get("type") or n.get("node_type") or "UNKNOWN"
            summary["by_type"][t] = summary["by_type"].get(t, 0) + 1

    return summary

def summarize_tul_log(data: Any) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "exists": data is not None,
        "raw_type": type(data).__name__,
        "entry_count": 0,
    }
    if isinstance(data, list):
        summary["entry_count"] = len(data)
    elif isinstance(data, dict):
        # 如果是 dict，粗略看 key 數量
        summary["entry_count"] = len(data)
    return summary

def summarize_pra_log(data: Any) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "exists": data is not None,
        "raw_type": type(data).__name__,
        "entry_count": 0,
        "by_policy": {},
    }
    if isinstance(data, list):
        summary["entry_count"] = len(data)
        for e in data:
            if isinstance(e, dict):
                p = e.get("Policy") or e.get("policy") or "UNKNOWN"
                summary["by_policy"][p] = summary["by_policy"].get(p, 0) + 1
    elif isinstance(data, dict):
        summary["entry_count"] = len(data)
    return summary

def main() -> None:
    ts = int(time.time())
    ts_str = time.strftime("%Y%m%d_%H%M%S", time.localtime(ts))

    print("[C-A] Meta-DAG Audit Phase starting...")
    print(f"[C-A] BASE_DIR : {BASE_DIR}")
    print(f"[C-A] STATE_DIR: {STATE_DIR}")

    meta_path = STATE_DIR / "meta_dag_memory.json"
    tul_path = STATE_DIR / "tul_log.json"
    pra_path = STATE_DIR / "pra_log.json"

    meta_data = load_json(meta_path, None)
    tul_data = load_json(tul_path, None)
    pra_data = load_json(pra_path, None)

    meta_summary = summarize_meta_dag_memory(meta_data)
    tul_summary = summarize_tul_log(tul_data)
    pra_summary = summarize_pra_log(pra_data)

    overall = {
        "timestamp": ts,
        "timestamp_str": ts_str,
        "meta_dag_memory": meta_summary,
        "tul_log": tul_summary,
        "pra_log": pra_summary,
    }

    # === 寫 JSON 報告 ===
    json_report = REPORT_DIR / f"c_a_audit_report_{ts_str}.json"
    with json_report.open("w", encoding="utf-8") as f:
        json.dump(overall, f, indent=2, ensure_ascii=False)

    # === 寫 Markdown 報告 ===
    md_report = REPORT_DIR / f"c_a_audit_report_{ts_str}.md"
    with md_report.open("w", encoding="utf-8") as f:
        f.write("# C-A Audit Report (Meta-DAG Engine)\n\n")
        f.write(f"- Timestamp: {ts_str}\n")
        f.write(f"- Base Dir : {BASE_DIR}\n")
        f.write(f"- State Dir: {STATE_DIR}\n\n")

        f.write("## Meta-DAG Memory Summary\n\n")
        f.write(f"- Exists     : {meta_summary['exists']}\n")
        f.write(f"- Raw Type   : {meta_summary['raw_type']}\n")
        f.write(f"- Node Count : {meta_summary['node_count']}\n")
        if meta_summary["by_type"]:
            f.write("- By Type:\n")
            for t, cnt in meta_summary["by_type"].items():
                f.write(f"  - {t}: {cnt}\n")
        f.write("\n")

        f.write("## TUL Log Summary\n\n")
        f.write(f"- Exists      : {tul_summary['exists']}\n")
        f.write(f"- Raw Type    : {tul_summary['raw_type']}\n")
        f.write(f"- Entry Count : {tul_summary['entry_count']}\n\n")

        f.write("## PRA Log Summary\n\n")
        f.write(f"- Exists      : {pra_summary['exists']}\n")
        f.write(f"- Raw Type    : {pra_summary['raw_type']}\n")
        f.write(f"- Entry Count : {pra_summary['entry_count']}\n")
        if pra_summary["by_policy"]:
            f.write("- By Policy:\n")
            for p, cnt in pra_summary["by_policy"].items():
                f.write(f"  - {p}: {cnt}\n")
        f.write("\n")

        f.write("## Notes\n\n")
        f.write("- 本階段僅進行 **只讀稽核 (Audit-Only)**，不修改任何 state/*.json。\n")
        f.write("- 後續如需正式進入記憶壓縮 / 清理，建議新增 c_a_collapse.py，\n")
        f.write("  採用 whitelist 策略明確標記要保留的節點類型，再進行壓縮寫回。\n")

    print("[C-A] Audit finished.")
    print(f"[C-A] JSON report: {json_report}")
    print(f"[C-A] MD   report: {md_report}")

if __name__ == '__main__':
    main()
