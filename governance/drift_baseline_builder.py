# governance/drift_baseline_builder.py
# C-3B Semantic Drift Baseline Builder (Passive / Offline Only)
#
# 目標：
# - 讀取 state/drift_log.json（由 C-3A / drift_monitor 寫入）
# - 建立「語義飄移基準」與「異常門檻建議」
# - 不修改任何引擎程式碼與治理流程（純監測用）

import json
import time
import math
from pathlib import Path
from typing import Any, Dict, List

# -----------------------------
# 路徑設定
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # sandbox root
STATE_DIR = BASE_DIR / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)

DRIFT_LOG_FILE = STATE_DIR / "drift_log.json"
BASELINE_JSON  = STATE_DIR / "drift_baseline.json"
BASELINE_MD    = STATE_DIR / "drift_baseline_metrics.md"


# -----------------------------
# 輔助函數
# -----------------------------
def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def compute_basic_stats(values: List[float]) -> Dict[str, float]:
    if not values:
        return {
            "min": 0.0,
            "max": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        }

    vmin = min(values)
    vmax = max(values)
    mean = sum(values) / len(values)
    if len(values) > 1:
        var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
        stdev = math.sqrt(var)
    else:
        stdev = 0.0

    return {
        "min": round(vmin, 4),
        "max": round(vmax, 4),
        "mean": round(mean, 4),
        "stdev": round(stdev, 4),
    }


def bucketize(values: List[float]) -> List[Dict[str, Any]]:
    """
    固定區間：0.0–0.2, 0.2–0.4, ..., 0.8–1.0
    """
    buckets = [
        (0.0, 0.2),
        (0.2, 0.4),
        (0.4, 0.6),
        (0.6, 0.8),
        (0.8, 1.0),
    ]
    total = len(values)
    result = []
    for low, high in buckets:
        cnt = sum(1 for v in values if (v >= low and (v < high or (high == 1.0 and v <= high))))
        ratio = (cnt / total) if total > 0 else 0.0
        result.append(
            {
                "range": [round(low, 1), round(high, 1)],
                "count": cnt,
                "ratio": round(ratio, 4),
            }
        )
    return result


def summarize_classification(entries: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    統計 classification.code / type 分布。
    """
    stats: Dict[str, Dict[str, Any]] = {}
    total = len(entries)

    for e in entries:
        cls = e.get("classification", {}) or {}
        code = cls.get("Code", "UNKNOWN")
        ctype = cls.get("Type", "Unknown Type")
        if code not in stats:
            stats[code] = {"count": 0, "type": ctype}
        stats[code]["count"] += 1

    # 加上比例
    for code, data in stats.items():
        cnt = data["count"]
        data["ratio"] = round(cnt / total, 4) if total > 0 else 0.0

    return stats


def suggest_thresholds(stats: Dict[str, float]) -> Dict[str, float]:
    """
    基於 baseline 分布給出建議門檻：
    - warning: max(mean + 2*stdev, 0.40)
    - critical: max(mean + 3*stdev, 0.60)
    即使目前樣本很少，也有保守的下限。
    """
    mean = stats.get("mean", 0.0)
    stdev = stats.get("stdev", 0.0)

    warning = max(mean + 2 * stdev, 0.40)
    critical = max(mean + 3 * stdev, 0.60)

    # 限制在 [0, 1]
    warning = min(max(warning, 0.0), 1.0)
    critical = min(max(critical, 0.0), 1.0)

    # 確保 critical >= warning
    if critical < warning:
        critical = warning

    return {
        "warning": round(warning, 4),
        "critical": round(critical, 4),
    }


# -----------------------------
# 主流程
# -----------------------------
def build_baseline() -> None:
    print("=== C-3B Semantic Drift Baseline Builder ===")
    print(f"[INFO] 讀取 drift log: {DRIFT_LOG_FILE}")

    entries: List[Dict[str, Any]] = load_json(DRIFT_LOG_FILE, [])

    if not entries:
        print("[WARN] drift_log.json 為空或不存在，無法建立 baseline。")
        print("       請先透過 C-3A (drift_monitor) 累積足夠事件後再執行本工具。")
        return

    # 收集 scores
    scores: List[float] = []
    for e in entries:
        try:
            s = float(e.get("Semantic_Drift_Score", 0.0))
            if 0.0 <= s <= 1.0:
                scores.append(s)
        except Exception:
            continue

    if not scores:
        print("[WARN] 無有效 Semantic_Drift_Score，無法建立統計。")
        return

    basic_stats = compute_basic_stats(scores)
    buckets = bucketize(scores)
    cls_stats = summarize_classification(entries)
    thresholds = suggest_thresholds(basic_stats)

    baseline = {
        "meta": {
            "created_at": time.time(),
            "created_at_iso": time.strftime(
                "%Y-%m-%dT%H:%M:%S", time.localtime()
            ),
            "source": "C-3B_drift_baseline_builder",
            "note": "Passive baseline only. No enforcement logic here.",
        },
        "sample_size": len(scores),
        "score_stats": basic_stats,
        "buckets": buckets,
        "classification_distribution": cls_stats,
        "suggested_thresholds": thresholds,
    }

    save_json(BASELINE_JSON, baseline)

    # 同步寫出人類可讀版 markdown 報告
    lines: List[str] = []
    lines.append("# C-3B Semantic Drift Baseline Metrics")
    lines.append("")
    lines.append(f"- 建立時間：{baseline['meta']['created_at_iso']}")
    lines.append(f"- 事件數量：{baseline['sample_size']}")
    lines.append("")
    lines.append("## Score 統計")
    lines.append("")
    lines.append(f"- min  : {basic_stats['min']}")
    lines.append(f"- max  : {basic_stats['max']}")
    lines.append(f"- mean : {basic_stats['mean']}")
    lines.append(f"- stdev: {basic_stats['stdev']}")
    lines.append("")
    lines.append("## 區間分布（Semantic_Drift_Score）")
    lines.append("")
    lines.append("| 區間 | Count | Ratio |")
    lines.append("|------|-------|-------|")
    for b in buckets:
        r = f"{b['range'][0]:.1f}–{b['range'][1]:.1f}"
        lines.append(
            f"| {r} | {b['count']} | {b['ratio']:.4f} |"
        )
    lines.append("")
    lines.append("## C-B 分類分布")
    lines.append("")
    lines.append("| Code | Type | Count | Ratio |")
    lines.append("|------|------|-------|-------|")
    for code, data in cls_stats.items():
        lines.append(
            f"| {code} | {data['type']} | {data['count']} | {data['ratio']:.4f} |"
        )
    lines.append("")
    lines.append("## 建議門檻（僅作為參考，不具強制力）")
    lines.append("")
    lines.append(f"- warning：{thresholds['warning']}")
    lines.append(f"- critical：{thresholds['critical']}")
    lines.append("")
    lines.append("> 說明：建議先在 dashboard 中以 **警示線** 顯示，")
    lines.append("> 觀察一段時間後再決定是否導入 C-3C enforcement。")

    BASELINE_MD.write_text("\n".join(lines), encoding="utf-8")

    print("")
    print("[OK] Baseline 建立完成：")
    print(f"  - JSON : {BASELINE_JSON}")
    print(f"  - MD   : {BASELINE_MD}")
    print("這是一個『離線參考基準』，尚未改變引擎治理邏輯。")


if __name__ == "__main__":
    build_baseline()
