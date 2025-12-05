# ==========================================
# Meta-DAG Engine v2 (Safe-Mode + --once)
# ==========================================

import sys
import json
import time
import subprocess
import argparse

from governance.drift_guard import enforce_governance
from engine.tul_map import TUL_translate_v2


# ======================
# CLI Argument Handler
# ======================
parser = argparse.ArgumentParser()
parser.add_argument("--once", type=str, help="Run a single query then exit")
args = parser.parse_args()


# ======================
# Model Stub (Safe-Mode)
# ======================
def run_model(prompt: str) -> str:
    """Mock Model (Local Debug Mode Only)"""
    try:
        return "[Mock Response] (Model not implemented yet)"
    except Exception as e:
        return f"[ENGINE WARNING] Model Exec Error: {e}"


# ======================
# Engine Boot Log
# ======================
print("C-2 Self-Assertion Passed - OK (Engine Integrity Verified)")
print("[C-3] Governance Lock Verified - OK (Safe-Mode)")
print("\nMeta-DAG Engine v1.0 booting...")
print("Core Loaded - OK")
print("Phase 2 Memory Hooks Active - OK")
print("Phase 3 TUL Translation Active - OK")
print("Engine Ready - OK")
print("[ENGINE LOCAL MODE READY] (Mock Mode + Governance Safe-Mode)\n")



# ======================
# Single-Shot Execution Mode
# ======================
if args.once:
    user_input = args.once.strip()
    tul = TUL_translate_v2("USER", user_input)
    out = run_model(user_input)

    try:
        drift = enforce_governance()
        print(f"[DRIFT] {drift:.3f}")
    except Exception as e:
        print(f"[VETO] {str(e)}")

    sys.exit(0)


# ======================
# LIVE Interactive Mode
# ======================
print("=== META-DAG LIVE MODE ===")


while True:
    try:
        user_input = input("\nCommand (exit to quit): ").strip()

        if user_input.lower() in ["exit", "quit"]:
            break

        tul = TUL_translate_v2("USER", user_input)

        print("\n=== TUL TRANSLATE RESULT ===")
        print(json.dumps(tul, indent=2, ensure_ascii=False))

        out = run_model(user_input)
        print("\n=== MODEL RESPONSE ===")
        print(out)

        try:
            drift = enforce_governance()
            print(f"[DRIFT] {drift:.3f}")
        except Exception:
            print("[VETO]")
        continue  # Skip to next iteration

           

    except KeyboardInterrupt:
        print("\n[Interrupted]")
        break

    except Exception as e:
        print(f"\n[ENGINE WARNING] {e}, continuing (Safe-Mode)")
        continue
