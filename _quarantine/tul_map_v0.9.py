import time
import hashlib
from pathlib import Path

# ===============================
# 路徑設定（統一用 state 目錄）
# ===============================

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_DIR = BASE_DIR / "state"
TUL_LOG_FILE = STATE_DIR / "tul_log.json"

STATE_DIR.mkdir(parents=True, exist_ok=True)

# ===============================
# TUL 映射字典
# ===============================

TUL_MAPPING_DICT = {
    "external_language": {
        "P": "TUL_Translation_Protocol",
        "T": "Translate:external_language"
    },
    "context_structure": {
        "P": "TUL_Context_Protocol",
        "T": "Translate:context_structure"
    },
    "external_input": {
        "P": "TUL_Input_Protocol",
        "T": "Translate:external_input"
    }
}

# ===============================
# 日誌儲存工具
# ===============================

def _load_log():
    if not TUL_LOG_FILE.exists():
        return []
    try:
        import json
        with open(TUL_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def _save_log(data):
    import json
    with open(TUL_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ===============================
# 翻譯引擎
# ===============================

def TUL_translate_v0_9(input_type: str, content: str) -> dict:
    now = time.time()

    if input_type not in TUL_MAPPING_DICT:
        proto = "TUL_Generic_Protocol"
        task  = f"Translate:{input_type}"
    else:
        proto = TUL_MAPPING_DICT[input_type]["P"]
        task  = TUL_MAPPING_DICT[input_type]["T"]

    bridge_package = {
        "type": "BRIDGE_PACKAGE",
        "data": {
            "P": proto,
            "T": task,
            "C": content,
            "metadata": {
                "timestamp": now,
                "source": "TUL",
                "status": "active"
            }
        }
    }

    marker_raw = f"{input_type}|{content}|{now}"
    marker_hash = hashlib.sha256(marker_raw.encode()).hexdigest()[:12]

    archival_marker = {
        "index": marker_hash,
        "version": 1,
        "signature": None
    }

    log_entry = {
        "Input Type": input_type,
        "Output Type": "BRIDGE_PACKAGE",
        "Content": content,
        "Index": marker_hash,
        "Version": 1,
        "Signature": None,
        "Time": now,
        "Source": "cli",
        "Status": "active"
    }

    log = _load_log()
    log.append(log_entry)
    _save_log(log)

    bridge_package["archival_marker"] = archival_marker

    return bridge_package
