import json
import time
import hashlib
import os
from typing import Dict, Any, List
from pathlib import Path

# ===============================
# 路徑設定（符合你的新結構）
# /meta_dag_engine/
#   ├── engine/
#   ├── state/
#   └── manifest/
# ===============================

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_DIR = BASE_DIR / "state"

MEMORY_STORE_FILE = STATE_DIR / "meta_dag_memory.json"
VETO_INDEX_FILE = STATE_DIR / "veto_index.json"


# ===============================
# 儲存層工具
# ===============================

def load_memory_store() -> List[Dict[str, Any]]:
    if not MEMORY_STORE_FILE.exists():
        return []
    with open(MEMORY_STORE_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_memory_store(nodes: List[Dict[str, Any]]):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_STORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(nodes, f, indent=4, ensure_ascii=False)

def load_veto_index() -> List[str]:
    if not VETO_INDEX_FILE.exists():
        return []
    with open(VETO_INDEX_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_veto_index(veto_ids: List[str]):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(VETO_INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(veto_ids, f, indent=4, ensure_ascii=False)

# ===============================
# 節點寫入與鏈結
# ===============================

def append_node(tul_input: Dict[str, Any], l_alpha_verdict: Dict[str, Any], pra_report: Dict[str, Any]) -> str:
    memory_nodes = load_memory_store()

    # 鏈結前一節點
    if memory_nodes:
        previous_node_id = memory_nodes[-1]["Node_ID"]
        node_index = memory_nodes[-1]["Node_Index"] + 1
    else:
        previous_node_id = "GENESIS_NODE_0000"
        node_index = 1

    creation_timestamp = time.time()

    core_content = json.dumps([tul_input, l_alpha_verdict, pra_report], sort_keys=True)
    node_hash = hashlib.sha256(f"{creation_timestamp}-{core_content}".encode()).hexdigest()
    node_id = f"TS{int(creation_timestamp)}_{node_hash[:8]}"

    new_node = {
        "Node_ID": node_id,
        "Node_Index": node_index,
        "Previous_Node_ID": previous_node_id,
        "Creation_Timestamp": creation_timestamp,
        "TUL_Input": tul_input,
        "L_Alpha_Verdict": l_alpha_verdict,
        "PRA_Final_Report": pra_report
    }

    memory_nodes.append(new_node)
    save_memory_store(memory_nodes)

    # 自動寫入 VETO 索引
    if l_alpha_verdict.get("Decision_Status") == "REJECTED_HARD_VETO":
        veto_log(node_id)

    return node_id

# ===============================
# VETO 索引
# ===============================

def veto_log(node_id: str):
    veto_index = load_veto_index()
    if node_id not in veto_index:
        veto_index.append(node_id)
        save_veto_index(veto_index)
        print(f"[PEC-3 VETO] Node {node_id} added to veto index.")

def get_veto_log() -> List[Dict[str, Any]]:
    veto_index = load_veto_index()
    all_nodes = load_memory_store()
    return [node for node in all_nodes if node["Node_ID"] in veto_index]

# ===============================
# 查詢工具
# ===============================

def pra_query(query_type: str, value: Any) -> List[Dict[str, Any]]:
    all_nodes = load_memory_store()
    results = []

    for node in all_nodes:
        if query_type == 'time':
            if node["Creation_Timestamp"] >= value[0] and node["Creation_Timestamp"] <= value[1]:
                results.append(node)

        elif query_type == 'pec':
            if value in node["TUL_Input"]["C"].get("Inferred_PEC", []):
                results.append(node)

        elif query_type == 'status':
            if node["L_Alpha_Verdict"].get("Decision_Status") == value:
                results.append(node)

    return results
