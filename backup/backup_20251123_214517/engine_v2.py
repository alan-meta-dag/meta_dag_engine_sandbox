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
import json

MEMORY_FILE = "memory.json"

META_DAG_PROFILE = """
[Meta-DAG Governance Profile v0.1]
Mode: Local Governance Engine

Rules:
- Self-contained system. No external blockchain references allowed.
- Nodes are BRIDGE_PACKAGE (P/T/C).
- Edges follow PEC semantic laws.
- Consensus via L(α), constrained by Minimal Seed + P.R.A.
- Output must align with ISO/NIST governance structure.
- Forbidden topics:
  * Blockchain / Testnet / Token / Dapp / Official website
"""

def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"memories": []}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def remember(text):
    data = load_memory()
    data["memories"].append(text)
    save_memory(data)

PEC_COMPONENTS = [
    {
        "component": "PEC1_PowerTracing",
        "requires": ["id", "source", "version"],
        "rule": "每個 BRIDGE_PACKAGE 必須標記來源與版本，並可追溯至治理核心"
    },
    {
        "component": "PEC2_RoleBehavior",
        "requires": ["role", "behavior"],
        "rule": "節點輸出必須符合角色語氣定義，不得偏移"
    },
    {
        "component": "PEC3_VetoImmunity",
        "requires": ["decision", "veto_flag"],
        "rule": "所有否決決策必須保留，不得被覆蓋或刪除"
    },
    {
        "component": "PEC4_TermAnchoring",
        "requires": ["terms", "anchor_ref"],
        "rule": "所有術語必須對應錨點詞典，禁止漂移"
    },
    {
        "component": "PEC5_PowerTermination",
        "requires": ["expiry", "termination_condition"],
        "rule": "所有節點必須定義退出條件，並在到期時自動失效"
    },
    {
        "component": "PEC6_CollaborativeEnforcement",
        "requires": ["sync_status", "partner_systems"],
        "rule": "所有跨平台傳輸必須同步一致，不得偏移"
    }
]

def validate_pec(node: dict):
    errors = []

    for law in PEC_COMPONENTS:
        for field in law["requires"]:
            if field not in node:
                errors.append(
                    f"{law['component']} 缺少必要欄位: {field}"
                )

    return errors

def arbitration_L_alpha(candidates, weights, thresholds):
    trace_log = []

    # Step 1: validate_source (PEC-1)
    valid_candidates = []
    for c in candidates:
        if "source" in c and c["source"]:
            valid_candidates.append(c)
            trace_log.append(f"PEC1 PASS: {c['id']}")
        else:
            trace_log.append(f"PEC1 FAIL: {c.get('id','unknown')}")
    
    # Step 2: check_veto (PEC-3)
    non_veto_candidates = []
    for c in valid_candidates:
        if c.get("veto_flag") is True:
            trace_log.append(f"PEC3 VETO: {c['id']}")
        else:
            non_veto_candidates.append(c)

    # Step 3: apply_weights()
    scored = []
    for c in non_veto_candidates:
        w = weights.get(c["id"], 1.0)
        scored.append((c, w))
        trace_log.append(f"WEIGHT APPLIED: {c['id']} = {w}")

    if not scored:
        return None, trace_log

    # Step 4: enforce_thresholds()
    threshold = thresholds.get("min_score", 0)
    passed = [c for c, w in scored if w >= threshold]

    for c, w in scored:
        if w >= threshold:
            trace_log.append(f"THRESHOLD PASS: {c['id']}")
        else:
            trace_log.append(f"THRESHOLD FAIL: {c['id']}")

    # 選最大權重者
    accepted_view = max(passed, key=lambda c: weights.get(c["id"], 1.0)) if passed else None

    return accepted_view, trace_log


def run_model(prompt):
    # ① 先檢查是否為 JSON（直接走 PEC，不丟給模型）
    if prompt.strip().startswith("{"):
        try:
            node = json.loads(prompt)
            pec_errors = validate_pec(node)
            if pec_errors:
                return "[PEC VIOLATION]\n" + "\n".join(pec_errors)
            return "[PEC PASS]"
        except Exception as e:
            return f"[PEC CHECK ERROR] {str(e)}"

    # ② 非 JSON 才交給模型
    controlled_prompt = META_DAG_PROFILE + "\n\n[User] " + prompt + "\n[Engine]"
    result = subprocess.run(
        ["ollama", "run", "gemma3:4b"],
        input=controlled_prompt,
        text=True,
        encoding="utf-8",
        capture_output=True
    )
    return result.stdout.strip()

    
    try:
        node = json.loads(output)
        pec_errors = validate_pec(node)
        if pec_errors:
            return "[PEC VIOLATION]\n" + "\n".join(pec_errors)
    except:
        pass

    return output

if __name__ == "__main__":
    print("\n=== META-DAG LIVE MODE ===")

    try:
        while True:
            user_input = input("\nCommand (exit to quit): ")

            if user_input.lower() in ["exit", "quit"]:
                print("Bye 👋")
                break

            if user_input.strip() == "":
                continue

            if user_input.startswith("/remember "):
                remember(user_input.replace("/remember ", ""))
                print("[Memory Saved ✅]")
                continue

            try:
                output = run_model(user_input)
            except Exception as e:
                output = f"[Model Error] {str(e)}"

            print("\n=== MODEL RESPONSE ===")
            print(output)

    except KeyboardInterrupt:
        print("\n[Interrupted]")
