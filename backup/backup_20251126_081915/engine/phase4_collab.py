import json
import time
import hashlib
import random
from typing import Dict, Any, Tuple

# ===============================
# 常數區
# ===============================
MAX_RETRIES = 3
INITIAL_DELAY_SECONDS = 1
PEC6_FAILURE_STATUS = "REJECTED_PEC6_EXTERNAL_FAILURE"

# ===============================
# 依賴掛鉤（安全匯入）
# ===============================
from phase2_memory_engine import append_node

try:
    from pra_utils import auto_pra
except:
    from engine_v2 import auto_pra


# ===============================
# 簽名生成
# ===============================
def generate_signature(package: Dict[str, Any]) -> str:
    payload = {k: v for k, v in package.items() if k not in ("signature", "bridge_id")}
    json_string = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(json_string.encode("utf-8")).hexdigest()


# ===============================
# Calendar 映射
# ===============================
def map_to_calendar_event(bridge_package: Dict[str, Any]) -> Dict[str, Any]:
    context = bridge_package.get("C", {})
    task_type = bridge_package.get("T", "GENERIC_TASK")

    start_ts = context.get("timestamp", time.time() + 3600)
    end_ts = start_ts + 3600

    return {
        "summary": context.get("summary", f"Meta-DAG 協同事件: {task_type}"),
        "start": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(start_ts)),
        "end": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(end_ts)),
        "description": (
            f"Bridge ID: {bridge_package.get('bridge_id')}\n"
            f"Risk: {context.get('Risk_Level')}\n"
            f"PEC: {','.join(context.get('Inferred_PEC', []))}\n"
            f"Original: {context.get('Original_NL')}"
        ),
        "attendees": context.get("attendees", []),
        "calendar_type": bridge_package.get("P")
    }


# ===============================
# 模擬外部 API
# ===============================
def mock_calendar_api_send(event: Dict[str, Any], attempt: int) -> Tuple[bool, str]:
    if attempt in (0, 2):
        return False, "API_NETWORK_TIMEOUT"
    return True, "SUCCESS"

def mock_mq_send(topic: str, message: Dict[str, Any], attempt: int) -> Tuple[bool, str]:
    if attempt == 0:
        return True, "SUCCESS"
    return False, "MQ_SERVICE_BUSY"


# ===============================
# Phase 4 核心傳輸
# ===============================
def transmit_to_external_systems(tul_input: Dict[str, Any],
                                 l_alpha_verdict: Dict[str, Any],
                                 pra_report: Dict[str, Any]) -> Tuple[str, str]:

    bridge_package = {
        "P": tul_input.get("P"),
        "T": tul_input.get("T"),
        "C": tul_input.get("C"),
        "timestamp": time.time(),
        "version_marker": "V4.5-PEC6-SYNC"
    }

    bridge_package["signature"] = generate_signature(bridge_package)
    bridge_package["bridge_id"] = bridge_package["signature"][:12]

    pra_report["ExternalSyncRetries"] = {"calendar": 0, "mq": 0}

    # === Calendar 傳輸 ===
    calendar_event = map_to_calendar_event(bridge_package)
    success_calendar, calendar_error = False, ""

    for attempt in range(MAX_RETRIES):
        pra_report["ExternalSyncRetries"]["calendar"] = attempt + 1
        ok, err = mock_calendar_api_send(calendar_event, attempt)
        if ok:
            success_calendar = True
            break
        calendar_error = err
        time.sleep(INITIAL_DELAY_SECONDS * (2 ** attempt) + random.uniform(0, 0.5))

    # === MQ 傳輸 ===
    mq_topic = "meta_dag.collab.sync"
    success_mq, mq_error = False, ""

    for attempt in range(MAX_RETRIES):
        pra_report["ExternalSyncRetries"]["mq"] = attempt + 1
        ok, err = mock_mq_send(mq_topic, bridge_package, attempt)
        if ok:
            success_mq = True
            break
        mq_error = err
        time.sleep(INITIAL_DELAY_SECONDS * (2 ** attempt) + random.uniform(0, 0.5))

    # ===============================
    # 結果判斷
    # ===============================
    if success_calendar and success_mq:
        status = "PEC6_SYNC_SUCCESS"
        pra_report["ExternalSync"] = auto_pra(
            "PEC-6 Enforcement",
            "External Sync Success",
            status,
            "transmitter"
        )
    else:
        status = PEC6_FAILURE_STATUS
        l_alpha_verdict["Decision_Status"] = status
        l_alpha_verdict["Verdict_Reason"] = (
            f"Calendar={success_calendar}({calendar_error}), "
            f"MQ={success_mq}({mq_error})"
        )
        l_alpha_verdict["Veto_Class"] = "EXTERNAL_PEC6"

        pra_report["ExternalSync"] = auto_pra(
            "PEC-6 Enforcement",
            "External System Failure",
            status,
            "transmitter"
        )

    # === 寫入 DAG ===
    node_id = append_node(tul_input, l_alpha_verdict, pra_report)
    return status, node_id


# ===============================
# 示範測試
# ===============================
def demonstrate_phase4():
    tul = {
        "P": "V4.5/COLLAB",
        "T": "COLLAB_SYNC",
        "C": {
            "Risk_Level": "LOW",
            "Inferred_PEC": ["PEC-6"],
            "Original_NL": "建立 11/30 會議並同步所有系統",
            "timestamp": time.time() + 86400,
            "summary": "PEC-6 協同任務",
            "attendees": ["team-lead@dag.ccr"]
        }
    }

    verdict = {
        "Decision_Status": "ACCEPTED",
        "L_Alpha_Score": 0.05
    }

    pra = auto_pra("Arbitration", "Low", "Approved", "Engine")

    status, node = transmit_to_external_systems(tul, verdict, pra)
    print(f"[PHASE4 DEMO] status={status}, node={node}")

