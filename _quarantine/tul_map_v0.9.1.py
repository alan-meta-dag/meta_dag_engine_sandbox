import json
import time
import hashlib
from typing import Dict, Any, List

# --- TUL Constants and Mappings ---
# TUL 協議版本
TUL_VERSION = "V4.5"

# 模擬語義錨點 (Semantic Anchors) - 實際應來自 Phase 1 L0/L1 模型
SEMANTIC_ANCHORS = {
    "collab": ["meeting", "sync", "collaboration", "review", "calendar"],
    "finance": ["budget", "invoice", "payment", "reimbursement", "fund"],
    "risk": ["exploit", "vulnerability", "leak", "drift", "failure", "veto"]
}

# 模擬 PEC (Policy Enforcement Cluster) 推導規則
PEC_RULES = {
    "PEC-6": lambda nl: any(word in nl.lower() for word in ["sync", "collab", "external", "calendar", "review"]), # 協同傳輸
    "PEC-1": lambda nl: any(word in nl.lower() for word in ["budget", "finance", "payment", "fund"]), # 財政審計
    "PEC-3": lambda nl: any(word in nl.lower() for word in ["leak", "vulnerability", "drift", "veto"]) # 風險控制
}

def derive_output_type(input_type: str) -> str:
    """根據輸入類型推導輸出類型。"""
    if "request" in input_type.lower() or "sync" in input_type.lower():
        return "STATE_CHANGE"
    return "ANALYSIS"

def infer_pec_cluster(nl_input: str) -> List[str]:
    """根據自然語言輸入推導適用的 PEC 集。"""
    inferred = []
    for pec, rule in PEC_RULES.items():
        if rule(nl_input):
            inferred.append(pec)
    return inferred if inferred else ["PEC-0 (Generic)"]


def TUL_translate_v0_9_1(nl_input: str, input_type: str = "NL_REQUEST", source: str = "cli") -> Dict[str, Any]:
    """
    Phase 3 核心：TUL 翻譯層 V2.0。
    將自然語言/事件轉換為標準 V4.5 結構，包含風險和 PEC 推導。
    """
    ts = time.time()
    
    # 1. 語義錨點分析
    anchors = [k for k, v in SEMANTIC_ANCHORS.items() if any(word in nl_input.lower() for word in v)]
    
    # 2. PEC 推導
    inferred_pec = infer_pec_cluster(nl_input)

    # 3. 建立 TUL V4.5 結構
    tul_struct = {
        "P": f"{TUL_VERSION}/{'-'.join(anchors).upper() or 'GENERIC'}",  # Protocol
        "T": input_type,  # Type
        "C": { # Context
            "Original_NL": nl_input,
            "Inferred_PEC": inferred_pec,
            "Semantic_Anchors": anchors,
            "Risk_Level": "HIGH" if "PEC-3" in inferred_pec else "MEDIUM", # 簡化風險推導
            "timestamp": ts,
            "duration": 3600, # 預設一小時
            "summary": f"TUL V2: {nl_input[:30]}...",
            "attendees": ["system@dag.ccr"]
        },
        "OUT": derive_output_type(input_type), # Expected Output Type
        "archival_marker": {
            "index": hashlib.sha256(f"{nl_input}|{ts}".encode()).hexdigest()[:12],
            "version": 2
        }
    }
    
    return tul_struct

if __name__ == "__main__":
    # 測試示範
    test_queries = [
        "建立一個 11 月 30 日關於系統同步的會議，並確保所有外部日曆都同步。",
        "請批准支付 5000 美元的項目發票。",
        "發現了潛在的資料洩漏風險，需要立即處理。"
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n--- Test Query {i+1}: {query} ---")
        tul_output = TUL_translate_v2(query)
        print(json.dumps(tul_output, indent=4, ensure_ascii=False))