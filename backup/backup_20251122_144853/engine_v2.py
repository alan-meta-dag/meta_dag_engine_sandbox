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
