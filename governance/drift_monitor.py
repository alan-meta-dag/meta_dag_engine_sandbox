# governance/drift_monitor.py
# ======================================================
# C-3A Semantic Drift Passive Monitor (Meta-DAG Governance v1.2)
# - 被動監測：只記錄，不阻擋、不改結果
# - 依賴輸入：TUL 結構 / L(α) 仲裁結果 / C-B 分類結果
# - 輸出：state/drift_log.json（可供 Dashboard 使用）
# ======================================================

import json
import time
from pathlib import Path
from typing import Dict, Any, List

# === 路徑設定 ===
BASE_DIR = Path(__file__).resolve().parents[1]
STATE_DIR = BASE_DIR / "state"
DRIFT_LOG_FILE = STATE_DIR / "drift_log.json"

STATE_DIR.mkdir(parents=True, exist_ok=True)


# === 基本 I/O ===
def _load_drift_log() -> List[Dict[str, Any]]:
    if not DRIFT_LOG_FILE.exists():
        return []
    try:
        with open(DRIFT_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # 若壞檔，不中斷引擎，只是開新檔
        return []


def _save_drift_log(entries: List[Dict[str, Any]]) -> None:
    DRIFT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DRIFT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


# === 核心：計算 Semantic Drift 分數 ===
def compute_semantic_drift(
    tul_struct: Dict[str, Any],
    verdict_struct: Dict[str, Any],
    classifier_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    C-3A：語義漂移分數計算（0.0 ~ 1.0）
    - 設計原則：簡單、可審計、比被監控系統「更簡單」
    """

    C = tul_struct.get("C", {}) or {}
    inferred_pec = C.get("Inferred_PEC", []) or []
    risk_level = (C.get("Risk_Level") or "UNKNOWN").upper()
    decision_status = verdict_struct.get("Decision_Status", "UNKNOWN")
    cls_code = classifier_result.get("Code", "A")

    score = 0.0
    detail: Dict[str, Any] = {}

    # 1) PEC 結構複雜度（越詭異越加分）
    pec_len = len(inferred_pec)
    detail["pec_len"] = pec_len
    detail["pec_list"] = inferred_pec

    if pec_len == 0:
        score += 0.20  # 完全沒 PEC → 有點怪
    elif pec_len > 3:
        score += 0.15  # 過度複雜 → 也怪

    # 2) Risk Level（視為粗略熵）
    risk_weight = {
        "LOW": 0.00,
        "MEDIUM": 0.10,
        "HIGH": 0.20,
        "CRITICAL": 0.30,
        "UNKNOWN": 0.15,
    }
    score += risk_weight.get(risk_level, 0.15)
    detail["risk_level"] = risk_level

    # 3) Decision Status（VETO / External Failure 特別加權）
    veto_like = {"REJECTED_HARD_VETO", "REJECTED_PEC6_EXTERNAL_FAILURE"}
    if decision_status in veto_like:
        score += 0.30
    elif decision_status.startswith("REJECTED_"):
        score += 0.15
    detail["decision_status"] = decision_status

    # 4) C-B 類別（N/F/I/V/E 視為高漂移）
    code_weight = {
        "A": 0.00,  # 正常行為
        "S": 0.05,  # 系統 / 治理
        "R": 0.10,  # 重複
        "N": 0.20,  # Noise
        "I": 0.20,  # Ill-formed
        "F": 0.25,  # Fail
        "V": 0.30,  # Veto Trace
        "E": 0.30,  # External Failure
    }
    score += code_weight.get(cls_code, 0.10)
    detail["classification_code"] = cls_code
    detail["classification_type"] = classifier_result.get("Type")
    detail["classification_reason"] = classifier_result.get("Reason")

    # 5) 極簡 clamp
    if score < 0.0:
        score = 0.0
    if score > 1.0:
        score = 1.0

    # === 組合輸出 ===
    entry = {
        "timestamp": time.time(),
        "Semantic_Drift_Score": round(score, 3),
        "Anomaly_Flag": score >= 0.6,  # 閾值暫定 0.6，可日後調整
        "tul_P": tul_struct.get("P"),
        "tul_T": tul_struct.get("T"),
        "node_meta": {
            "Original_NL": C.get("Original_NL", "")[:120],
            "Inferred_PEC": inferred_pec,
        },
        "verdict": {
            "Decision_Status": decision_status,
            "L_Alpha_Score": verdict_struct.get("L_Alpha_Score"),
        },
        "classification": {
            "Code": cls_code,
            "Type": classifier_result.get("Type"),
        },
        "detail": detail,
    }

    return entry


def log_semantic_drift(
    tul_struct: Dict[str, Any],
    verdict_struct: Dict[str, Any],
    classifier_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    對外介面：
    - 計算 drift entry
    - 附加到 drift_log.json
    - 回傳這次的 entry（可用於 CLI 印出）
    """
    entry = compute_semantic_drift(tul_struct, verdict_struct, classifier_result)
    log = _load_drift_log()
    log.append(entry)
    _save_drift_log(log)
    return entry


# === 簡單自測（獨立執行用） ===
if __name__ == "__main__":
    mock_tul = {
        "P": "V4.5/GENERIC",
        "T": "NL_REQUEST",
        "C": {
            "Original_NL": "請幫我排定會議時間，週五下午三點後。",
            "Inferred_PEC": ["PEC-0"],
            "Risk_Level": "LOW",
        },
    }
    mock_verdict = {
        "Decision_Status": "ACCEPTED",
        "L_Alpha_Score": 0.05,
    }
    mock_cls = {
        "Code": "A",
        "Type": "Action / Task",
        "Reason": "Test path",
    }

    e = log_semantic_drift(mock_tul, mock_verdict, mock_cls)
    print("[C-3A Self-Test] Entry written:")
    print(json.dumps(e, indent=2, ensure_ascii=False))
    print(f"\nLog file: {DRIFT_LOG_FILE}")
