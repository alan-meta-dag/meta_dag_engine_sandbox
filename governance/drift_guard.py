# governance/drift_guard.py (C-4 Balanced Governance)
import os
import json
import time
from governance.drift_index import compute_drift_index

RULES_PATH = "governance/governance_thresholds.json"
SNAP_DIR = "state/drift_snapshots"
os.makedirs(SNAP_DIR, exist_ok=True)

# fallback default (若 thresholds 未建立)
SNAPSHOT_THRESHOLD = 0.69
VETO_THRESHOLD = 0.92

# ====== Load Dynamic Governance Config ======
if os.path.exists(RULES_PATH):
    try:
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            SNAPSHOT_THRESHOLD = cfg.get("threshold_snapshot", SNAPSHOT_THRESHOLD)
            VETO_THRESHOLD = cfg.get("threshold_veto", VETO_THRESHOLD)
    except Exception as e:
        print(f"[Governance Warning] threshold config load failed: {e}")

print(f"[Governance] Thresholds Loaded → Snapshot={SNAPSHOT_THRESHOLD:.3f}, Veto={VETO_THRESHOLD:.3f}")

# ===========================================================
#   C-4 Drift Governance Handler
# ===========================================================
def enforce_governance():
    drift = compute_drift_index()

    # Print index for visibility
    print(f"[Governance] drift-index = {drift:.3f}")

    # Snapshot zone — abnormal but not lethal
    if drift >= SNAPSHOT_THRESHOLD:
        snap_file = os.path.join(SNAP_DIR, f"snapshot_{time.time_ns()}.json")
        with open(snap_file, "w", encoding="utf-8") as f:
            json.dump({"drift_index": drift, "time": time.time()}, f, indent=2)
        print(f"[Snapshot] {snap_file}")

    # Hard veto — severe semantic drift
    if drift >= VETO_THRESHOLD:
        raise RuntimeError("ERR_SEMANTIC_DRIFT")

    return drift
