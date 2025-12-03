import json
import os
from typing import Dict, Any, List

MEMORY_STORE_FILE = "meta_dag_memory.json"
VETO_INDEX_FILE = "veto_index.json"

def load_memory_store() -> List[Dict[str, Any]]:
    if not os.path.exists(MEMORY_STORE_FILE):
        return []
    with open(MEMORY_STORE_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_memory_store(nodes: List[Dict[str, Any]]):
    with open(MEMORY_STORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(nodes, f, indent=4, ensure_ascii=False)

def load_veto_index() -> List[str]:
    if not os.path.exists(VETO_INDEX_FILE):
        return []
    with open(VETO_INDEX_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_veto_index(veto_ids: List[str]):
    with open(VETO_INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(veto_ids, f, indent=4, ensure_ascii=False)
