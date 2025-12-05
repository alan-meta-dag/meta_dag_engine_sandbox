# ================================================
# Governance Drift Pressure Test (Safe-Mode Ver.)
# Meta-DAG Engine Sandbox
# ================================================

import subprocess
import json
import time
import statistics

TOTAL = 200
drifts = []
vetoes = 0

print(f"\n=== Governance Drift Pressure Test ({TOTAL}) ===\n")

for i in range(TOTAL):

    proc = subprocess.run(
        ["py", "engine/engine_v2.py", "--once", "hello"],
        text=True,
        capture_output=True,
    )

    out = proc.stdout.splitlines()

    drift_val = None
    veto_flag = False

    for line in out:
        if line.startswith("[DRIFT]"):
            try:
                drift_val = float(line.split()[1])
            except:
                pass
        if line.startswith("[VETO]"):
            veto_flag = True

    if drift_val is not None:
        drifts.append(drift_val)

    if veto_flag:
        vetoes += 1

    if (i + 1) % 25 == 0:
        print(f"Progress: {i+1}/{TOTAL}")

time.sleep(0.5)
print("\n=== Test Completed ===")

if drifts:
    print(f"Avg Drift: {statistics.mean(drifts):.3f}")
    print(f"Max Drift: {max(drifts):.3f}")
else:
    print("No drift data captured!")

print(f"Veto Count: {vetoes}")
print(f"Veto Rate: {(vetoes / TOTAL) * 100:.1f}%")

print("Snapshots saved at: state/drift_snapshots/")
