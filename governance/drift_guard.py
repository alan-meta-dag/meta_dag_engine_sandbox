# governance/drift_guard.py
import os
import json
import time
from governance.drift_index import compute_drift_index

RULES_PATH = "governance/governance_rules.json"
SNAP_DIR = "state/drift_snapshots"
os.makedirs(SNAP_DIR, exist_ok=True)

def enforce_governance():
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        rules = json.load(f)

    drift = compute_drift_index()
    threshold = rules["drift_threshold"]
    rollback_th = rules["rollback_threshold"]
    snapshot_flag = rules["snapshot_on_violation"]

    print(f"[Governance] drift-index = {drift}")

    # snapshot if needed
    if snapshot_flag and drift > threshold:
        snap_file = os.path.join(SNAP_DIR, f"snapshot_{time.time_ns()}.json")
        with open(snap_file, "w", encoding="utf-8") as f:
            json.dump({"drift_index": drift, "time": time.time()}, f, indent=2)
        print(f"[Snapshot] {snap_file}")

    # veto high drift
    if drift > rollback_th:
        raise RuntimeError("ERR_SEMANTIC_DRIFT")

    return drift
