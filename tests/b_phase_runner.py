import json
import time
from pathlib import Path
from typing import List

import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

BASE_DIR = Path(__file__).resolve().parent.parent
TESTS_DIR = BASE_DIR / "tests"

# 確保 package 匯入可用
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tests.b_phase_attack_test import load_attack_cases, run_attack_batch
from tests.b_phase_snapshot import take_snapshot
from tests.b_phase_diff import diff_snapshots
from tests.b_phase_metrics import compute_metrics


def main():
    REPORT_DIR = TESTS_DIR / "attack_reports"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # 1) 載入語料
    cases = load_attack_cases(2000)

    # 2) 建立 snapshot list，並定義 hook
    snapshot_paths: List[Path] = []

    def hook(tag: str):
        p = take_snapshot(tag)
        snapshot_paths.append(p)
        print(f"[SNAPSHOT] {tag} -> {p.name}")

    # 起始 snapshot
    start_snap = take_snapshot("start")
    snapshot_paths.append(start_snap)

    # 3) 執行攻擊測試
    print("\n[INFO] B-Phase attack test starting...")
    summary = run_attack_batch(cases, snapshot_hook=hook, snapshot_interval=100)
    print("[INFO] B-Phase attack test finished.")

    # 結束 snapshot
    end_snap = take_snapshot("end")
    snapshot_paths.append(end_snap)

    # 4) 連續 snapshot diff
    diff_reports: List[Path] = []
    for a, b in zip(snapshot_paths, snapshot_paths[1:]):
        rp = diff_snapshots(a, b)
        diff_reports.append(rp)
        print(f"[DIFF] {a.name} vs {b.name} -> {rp.name}")

    # 5) 指標計算
    metrics = compute_metrics(snapshot_paths)

    # 6) 寫出總報告
    final_report = {
        "summary": summary,
        "snapshots": [str(p) for p in snapshot_paths],
        "diff_reports": [str(p) for p in diff_reports],
        "metrics": metrics,
        "generated_at": time.time(),
    }

    out_json = REPORT_DIR / "b_phase_full_report.json"
    out_md = REPORT_DIR / "b_phase_full_report.md"

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)

    # 簡單 Markdown 版
    lines = []
    lines.append("# B-Phase Governance-Aware Attack Test Report\n")
    lines.append("## Summary")
    lines.append(f"- Total cases: {summary['total_cases']}")
    lines.append(f"- Elapsed: {summary['elapsed_sec']:.2f} sec")
    lines.append(f"- Avg per case: {summary['avg_per_case_ms']:.2f} ms")
    lines.append("")
    lines.append("## Snapshots")
    for p in snapshot_paths:
        lines.append(f"- {p}")
    lines.append("")
    lines.append("## Diff Reports")
    for p in diff_reports:
        lines.append(f"- {p}")
    lines.append("")
    lines.append("## Metrics")
    lines.append("```json")
    lines.append(json.dumps(metrics, indent=2, ensure_ascii=False))
    lines.append("```")

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n[OK] B-Phase report written:")
    print(f" - JSON: {out_json}")
    print(f" - MD  : {out_md}")


if __name__ == "__main__":
    main()
