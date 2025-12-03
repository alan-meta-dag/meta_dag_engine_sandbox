import json
import os

print("Meta-DAG Engine v0.1 booting...")

base_path = os.path.dirname(__file__)

core_path = os.path.join(base_path, "meta_dag.core.json")
runtime_path = os.path.join(base_path, "meta_dag.runtime.json")

# ===== Load Core =====
try:
    with open(core_path, "r", encoding="utf-8") as f:
        core = json.load(f)
    print("Core Loaded ✅")
except Exception as e:
    print("Core Load Failed:", e)

# ===== Load Runtime =====
try:
    with open(runtime_path, "r", encoding="utf-8") as f:
        runtime = json.load(f)
    print("Runtime Loaded ✅")
except Exception as e:
    print("Runtime Load Failed:", e)

print("Engine Ready ✅")

# ====== CLI ENTRYPOINT ======
import sys

def dump_missing(core, runtime):
    print("\n[DEBUG] Scanning for missing keys...\n")

    required_core_keys = ["system", "owner", "version", "principles", "nodes", "edges"]
    required_runtime_keys = ["meta", "profiles"]

    missing_core = []
    missing_runtime = []

    for k in required_core_keys:
        if k not in core:
            missing_core.append(k)

    for k in required_runtime_keys:
        if k not in runtime:
            missing_runtime.append(k)

    if not missing_core and not missing_runtime:
        print("[OK] No missing keys ✅")
    else:
        if missing_core:
            print("[MISSING] core.json missing:")
            for k in missing_core:
                print("  -", k)

        if missing_runtime:
            print("[MISSING] runtime.json missing:")
            for k in missing_runtime:
                print("  -", k)

    print("\n[Scan Completed]\n")


if __name__ == "__main__":
    if "--export-state" in sys.argv:
        print("[DEBUG] Exporting runtime state...")

        state = {
            "core_loaded": bool(core),
            "runtime_loaded": bool(runtime),
            "core_version": core.get("meta", {}).get("version", "unknown"),
            "runtime_version": runtime.get("meta", {}).get("version", "unknown"),
            "profiles": list(runtime.get("profiles", {}).keys())
        }

        with open("meta_dag.state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        print("[OK] Exported meta_dag.state.json ✅")

import subprocess

def run_model(prompt):
    result = subprocess.run(
        ["ollama", "run", "gemma3:4b"],
        input=prompt,
        text=True,
        encoding="utf-8",
        capture_output=True
    )
    return result.stdout.strip()


if __name__ == "__main__":
    print("\n=== META-DAG LIVE MODE ===")

    while True:
        user_input = input("\nCommand (exit to quit): ")

        if user_input.lower() in ["exit", "quit"]:
            print("Bye 👋")
            break

        output = run_model(user_input)

        print("\n=== MODEL RESPONSE ===")
        print(output)
