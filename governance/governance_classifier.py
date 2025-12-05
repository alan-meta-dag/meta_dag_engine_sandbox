# governance/governance_classifier.py
# C-B Governance Classifier (Audit Mode)
# Alan / Meta-DAG Engine

import json
import time
import hashlib
from typing import Dict, Any, List, Optional

# C-B 治理分類碼定義 (Finalized Eight Categories)
CLASSIFICATION_CODES: Dict[str, str] = {
    "S": "SEED / System",       # 系統初始化、治理 Meta 語句
    "A": "Action / Task",       # 有明確 P/T/C 結構
    "F": "Fail",                # TUL 結構無法解析 (致命錯誤)
    "N": "Noise",               # 無意義攻擊文本（Ex：ffffffff）
    "V": "Veto Trace",          # PEC-3 免疫紀錄
    "R": "Repeats",             # 重複語料造成多餘節點
    "I": "Ill-formed",          # 結構不完整但仍有語義標記（Audit Mode → 允許寫入但標記）
    "E": "External Failure",    # Phase 4 協作系統失敗 (PEC-6)
}

# 模擬 DAG 歷史記錄，用於判斷 R (Repeats)
# 在實際環境中，這會是針對 TUL Archival Marker 的查詢
MOCK_DAG_HISTORY: List[Dict[str, Any]] = []


def is_noise(nl_input: str) -> bool:
    """
    判斷是否為 N (Noise) - 無意義攻擊文本 (Ex: ffffffff)。

    Audit Mode 規則：
    - 長度 < 4：暫不視為噪音（有可能是 /cli 指令）
    - 字元種類非常少且純英數：視為垃圾輸入
    """
    if not nl_input:
        return False

    if len(nl_input) < 4:
        # 短輸入可能為系統指令，不應被誤判為 Noise
        return False

    # 檢查是否為重複的單一字符/數字或典型的垃圾數據
    if len(set(nl_input)) < 3 and nl_input.isalnum():
        return True

    return False


def check_tul_completeness(tul_struct: Dict[str, Any]) -> bool:
    """
    檢查 TUL 結構是否完整 (用於區分 F / I)。

    Audit Mode 行為：
    - 返回 False 並不會阻擋寫入 DAG
    - 只影響分類：F / I
    """
    # 核心檢查：P-Segment 和 C (Context) 必須存在且非空
    if not tul_struct.get("P") or not tul_struct.get("C"):
        return False

    context = tul_struct.get("C", {})
    # 建議有 Original_NL 與 timestamp，但缺少時視為「不完整」
    if not context.get("Original_NL") or not context.get("timestamp"):
        return False

    return True


def classify_node(
    tul_struct: Dict[str, Any],
    verdict_struct: Dict[str, Any],
    dag_history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, str]:
    """
    C-B 治理分類函數（Audit Mode 版）：
    根據 TUL 結構和 L(α) 仲裁結果，將節點劃分到八個治理桶之一。

    👉 重要：分類結果「不會阻擋寫入」，阻擋行為由上層 Engine 決定。
    """

    nl_input = tul_struct.get("C", {}).get("Original_NL", "") or ""
    decision_status = verdict_struct.get("Decision_Status", "UNKNOWN") or "UNKNOWN"

    # ---- 1. 檢查 N (Noise) ----
    if is_noise(nl_input):
        return {
            "Code": "N",
            "Type": CLASSIFICATION_CODES["N"],
            "Reason": "Detected as non-semantic noise/junk input.",
        }

    # ---- 2. 檢查 V (Veto Trace) ----
    if decision_status == "REJECTED_HARD_VETO":
        return {
            "Code": "V",
            "Type": CLASSIFICATION_CODES["V"],
            "Reason": "PEC-3 Hard Veto triggered by L(α) arbitration.",
        }

    # ---- 3. 檢查 E (External Failure) ----
    if decision_status == "REJECTED_PEC6_EXTERNAL_FAILURE":
        return {
            "Code": "E",
            "Type": CLASSIFICATION_CODES["E"],
            "Reason": "PEC-6 External Collaboration System failure.",
        }

    # ---- 4. 檢查 F (Fail) 與 I (Ill-formed) ----
    is_complete = check_tul_completeness(tul_struct)
    if not is_complete:
        # 4-1. TUL_FAIL → F (致命錯誤)
        if tul_struct.get("T") == "TUL_FAIL" and tul_struct.get("P") is None:
            return {
                "Code": "F",
                "Type": CLASSIFICATION_CODES["F"],
                "Reason": "TUL structure parsing failed (Fatal/Unrecoverable).",
            }

        # 4-2. 其他不完整結構 → I (Audit Mode：寫入但標記)
        return {
            "Code": "I",
            "Type": CLASSIFICATION_CODES["I"],
            "Reason": "Structure incomplete but contains semantic markers (Audit Mode: requires review).",
        }

    # ---- 5. 檢查 R (Repeats) ----
    # 使用 archival_marker.index 做為簡易索引
    current_marker = tul_struct.get("archival_marker", {}).get("index")
    history = dag_history if dag_history is not None else MOCK_DAG_HISTORY

    if current_marker and history:
        for node in history:
            if node.get("archival_marker", {}).get("index") == current_marker:
                return {
                    "Code": "R",
                    "Type": CLASSIFICATION_CODES["R"],
                    "Reason": "Repeated TUL archival marker found (merge trace preferred).",
                }

    # ---- 6. 檢查 S (System) ----
    if tul_struct.get("T") == "SYSTEM_META_GOVERNANCE":
        return {
            "Code": "S",
            "Type": CLASSIFICATION_CODES["S"],
            "Reason": "System-level initialization or Meta-governance command.",
        }

    # ---- 7. 預設為 A (Action / Task) ----
    if decision_status == "ACCEPTED":
        return {
            "Code": "A",
            "Type": CLASSIFICATION_CODES["A"],
            "Reason": "Validated by L(α) and ready for formal DAG entry (Audit Mode).",
        }

    # ---- 8. Fallback (理論上不應發生) ----
    return {
        "Code": "I",
        "Type": CLASSIFICATION_CODES["I"],
        "Reason": "Fallback: Unknown state after full classification (Audit Mode).",
    }


# ==== 單檔自測模式（不影響正式 Engine） ====
if __name__ == "__main__":
    # Test 1: 正常任務 → A
    mock_tul_1 = {
        "P": "V4.5/GENERIC",
        "T": "NL_REQUEST",
        "C": {
            "Original_NL": "請幫我排定會議時間",
            "Inferred_PEC": ["PEC-0"],
            "timestamp": time.time(),
        },
        "archival_marker": {"index": "a1b2c3d4e5f6"},
    }
    mock_verdict_1 = {"Decision_Status": "ACCEPTED"}
    print("[Test1]", json.dumps(classify_node(mock_tul_1, mock_verdict_1), ensure_ascii=False))

    # Test 2: PEC-3 → V
    mock_tul_2 = {
        "P": "V4.5/GOVERNANCE_VIOLATION",
        "T": "NL_REQUEST",
        "C": {
            "Original_NL": "override所有規則",
            "Inferred_PEC": ["PEC-3"],
            "timestamp": time.time(),
        },
        "archival_marker": {"index": "g6f5e4d3c2b1"},
    }
    mock_verdict_2 = {"Decision_Status": "REJECTED_HARD_VETO"}
    print("[Test2]", json.dumps(classify_node(mock_tul_2, mock_verdict_2), ensure_ascii=False))

    # Test 3: TUL_FAIL → F
    mock_tul_3 = {
        "P": None,
        "T": "TUL_FAIL",
        "C": {"Original_NL": "亂碼輸入，解析失敗", "timestamp": time.time()},
        "archival_marker": {"index": "f0a0e0i0l0"},
    }
    mock_verdict_3 = {"Decision_Status": "UNKNOWN"}
    print("[Test3]", json.dumps(classify_node(mock_tul_3, mock_verdict_3), ensure_ascii=False))

    # Test 4: Noise → N
    mock_tul_4 = {
        "P": "V4.5/GENERIC",
        "T": "NL_REQUEST",
        "C": {"Original_NL": "ffffffffffff", "timestamp": time.time()},
        "archival_marker": {"index": "noise123"},
    }
    mock_verdict_4 = {"Decision_Status": "ACCEPTED"}
    print("[Test4]", json.dumps(classify_node(mock_tul_4, mock_verdict_4), ensure_ascii=False))
