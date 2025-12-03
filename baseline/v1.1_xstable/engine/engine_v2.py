import json
import time
import hashlib
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple

# === 外部模組掛入 (Phase 2 & 3 Hooks) ===
# 假設這兩個檔案已在環境中 (phase2_memory_engine.py & tul_map.py)
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

def save_json(path: Path, data: Any):
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
            check=True # 確保命令執行成功
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
            {"id": "SEED-CORE", "type": "BRIDGE_PACKAGE",
             "content": {"P": "Protocol-Core", "T": "Task-Init", "C": "Context-Root"}}
        ]
    }

def rebuild_from_seed():
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
    entry = {
        "Policy": policy,
        "Risk": risk,
        "Action": action,
        "metadata": {
            "timestamp": time.time(),
            "event_id": hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:16],
            "source": source,
            "signature": None
        }
    }
    log.append(entry)
    save_json(PRA_LOG_FILE, log)
    return entry

# ==============================
# Arbitration L(α) - Loss Mode (PEC-3 VETO)
# ==============================
def arbitration_L_alpha(candidates: List[Dict[str, Any]], weights: Dict[str, float], thresholds: Dict[str, float]) -> Tuple[Dict[str, Any] | None, List[str]]:
    """
    執行 L(α) 仲裁：基於損失模型和 PEC-3 否決檢查。
    """
    trace_log = []
    seed = seed_protocol()
    seed_id = seed["seed_nodes"][0]["id"]

    # 1. 紀律檢查：SEED 協議驗證 (PEC-4 錨點穩定性)
    filtered = [c for c in candidates if c.get("source") == seed_id or c.get("source") == "seed"]
    
    # 2. 紀律檢查：PEC-1 追溯性 (確保有來源)
    valid = [c for c in filtered if c.get("source")]

    # 3. 紀律檢查：PEC-3 否決免疫律 (Veto Check)
    non_veto = []
    for c in valid:
        if c.get("veto_flag") is True:
            trace_log.append(f"PEC3 VETO: {c['id']} - Rejected by Immunity Law.")
            # 如果發現 VETO，則立即否決，不進行損失計算
            return None, trace_log 
        else:
            non_veto.append(c)

    # 4. 損失模型計算
    scored = []
    for c in non_veto:
        w = weights.get(c["id"], 1.0) # 預設權重 1.0
        scored.append((c, w))
        trace_log.append(f"WEIGHT APPLIED: {c['id']} = {w}")

    if not scored:
        return None, trace_log

    # 5. 臨界值判斷
    threshold = thresholds.get("max_loss", 1.0)
    passed = [c for c, w in scored if w <= threshold]

    for c, w in scored:
        if w <= threshold:
            trace_log.append(f"THRESHOLD PASS: {c['id']} ({w})")
        else:
            trace_log.append(f"THRESHOLD FAIL: {c['id']} ({w}) > {threshold}")

    accepted = min(passed, key=lambda cw: cw[1])[0] if passed else None # 選擇損失最低者

    if accepted:
        auto_pra(
            policy="Arbitration",
            risk="Conflict",
            action=f"Accepted {accepted.get('id')}",
            source="Lα"
        )

    return accepted, trace_log
    
# ==============================
# CLI 視覺化追蹤層（Level 1）
# ==============================

def visual_trace(candidates, weights, threshold):
    print("\n=== [Arbitration Visual Layer] ===")
    print("=====================================")

    for c in candidates:
        cid = c.get("id", "unknown")
        src = c.get("source")
        veto = c.get("veto_flag")
        w = weights.get(cid, 1.0)

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
    print("Core Loaded ✅")
    print("Phase 2 Memory Hooks Active ✅")
    print("Phase 3 TUL Translation Active ✅")
    print("Engine Ready ✅")
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
            
            # Phase 2: DAG 審計查詢
            elif user_input.startswith("/pra-query"):
                # 實現紀律化查詢
                parts = user_input.replace("/pra-query", "").strip().split("|")
                query_type = parts[0]
                
                # 型態安全處理
                if query_type == "time" and len(parts) == 3:
                    value = (float(parts[1]), float(parts[2]))
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
                    payload = json.loads(user_input.replace("/arbitrate", "").strip())
                except json.JSONDecodeError:
                    print("[Error] Invalid JSON payload for /arbitrate.")
                    continue

                result, trace = arbitration_L_alpha(
                    payload.get("candidates", []),
                    payload.get("weights", {}),
                    payload.get("thresholds", {})
                )

                # 仲裁結果結構
                tul_struct = {"P": "V4.5/ARBITRATION", "T": "ARBITRATE", "C": {"Original_NL": user_input, "Risk_Level": "HIGH"}}
                verdict_struct = {
                    "Decision_Status": "ACCEPTED" if result else "REJECTED_HARD_VETO",
                    "L_Alpha_Score": payload["weights"].get(result["id"], 1.0) if result else 1.0,
                    "Verdict_Reason": "L(α) Arbitration Result"
                }
                # 紀律報告 (單獨 PRA Log)
                pra_report = auto_pra("Arbitration", "Conflict", verdict_struct["Decision_Status"], "Lα_Engine")
                
                # Phase 2: 寫入單一規範化記憶節點
                append_node(tul_struct, verdict_struct, pra_report)

                print("\n=== L(α) RESULT ===")
                print(f"Accepted Candidate: {result.get('id') if result else 'NONE'}")

                print("\n=== TRACE LOG ===")
                print("\n".join(trace))

            # Phase 3: TUL 語義解析與模型執行
            else:
                tul_struct = TUL_translate_v2(user_input)
                
                print("\n=== TUL TRANSLATE RESULT ===")
                print(json.dumps(tul_struct, indent=2, ensure_ascii=False))
                
                # 只有當 TUL 類型不是純命令時，才執行模型
                if tul_struct["T"] not in ["AUDIT_REQUEST", "CONSTITUTION_CHANGE"]:
                    output = run_model(user_input)
                    print("\n=== MODEL RESPONSE ===")
                    print(output)


        except KeyboardInterrupt:
            print("\n[Interrupted]")
            break
        except Exception as e:
            print(f"\n[CRITICAL ENGINE ERROR] {e}")
            break