# ===============================================
#  quality_check.py
#  語料庫品質檢查工具（攻擊壓力測試前使用）
#  - 去重 / 過短句 / 相似度過高
#  - H / S 熵值檢查
#  - 產生 JSON + MD 報告
# ===============================================

import os
import time
import json
import math
from pathlib import Path
from typing import List, Dict, Any, Tuple

# -----------------------------------
BASE_DIR = Path(__file__).resolve().parent
CASE_DIR = BASE_DIR / "attack_cases"
REPORT_DIR = BASE_DIR / "attack_reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# 相似度門檻（0~1）
SIM_THRESHOLD = 0.75

# 最小字數
MIN_LEN = 4


# -----------------------------------
# 工具函数
# -----------------------------------

def load_file(path: Path) -> List[str]:
    if not path.exists():
        return []
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                out.append(s)
    return out


def jaccard(a: str, b: str) -> float:
    """
    字符集 Jaccard similarity
    高於 SIM_THRESHOLD 就視為相似句
    """
    sa = set(a)
    sb = set(b)
    if not sa or not sb:
        return 0
    return len(sa & sb) / len(sa | sb)


def entropy(s: str) -> float:
    """
    極簡字符熵估計
    """
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    total = len(s)
    h = 0.0
    for c, n in freq.items():
        p = n / total
        h -= p * math.log2(p)
    return h


# -----------------------------------
# 語料庫品質分析
# -----------------------------------

def analyze_corpus() -> Tuple[Dict, Dict]:
    """
    回傳:
      result: 每個語料庫的問題集合
      meta:   全域統計
    """
    result = {}
    meta = {
        "files": [],
        "total_sentences": 0,
        "duplicate_count": 0,
        "short_count": 0,
        "similar_pairs": 0,
        "high_entropy": [],
        "timestamp": time.time(),
    }

    files = list(CASE_DIR.glob("*.txt"))
    files.sort()

    all_sentences = []
    per_file = {}

    # -------------------
    # Load 每個語料庫
    # -------------------
    for f in files:
        lines = load_file(f)
        per_file[f.name] = lines

        meta["files"].append(f.name)
        meta["total_sentences"] += len(lines)

        # per file 檢查
        issues = {
            "short": [],
            "duplicates": [],
        }

        seen = set()
        for line in lines:
            # 過短句
            if len(line) < MIN_LEN:
                issues["short"].append(line)

            # 重複句
            if line in seen:
                issues["duplicates"].append(line)
            else:
                seen.add(line)

        result[f.name] = issues
        all_sentences.extend(lines)

    # -------------------
    # 全域去重檢查
    # -------------------
    unique = set(all_sentences)
    meta["duplicate_count"] = len(all_sentences) - len(unique)

    # -------------------
    # 相似度檢查（全檔案交叉比較）
    # -------------------
    similar_pairs = []
    uni_list = list(unique)
    N = len(uni_list)

    for i in range(N):
        for j in range(i + 1, N):
            sim = jaccard(uni_list[i], uni_list[j])
            if sim >= SIM_THRESHOLD:
                similar_pairs.append((uni_list[i], uni_list[j], sim))

    meta["similar_pairs"] = len(similar_pairs)

    # -------------------
    # 高熵語料分析（適用 H / S）
    # -------------------
    high_entropy_list = []
    for f in files:
        if f.stem.startswith("H") or f.stem.startswith("S"):
            values = []
            for line in per_file[f.name]:
                values.append(entropy(line))
            if values:
                avg_h = sum(values) / len(values)
                high_entropy_list.append({
                    "file": f.name,
                    "avg_entropy": avg_h,
                })

    meta["high_entropy"] = high_entropy_list

    return result, meta


# -----------------------------------
# 報告輸出
# -----------------------------------

def write_reports(result: Dict, meta: Dict):
    ts = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    json_path = REPORT_DIR / f"quality_report_{ts}.json"
    md_path = REPORT_DIR / f"quality_report_{ts}.md"

    # JSON
    with json_path.open("w", encoding="utf-8") as f:
        json.dump({"meta": meta, "result": result},
                  f, ensure_ascii=False, indent=2)

    # Markdown
    with md_path.open("w", encoding="utf-8") as f:
        f.write(f"# Corpus Quality Report ({ts})\n\n")
        f.write(f"Total Sentences: {meta['total_sentences']}\n")
        f.write(f"Duplicates Across All Files: {meta['duplicate_count']}\n")
        f.write(f"Similar Pairs: {meta['similar_pairs']}\n\n")

        f.write("## High Entropy Files\n")
        for h in meta["high_entropy"]:
            f.write(f"- {h['file']}: avg entropy = {h['avg_entropy']:.3f}\n")

        f.write("\n## Per-file Issues\n")
        for fname, issues in result.items():
            f.write(f"### {fname}\n")
            f.write(f"- Short Sentences: {len(issues['short'])}\n")
            f.write(f"- Duplicates: {len(issues['duplicates'])}\n\n")


# -----------------------------------
# Main
# -----------------------------------

if __name__ == "__main__":
    result, meta = analyze_corpus()
    write_reports(result, meta)
    print("[INFO] Quality check complete. Reports written.")
