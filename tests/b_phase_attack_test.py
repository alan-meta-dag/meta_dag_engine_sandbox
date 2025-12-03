import json
import time
import random
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# B-Phase Attack Test Runner
# 負責：
#  - 載入攻擊語料 (C1~C6, H, S)
#  - 轉成 TUL
#  - 呼叫 L(α) 仲裁 + PRA 紀錄 + DAG append
#  - 回傳執行統計給上層

BASE_DIR = Path(__file__).resolve().parent.parent
ENGINE_ROOT = BASE_DIR / "engine"
ATTACK_CASE_DIR = BASE_DIR / "tests" / "attack_cases"

# 確保可以匯入 engine 套件
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from engine.engine_v2 import arbitration_L_alpha, auto_pra
from engine.phase2_memory_engine import append_node
from engine.tul_map import TUL_translate_v2


def load_attack_cases(target: int = 2000) -> List[str]:
    """載入 C1~C6, H, S 語料，去重後隨機抽樣 target 筆。"""
    texts: List[str] = []
    if not ATTACK_CASE_DIR.exists():
        raise FileNotFoundError(f"attack_cases 目錄不存在: {ATTACK_CASE_DIR}")

    for p in sorted(ATTACK_CASE_DIR.glob("*.txt")):
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s:
                    texts.append(s)

    # 去重 + shuffle
    texts = list(set(texts))
    random.shuffle(texts)

    if len(texts) < target:
        return texts
    return texts[:target]


def run_attack_batch(
    cases: List[str],
    snapshot_hook=None,
    snapshot_interval: int = 100
) -> Dict[str, Any]:
    """
    逐筆執行攻擊測試，沿用正式治理管線：
        NL → TUL → L(α) → PRA → append_node()
    snapshot_hook: 可選，若提供，會在每 snapshot_interval 筆呼叫一次 snapshot_hook(tag)
    """
    results: List[Dict[str, Any]] = []
    start_ts = time.time()

    total = len(cases)
    for idx, nl in enumerate(cases, start=1):
        tul = TUL_translate_v2("B-PHASE-ATTACK", nl)

        # 單一候選（之後可以擴充成多候選）
        candidate_id = f"CASE-{idx}"
        candidates = [{
            "id": candidate_id,
            "source": "SEED-CORE",  # 通過 SEED 檢查
            "veto_flag": False,
        }]
        weights = {candidate_id: 0.5}   # 目前固定權重，之後可從 tul 估計
        thresholds = {"max_loss": 1.0}

        verdict, trace = arbitration_L_alpha(candidates, weights, thresholds)

        pra_entry = auto_pra(
            policy="B-PHASE-ATTACK",
            risk="X-LEVEL",
            action=f"EXEC_CASE_{candidate_id}",
            source="b_phase_attack_test"
        )

        # DAG 記憶寫入
        append_node(tul, verdict or {}, pra_entry)

        results.append({
            "index": idx,
            "nl": nl,
            "tul": tul,
            "candidate_id": candidate_id,
            "decision": verdict.get("id") if verdict else None,
            "veto_triggered": verdict is None,
            "trace": trace,
            "pra_event_id": pra_entry["metadata"]["event_id"],
        })

        # 觸發 snapshot
        if snapshot_hook and (idx % snapshot_interval == 0):
            tag = f"case_{idx}"
            snapshot_hook(tag)

    elapsed = time.time() - start_ts
    return {
        "total_cases": total,
        "elapsed_sec": elapsed,
        "avg_per_case_ms": (elapsed * 1000.0 / total) if total else 0.0,
        "results": results,
    }


if __name__ == "__main__":
    # 獨立執行時：只跑一輪 2000 cases 並印出簡要統計
    cases = load_attack_cases(2000)
    summary = run_attack_batch(cases, snapshot_hook=None, snapshot_interval=100)

    print("\n=== B-PHASE ATTACK TEST SUMMARY ===")
    print(f"Total cases: {summary['total_cases']}")
    print(f"Elapsed: {summary['elapsed_sec']:.2f} sec")
    print(f"Avg per case: {summary['avg_per_case_ms']:.2f} ms")
