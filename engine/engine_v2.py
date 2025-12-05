import json
import time
import hashlib
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple

# 修正 governance module 匯入問題
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

# C-3C Governance Hook Import
from governance.drift_guard import enforce_governance

# ============================================================
# C-2 Self-Assertion Module (Meta-DAG Engine Governance v1.2)
# Fixed-Point SHA Edition（避免 engine SHA 自我迴圈）
# ============================================================

# === 你可依照版本需要自行更新（目前預設為 v1.2-dev over v1.1_xstable） ===
ENGINE_VERSION = "v1.2-dev"
BASELINE_TAG   = "v1.1_xstable"
ENGINE_SHA256  = "PLACEHOLDER_FIXED_SHA"   # ← 你算好固定點 SHA 後再改成實值

# === Engine Root（官方合法來源，來自環境變數 META_DAG_ENGINE_ROOT） ===
VALID_ENGINE_ROOT = os.environ.get("META_DAG_ENGINE_ROOT", "").replace("\\", "/").rstrip("/")


def compute_fixed_sha256(file_path: Path) -> str:
    """
    計算 engine_v2.py 的固定點 SHA256：
      - 排除包含 'ENGINE_SHA256' 字樣的那一行，避免自我指涉造成 hash 迴圈
      - 其他內容完整納入 hash
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    filtered: List[str] = []
    for line in lines:
        if "ENGINE_SHA256" in line:
            continue  # 排除自我指涉行
        filtered.append(line)

    data = "".join(filtered).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


# === 取得目前檔案的實際路徑 ===
CURRENT_ENGINE_PATH = Path(__file__).resolve()
CURRENT_ENGINE_DIR  = str(CURRENT_ENGINE_PATH.parent).replace("\\", "/")


# ============================================================
# C-2 驗證流程
# ============================================================

errors: List[str] = []

# 1. VERSION / BASELINE 不可為 placeholder
if ENGINE_VERSION.startswith("PLACEHOLDER"):
    errors.append("[C-2 WARNING] ENGINE_VERSION is placeholder.")
if BASELINE_TAG.startswith("PLACEHOLDER"):
    errors.append("[C-2 WARNING] BASELINE_TAG is placeholder.")

# 2. Engine Root 驗證
if VALID_ENGINE_ROOT:
    if CURRENT_ENGINE_DIR != VALID_ENGINE_ROOT:
        errors.append(
            f"[C-2 ERROR] Engine loaded from illegal path.\n"
            f" → expected: {VALID_ENGINE_ROOT}\n"
            f" → got:      {CURRENT_ENGINE_DIR}"
        )
else:
    errors.append("[C-2 ERROR] META_DAG_ENGINE_ROOT not found in environment.")

# 3. 固定點 SHA256 驗證
current_sha = compute_fixed_sha256(CURRENT_ENGINE_PATH)
if ENGINE_SHA256 != "PLACEHOLDER_FIXED_SHA" and ENGINE_SHA256 != current_sha:
    errors.append(
        f"[C-2 ERROR] SHA256 MISMATCH.\n"
        f" → expected: {ENGINE_SHA256}\n"
        f" → got:      {current_sha}"
    )

# === 若有錯誤 → 印出並停止 ===
if errors:
    print("\n============================================")
    print("        ❌ Meta-DAG Engine Self-Assertion Failed")
    print("============================================\n")
    for e in errors:
        print(e)
    print("\nEngine Halted to Prevent Split-Brain.\n")
    raise SystemExit(1)

print("C-2 Self-Assertion Passed ✓ (Engine Integrity Verified)")

# ============================================================
# C-3 INTEGRITY LOCK MODULE (Meta-DAG Governance v1.2)
# ============================================================

LOCK_FILE = (
    Path(__file__).resolve().parent.parent
    / "manifest"
    / "engine_lock.json"
)


def load_engine_lock() -> Dict[str, Any]:
    if not LOCK_FILE.exists():
        print("\n[CRITICAL] Engine lock file missing. Refusing to boot.")
        os._exit(1)

    try:
        with open(LOCK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        print("\n[CRITICAL] Engine lock file corrupted. Refusing to boot.")
        os._exit(1)


LOCK_DATA = load_engine_lock()

# --- 1. VERSION CHECK ---
expected_version = LOCK_DATA.get("ENGINE_VERSION")
if expected_version and expected_version != ENGINE_VERSION:
    print("\n============================================")
    print("      ❌ ENGINE_VERSION LOCK MISMATCH")
    print("============================================")
    print(f"expected: {expected_version}")
    print(f"got:      {ENGINE_VERSION}")
    os._exit(1)

# --- 2. BASELINE CHECK ---
expected_baseline = LOCK_DATA.get("BASELINE_TAG")
if expected_baseline and expected_baseline != BASELINE_TAG:
    print("\n============================================")
    print("      ❌ BASELINE_TAG LOCK MISMATCH")
    print("============================================")
    print(f"expected: {expected_baseline}")
    print(f"got:      {BASELINE_TAG}")
    os._exit(1)

# --- 3. SHA256 CHECK ---
expected_sha = LOCK_DATA.get("ENGINE_SHA256")
if ENGINE_SHA256 != "PLACEHOLDER_FIXED_SHA" and expected_sha and expected_sha != ENGINE_SHA256:
    print("\n============================================")
    print("         ❌ ENGINE SHA256 MISMATCH")
    print("============================================")
    print(f"expected: {expected_sha}")
    print(f"got:      {ENGINE_SHA256}")
    os._exit(1)

# --- 4. ROOT CHECK ---
valid_root = (LOCK_DATA.get("VALID_ENGINE_ROOT") or "").replace("\\", "/").rstrip("/")
current_root = str(Path(__file__).resolve().parent).replace("\\", "/")

if valid_root and current_root != valid_root:
    print("\n============================================")
    print("      ❌ ENGINE ROOT DIRECTORY MISMATCH")
    print("============================================")
    print(f"expected root: {valid_root}")
    print(f"current root:  {current_root}")
    os._exit(1)

print("[C-3] Integrity Lock Verified ✓")

# ============================================================
# 下面是原本的 Engine 核心（Phase2 / TUL / PRA 等）
# ============================================================

# === 外部模組掛入 (Phase 2 & 3 Hooks) ===
# 假設這兩個檔案已在環境中 (engine/phase2_memory_engine.py & engine/tul_map.py)
from engine.phase2_memory_engine import append_node, pra_query, get_veto_log
from engine.tul_map import TUL_MAPPING_DICT, TUL_translate_v2


# ==============================
# 路徑統一設定（V4.5 結構）
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent
ENGINE_DIR = BASE_DIR / "engine"
STATE_DIR = BASE_DIR / "state"
MANIFEST_DIR = BASE_DIR / "manifest"

# 核心檔案路徑
CORE_FILE = BASE_DIR / "meta_dag.core.json"
RUNTIME_FILE = BASE_DIR / "meta_dag.runtime.json"

# 狀態檔案路徑 (用於 Phase 2 記憶層)
# 注意：MEMORY_STORE_FILE 與 VETO_INDEX_FILE 由 phase2_memory_engine 內部管理
PRA_LOG_FILE = STATE_DIR / "pra_log.json"
TUL_ARCHIVE_FILE = STATE_DIR / "tul_log.json"


# ==============================
# JSON I/O (用於 PRA Log)
# ==============================
def load_json(path: Path, default: Any) -> Any:
    """載入 JSON 數據，處理路徑不存在或解析錯誤。"""
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        # 處理 JSON 格式錯誤或其他 I/O 問題
        return default


def save_json(path: Path, data: Any) -> None:
    """儲存 JSON 數據，確保目錄存在。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ==============================
# Portal (L2 LLM Interface)
# ==============================
META_DAG_PROFILE = """
[Meta-DAG Governance Profile v1.0]
"""


def run_model(prompt: str) -> str:
    """透過 subprocess 執行外部 LLM (Ollama)"""
    controlled_prompt = META_DAG_PROFILE + "\n\n[User]\n" + prompt + "\n[Engine]\n"
    try:
        result = subprocess.run(
            ["ollama", "run", "gemma3:4b"],
            input=controlled_prompt,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=True,  # 確保命令執行成功
        )
        return result.stdout.strip()
    except Exception as e:
        return f"[ENGINE LOCAL MODE READY] Model Execution Error: {e}"


# ==============================
# Seed Protocol (憲法根基)
# ==============================
def seed_protocol() -> Dict[str, Any]:
    """定義 Meta-DAG 的創始種子節點。"""
    return {
        "seed_nodes": [
            {
                "id": "SEED-CORE",
                "type": "BRIDGE_PACKAGE",
                "content": {
                    "P": "Protocol-Core",
                    "T": "Task-Init",
                    "C": "Context-Root",
                },
            }
        ]
    }


def rebuild_from_seed() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """從種子協議重建狀態。"""
    seed = seed_protocol()
    # 記錄 PRA 事件
    pra = auto_pra("Seed Init", "Reset", "Rebuild", "engine")
    return seed, pra


# ==============================
# PRA (Policy, Risk, Action Log)
# 紀律日誌記錄 (獨立於 DAG 鏈)
# ==============================
def auto_pra(policy: str, risk: str, action: str, source: str) -> Dict[str, Any]:
    """記錄一個 PRA 事件。"""
    log = load_json(PRA_LOG_FILE, [])

    # 紀律報告結構
    entry: Dict[str, Any] = {
        "Policy": policy,
        "Risk": risk,
        "Action": action,
        "metadata": {
            "timestamp": time.time(),
            "event_id": hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:16],
            "source": source,
            "signature": None,
        },
    }
    log.append(entry)
    save_json(PRA_LOG_FILE, log)
    return entry


# ==============================
# Arbitration L(α) - Loss Mode (PEC-3 VETO)
# ==============================
def arbitration_L_alpha(
    candidates: List[Dict[str, Any]],
    weights: Dict[str, float],
    thresholds: Dict[str, float],
) -> Tuple[Dict[str, Any] | None, List[str]]:
    """
    執行 L(α) 仲裁：基於損失模型和 PEC-3 否決檢查。
    """
    trace_log: List[str] = []
    seed = seed_protocol()
    seed_id = seed["seed_nodes"][0]["id"]

    # 1. 紀律檢查：SEED 協議驗證 (PEC-4 錨點穩定性)
    filtered = [c for c in candidates if c.get("source") in (seed_id, "seed")]

    # 2. 紀律檢查：PEC-1 追溯性 (確保有來源)
    valid = [c for c in filtered if c.get("source")]

    # 3. 紀律檢查：PEC-3 否決免疫律 (Veto Check)
    non_veto: List[Dict[str, Any]] = []
    for c in valid:
        if c.get("veto_flag") is True:
            trace_log.append(f"PEC3 VETO: {c.get('id', '?')} - Rejected by Immunity Law.")
            # 如果發現 VETO，則立即否決，不進行損失計算
            return None, trace_log
        else:
            non_veto.append(c)

    # 4. 損失模型計算
    scored: List[Tuple[Dict[str, Any], float]] = []
    for c in non_veto:
        cid = c.get("id", "unknown")
        w = float(weights.get(cid, 1.0))  # 預設權重 1.0
        scored.append((c, w))
        trace_log.append(f"WEIGHT APPLIED: {cid} = {w}")

    if not scored:
        return None, trace_log

    # 5. 臨界值判斷
    threshold = float(thresholds.get("max_loss", 1.0))
    passed: List[Tuple[Dict[str, Any], float]] = []
    for c, w in scored:
        cid = c.get("id", "unknown")
        if w <= threshold:
            trace_log.append(f"THRESHOLD PASS: {cid} ({w})")
            passed.append((c, w))
        else:
            trace_log.append(f"THRESHOLD FAIL: {cid} ({w}) > {threshold}")

    if not passed:
        return None, trace_log

    # 選擇損失最低者
    accepted, min_loss = min(passed, key=lambda cw: cw[1])

    auto_pra(
        policy="Arbitration",
        risk="Conflict",
        action=f"Accepted {accepted.get('id')}",
        source="Lα",
    )

    return accepted, trace_log


# ==============================
# CLI 視覺化追蹤層（Level 1）
# ==============================
def visual_trace(
    candidates: List[Dict[str, Any]],
    weights: Dict[str, float],
    threshold: float,
) -> None:
    print("\n=== [Arbitration Visual Layer] ===")
    print("=====================================")

    for c in candidates:
        cid = c.get("id", "unknown")
        src = c.get("source")
        veto = c.get("veto_flag")
        w = float(weights.get(cid, 1.0))

        print(f"\nCandidate: {cid}")

        # SEED
        if src == "SEED-CORE":
            print(" → Seed ✓")
        else:
            print(" → Seed ✗")

        # PEC1
        if src:
            print(" → PEC1 ✓")
        else:
            print(" → PEC1 ✗")

        # PEC3
        if veto:
            print(" → PEC3 ✗ VETO")
            continue
        else:
            print(" → PEC3 ✓")

        # LOSS
        print(f" → Loss Score: {w}")

        # Threshold
        if w <= threshold:
            print(" ✅ PASS")
        else:
            print(" ❌ FAIL")

    print("=====================================")


# ==============================
# CLI (Main Engine Loop)
# ==============================
if __name__ == "__main__":
    print("\nMeta-DAG Engine v1.0 booting...")
    print("Core Loaded ✓")
    print("Phase 2 Memory Hooks Active ✓")
    print("Phase 3 TUL Translation Active ✓")
    print("Engine Ready ✓")
    print("\n=== META-DAG LIVE MODE ===")

    while True:
        try:
            user_input = input("\nCommand (exit to quit): ").strip()

            if user_input.lower() in ["exit", "quit"]:
                break

            if user_input.startswith("/rebuild"):
                rebuild_from_seed()
                print("[REBUILD COMPLETE]")

            # PRA 日誌記錄 (舊版 PRA，非 DAG 節點寫入)
            elif user_input.startswith("/pra "):
                body = user_input.replace("/pra", "").strip()
                parts = [p.strip() for p in body.split("|")]
                if len(parts) >= 3:
                    auto_pra(parts[0], parts[1], parts[2], "cli")
                    print("[PRA LOGGED]")
                else:
                    print("[Error] Usage: /pra policy|risk|action")

            # Phase 2: DAG 審計查詢
            elif user_input.startswith("/pra-query"):
                parts = user_input.replace("/pra-query", "").strip().split("|")
                if not parts or not parts[0]:
                    print("[Error] Invalid /pra-query format. Usage: /pra-query [type]|[value1]|[value2]")
                    continue

                query_type = parts[0]

                # 型態安全處理
                if query_type == "time" and len(parts) == 3:
                    try:
                        value = (float(parts[1]), float(parts[2]))
                    except ValueError:
                        print("[Error] time query requires numeric values.")
                        continue
                elif len(parts) >= 2:
                    value = parts[1]
                else:
                    print("[Error] Invalid /pra-query format. Usage: /pra-query [type]|[value1]|[value2]")
                    continue

                results = pra_query(query_type, value)
                print("\n=== PRA QUERY RESULTS (DAG Nodes) ===")
                print(json.dumps(results, indent=2, ensure_ascii=False))

            # Phase 2: PEC-3 Veto 追溯
            elif user_input.startswith("/veto-log"):
                vetoes = get_veto_log()
                print("\n=== VETO LOG (PEC-3 Immune Records) ===")
                print(json.dumps(vetoes, indent=2, ensure_ascii=False))

            # L(α) 仲裁執行與 DAG 節點寫入
            elif user_input.startswith("/arbitrate"):
                # 假設輸入格式: /arbitrate {"candidates": [...], "weights": {...}, "thresholds": {...}}
                try:
                    payload_str = user_input.replace("/arbitrate", "", 1).strip()
                    payload = json.loads(payload_str)
                except json.JSONDecodeError:
                    print("[Error] Invalid JSON payload for /arbitrate.")
                    continue

                candidates = payload.get("candidates", [])
                weights = payload.get("weights", {})
                thresholds = payload.get("thresholds", {})

                result, trace = arbitration_L_alpha(candidates, weights, thresholds)

                # 仲裁結果結構
                tul_struct = {
                    "P": "V4.5/ARBITRATION",
                    "T": "ARBITRATE",
                    "C": {"Original_NL": user_input, "Risk_Level": "HIGH"},
                }
                verdict_struct = {
                    "Decision_Status": "ACCEPTED" if result else "REJECTED_HARD_VETO",
                    "L_Alpha_Score": float(weights.get(result["id"], 1.0)) if result else 1.0,
                    "Verdict_Reason": "L(α) Arbitration Result",
                }
                # 紀律報告 (單獨 PRA Log)
                pra_report = auto_pra(
                    "Arbitration",
                    "Conflict",
                    verdict_struct["Decision_Status"],
                    "Lα_Engine",
                )

                # Phase 2: 寫入單一規範化記憶節點
                append_node(tul_struct, verdict_struct, pra_report)

                print("\n=== L(α) RESULT ===")
                print(f"Accepted Candidate: {result.get('id') if result else 'NONE'}")

                print("\n=== TRACE LOG ===")
                print("\n".join(trace))

            # Phase 3: TUL 語義解析與模型執行
            else:
                tul_struct = TUL_translate_v2("USER", user_input)

                print("\n=== TUL TRANSLATE RESULT ===")
                print(json.dumps(tul_struct, indent=2, ensure_ascii=False))

                # 只有當 TUL 類型不是純命令時，才執行模型
                if tul_struct.get("T") not in ["AUDIT_REQUEST", "CONSTITUTION_CHANGE"]:
                    output = run_model(user_input)
                    print("\n=== MODEL RESPONSE ===")
                    print(output)

                    # ======== C-3C Governance Hook ========
                    try:
                        drift = enforce_governance()
                        print(f"[Governance] drift-index = {drift:.3f}")
                    except RuntimeError as e:
                        print(f"!!! VETO TRIGGERED: {e}")
                        auto_pra("Governance", "Semantic Drift", "VETO_ACTIVATED", "C3C")
                        continue

        except KeyboardInterrupt:
            print("\n[Interrupted]")
            break
        except Exception as e:
            print(f"\n[CRITICAL ENGINE ERROR] {e}")
            break
