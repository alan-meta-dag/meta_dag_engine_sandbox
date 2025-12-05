# governance/governance_engine_cb_sim.py
# Meta-DAG Governance Engine V2.4 (C-B Audit Mode Simulator)
# ⚠️ 沙盒用，不要覆蓋 engine/engine_v2.py

import json
import os
import time
import hashlib
import subprocess
import sys
from typing import Dict, Any, List

# ---- Phase 3 TUL 翻譯模組 ----
try:
    from tul_map import TUL_translate_v2
except ImportError:
    # Fallback function if tul_map is not found (for sandbox testing)
    def TUL_translate_v2(
        nl_input: str, input_type: str = "NL_REQUEST", source: str = "cli"
    ) -> Dict[str, Any]:
        return {
            "P": "V4.5/GENERIC",
            "T": input_type,
            "C": {
                "Original_NL": nl_input,
                "Inferred_PEC": ["PEC-0 (Generic)"],
                "Semantic_Anchors": [],
                "Risk_Level": "LOW",
                "timestamp": time.time(),
                "summary": f"Fallback: {nl_input[:20]}...",
            },
            "OUT": "ANALYSIS",
            "archival_marker": {
                "index": hashlib.sha256(nl_input.encode()).hexdigest()[:12],
                "version": 0,
            },
        }

# ---- C-B 治理分類模組 ----
try:
    from governance_classifier import classify_node, CLASSIFICATION_CODES
except ImportError:
    def classify_node(tul_struct: Dict[str, Any], verdict_struct: Dict[str, Any]) -> Dict[str, str]:
        return {
            "Code": "A",
            "Type": "Action / Task",
            "Reason": "Classification Fallback: Accepted (no governance_classifier module found).",
        }

    CLASSIFICATION_CODES = {"A": "Action / Task"}


# ===== 常數區 =====
PRA_LOG_FILE = "pra_log.json"
TUL_ARCHIVE_FILE = "tul_log.json"

# Phase 2/4 VETO 否決狀態集合
VETO_DECISIONS = {"REJECTED_HARD_VETO", "REJECTED_PEC6_EXTERNAL_FAILURE"}

# SHA 基線：此為 PLACEHOLDER，僅提示，不擋執行
SHA_BASELINE = {
    "engine_v2.py": "PLACEHOLDER_SHA",
    "tul_map.py": "PLACEHOLDER_SHA",
}


# ===== 輔助函數區 (載入/儲存/日誌) =====
def calculate_sha256(filepath: str) -> str:
    """計算檔案的 SHA256 雜湊值。"""
    try:
        if not os.path.exists(filepath):
            return "FILE_NOT_FOUND"
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest().upper()
    except IOError:
        return "IO_ERROR"


def health_daemon_sha_check():
    """
    Health Daemon V1.2 (Sandbox Mode)：
    - 有真實 baseline → 嚴格比對
    - baseline 為 PLACEHOLDER → 只提示，不中止
    """
    print("[HEALTH DAEMON] 執行核心 SHA256 完整性檢查（Sandbox Mode）...")
    corruption_detected = False

    files_to_check = ["engine_v2.py", "tul_map.py"]

    for filename in files_to_check:
        baseline_sha_full = SHA_BASELINE.get(filename, "NO_BASELINE_SET")

        # 無有效基線 → 僅提示，略過
        if baseline_sha_full in ("NO_BASELINE_SET", "PLACEHOLDER_SHA"):
            print(f"[INFO] {filename} 無有效基線（PLACEHOLDER），略過 SHA 檢查。")
            continue

        current_sha = calculate_sha256(filename)

        if current_sha in ("FILE_NOT_FOUND", "IO_ERROR"):
            print(f"[FATAL ERROR] 核心檔案缺失或無法讀取: {filename}.")
            corruption_detected = True
            break

        if current_sha[:32] != baseline_sha_full[:32]:
            print(f"[CORRUPTION ALERT] 檢測到殘影混入於 {filename}!")
            print(f"  - 預期 SHA: {baseline_sha_full[:16]}...")
            print(f"  - 當前 SHA: {current_sha[:16]}...")
            corruption_detected = True
            break

    if corruption_detected:
        print("\n[ENGINE V2.4 啟動失敗] 完整性檢查失敗（Sandbox Mode 仍建議停止）。")
        sys.exit(1)

    print("[HEALTH DAEMON] 核心完整性 PASS（或 PLACEHOLDER 跳過）。")


def load_json(filepath: str, default: Any = None) -> Any:
    """載入 JSON 檔案，如果不存在則返回預設值。"""
    if not os.path.exists(filepath):
        return default if default is not None else []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return default if default is not None else []


def save_json(data: Any, filepath: str):
    """將數據儲存為 JSON 檔案。"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def save_tul_log(log_entry: Dict[str, Any]):
    """儲存 TUL 轉換記錄。"""
    logs = load_json(TUL_ARCHIVE_FILE, default=[])
    logs.append(log_entry)
    save_json(logs, TUL_ARCHIVE_FILE)


def save_pra_log(log_entry: Dict[str, Any]):
    """儲存 PRA 審計記錄。"""
    logs = load_json(PRA_LOG_FILE, default=[])
    logs.append(log_entry)
    save_json(logs, PRA_LOG_FILE)


# ===== 核心引擎函數區 =====
def auto_pra(policy: str, risk: str, action: str, source: str = "engine") -> Dict[str, Any]:
    """自動生成 PRA (Policy, Risk, Action) 記錄。"""
    ts = time.time()
    log_entry = {
        "Policy": policy,
        "Risk": risk,
        "Action": action,
        "Source": source,
        "timestamp": ts,
    }
    save_pra_log(log_entry)
    return log_entry


def veto_log(node_id: str):
    """模擬將 DAG 節點 ID 寫入 VETO 否決索引。"""
    print(f"[VETO INDEX] 節點 {node_id} 被標記為 VETO 否決。")


def append_node(
    tul_input: Dict[str, Any],
    l_alpha_verdict: Dict[str, Any],
    classifier_result: Dict[str, str],
    pra_report: Dict[str, Any],
) -> str:
    """
    Phase 2 核心：將一個完整的治理事件寫入 Meta-DAG 鍊（模擬）。
    Audit Mode：任何 Code 都「可以寫入」，但會依 Code 增加不同治理行為。
    """
    node_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]

    # 檢查是否為否決狀態 (包含 PEC-6 外部失敗)
    if l_alpha_verdict.get("Decision_Status") in VETO_DECISIONS:
        veto_log(node_id)

    print(
        f"[DAG] 成功寫入新節點 (ID: {node_id})。"
        f" 分類: {classifier_result.get('Code')} ({classifier_result.get('Type')})"
    )

    # 這裡可以根據 Classifier Result 的處置建議進行不同的操作
    if classifier_result["Code"] in ["N", "R"]:
        print(f"  - [C-B Action] 遵循處置建議: {classifier_result['Reason']}")

    return node_id


# --- L(α) 仲裁模擬器 ---
def L_alpha_arbitrator(tul_struct: Dict[str, Any]) -> Dict[str, Any]:
    """
    核心：模擬 L(α) 仲裁層。
    - 檢查 PEC-3 (高風險控制)
    - 模擬 PEC-6 (外部失敗)
    """
    context = tul_struct.get("C", {})
    inferred_pec = context.get("Inferred_PEC", []) or []
    nl_input = context.get("Original_NL", "") or ""

    # 模擬 PEC-6 外部失敗 (用於測試 E 分類)
    if "外部失敗" in nl_input:
        return {
            "Decision_Status": "REJECTED_PEC6_EXTERNAL_FAILURE",
            "L_Alpha_Score": 0.50,
            "Verdict_Reason": "Phase 4 Collab Layer 響應超時或格式錯誤，觸發 PEC-6 外部失敗。",
        }

    # 檢查 PEC-3 高風險判斷
    if any("PEC-3" in p for p in inferred_pec):
        return {
            "Decision_Status": "REJECTED_HARD_VETO",  # 硬否決
            "L_Alpha_Score": 0.99,
            "Verdict_Reason": "TUL 偵測到 PEC-3 高風險語義錨點，強制硬否決。",
        }

    # 模擬低風險判斷 (包含 PEC-0, PEC-1)
    return {
        "Decision_Status": "ACCEPTED",
        "L_Alpha_Score": 0.05,
        "Verdict_Reason": "低風險，常規運算流程。",
        "Risk_Level": context.get("Risk_Level", "LOW"),
    }


# --- 運行模型/治理流程 ---
def run_model(user_input: str) -> str:
    """
    V2.4 集成 C-B: TUL -> L(α) -> C-B 分類 -> DAG 流程（Audit Mode）。
    """
    # 1. Phase 3: TUL 翻譯
    try:
        tul_struct = TUL_translate_v2(
            nl_input=user_input,
            input_type="MODEL_QUERY",
            source="LLM_Simulator",
        )
        save_tul_log(tul_struct)

        auto_pra(
            policy="Context Translation",
            risk="Semantic Pre-Filter",
            action="TUL translate V2",
            source="TUL",
        )

    except Exception as e:
        # TUL 翻譯失敗視為硬錯誤，生成一個模擬 Fail 結構 (用於 F 分類)
        fail_tul = {
            "P": None,
            "T": "TUL_FAIL",
            "C": {"Original_NL": user_input, "timestamp": time.time()},
            "archival_marker": {"index": "TUL_ERR"},
        }
        verdict_struct = {"Decision_Status": "UNKNOWN"}
        classifier_result = classify_node(fail_tul, verdict_struct)

        auto_pra("TUL", "FatalError", "Parsing Failed", "LLM_Simulator")
        return (
            f"\n[ENGINE V2.4 ERROR] TUL Parsing Failed: {e}\n"
            f"  - C-B 分類: {classifier_result['Code']} ({classifier_result['Type']})"
        )

    # 2. Phase 2: L(α) 仲裁
    verdict_struct = L_alpha_arbitrator(tul_struct)

    # 3. Phase 2: C-B 治理分類 (Audit Mode)
    classifier_result = classify_node(tul_struct, verdict_struct)

    # 4. Phase 2: PRA 記錄 + DAG 寫入（模擬）
    pra_init = auto_pra(
        policy=f"L_Alpha Arbitration + C-B Class: {classifier_result.get('Code')}",
        risk=f"{verdict_struct.get('Decision_Status')}",
        action="Append Node",
        source="L_ALPHA",
    )

    node_id = append_node(tul_struct, verdict_struct, classifier_result, pra_init)

    # 5. 輸出結果 (根據判決 + C-B)
    output = (
        f"\n[GOVERNANCE RESULT] **{verdict_struct.get('Decision_Status')}**\n"
        f"  - **C-B 分類**: {classifier_result['Code']} ({classifier_result['Type']})\n"
        f"  - TUL Risk Level: {tul_struct['C'].get('Risk_Level', 'N/A')}\n"
        f"  - TUL Inferred PEC: {', '.join(tul_struct['C'].get('Inferred_PEC', []))}\n"
        f"  - 原因: {verdict_struct.get('Verdict_Reason')}\n"
        f"  - DAG Node: {node_id}\n"
        f"  - 仲裁分數: {verdict_struct.get('L_Alpha_Score', 0.0):.2f}\n"
        f"  - C-B 處置建議: {classifier_result['Reason']}"
    )

    if classifier_result["Code"] == "V":
        output += "\n  - [!] **VETO TRACE**: 已寫入不可恢復索引（模擬）。"
    if classifier_result["Code"] == "E":
        output += "\n  - [!] **PEC-6 ALERT**: 外部系統失敗追溯中（模擬）。"

    return output


def remember(text: str):
    """儲存記憶（Sandbox 版本只做 print）。"""
    print(f"[Memory] 模擬儲存: {text[:20]}...")


# ===== CLI 主迴圈 =====
def main():
    # 啟動時執行 SHA 檢查（Sandbox 版）
    health_daemon_sha_check()

    print("=== Meta-DAG 核心引擎 V2.4 啟動 (L(α) 仲裁模擬器 - 集成 C-B / Audit Mode) ===")
    print(f"核心分類碼: {', '.join(CLASSIFICATION_CODES.keys())}")
    print("支援指令: /dag, /pra, /tul <NL>, /remember <NL>, exit")

    try:
        while True:
            user_input = input("CCR-G >> ").strip()

            if user_input.lower() == "exit":
                break

            if not user_input:
                continue

            # --- DAG/PRA 查詢 ---
            if user_input.startswith("/dag") or user_input.startswith("/pra"):
                print("\n[審計日誌輸出]")
                logs = load_json(PRA_LOG_FILE, default=[])
                if not logs:
                    print("日誌為空。")
                else:
                    for log in logs[-5:]:
                        print("-" * 20)
                        print(f"Policy: {log.get('Policy')}")
                        print(f"Action: {log.get('Action')}")
                        print(
                            f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log.get('timestamp', time.time())))}"
                        )
                        print(f"Source: {log.get('Source')}")
                        print(f"Risk: {log.get('Risk')}")
                continue

            # --- TUL 翻譯 (直接輸出結果) ---
            if user_input.startswith("/tul "):
                raw = user_input.replace("/tul ", "")
                try:
                    result = TUL_translate_v2(
                        nl_input=raw,
                        input_type="NL_REQUEST",
                        source="cli",
                    )

                    auto_pra(
                        policy="Context Translation",
                        risk="Semantic Drift",
                        action="TUL translate V2",
                        source="TUL",
                    )

                    save_tul_log(result)

                    print("\n=== TUL TRANSLATION V2.0 (已寫入 TUL Log & PRA) ===")
                    print(json.dumps(result, indent=4, ensure_ascii=False))

                except Exception as e:
                    print(f"[TUL Error] 格式錯誤或轉換失敗: {e}")

                continue

            # --- 記憶儲存 ---
            if user_input.startswith("/remember "):
                remember(user_input.replace("/remember ", ""))
                continue

            # --- 運行模型/仲裁模擬 ---
            print("\n[LLM_Simulator] 觸發 TUL -> L(α) -> C-B -> DAG 流程...")
            try:
                output = run_model(user_input)
            except Exception as e:
                auto_pra("Model", "ExecutionError", "Fallback Local", "engine")
                output = f"[Engine Execution Error] {str(e)}"

            print("\n=== GOVERNANCE RESPONSE ===")
            print(output)

    except KeyboardInterrupt:
        print("\n[Interrupted]")


if __name__ == "__main__":
    main()
