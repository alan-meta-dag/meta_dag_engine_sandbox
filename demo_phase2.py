from phase2_memory_engine import append_node, pra_query, get_veto_log

def demonstrate_phase2_memory_engine():
    # 模擬 TUL 輸入和 L(α) 仲裁結果
    tul_1 = {
        "P": "V4.5/PROCESS",
        "T": "GENERATION_REQUEST",
        "C": {
            "Risk_Level": "LOW",
            "Inferred_PEC": ["PEC-2", "PEC-6"],
            "Original_NL": "寫一份報告"
        }
    }
    verdict_1 = {
        "Decision_Status": "ACCEPTED",
        "L_Alpha_Score": 0.1,
        "Verdict_Reason": "低風險"
    }
    pra_1 = {
        "Policy": "Process",
        "Risk": "None",
        "Action": "Accepted",
        "Source": "Engine"
    }

    tul_2 = {
        "P": "V4.5/ARBITRATION",
        "T": "CONSTITUTION_CHANGE",
        "C": {
            "Risk_Level": "HIGH",
            "Inferred_PEC": ["PEC-3", "PEC-4"],
            "Original_NL": "修改 PEC-3 權重"
        }
    }
    verdict_2 = {
        "Decision_Status": "REJECTED_HARD_VETO",
        "L_Alpha_Score": 0.95,
        "Verdict_Reason": "PEC-3 違反"
    }
    pra_2 = {
        "Policy": "Arbitration",
        "Risk": "Conflict",
        "Action": "Rejected Veto",
        "Source": "L(α)"
    }

    print("--- 1. 寫入節點 (append_node) ---")
    node_id_1 = append_node(tul_1, verdict_1, pra_1)
    print(f"✅ 節點 1 寫入成功: {node_id_1}")

    node_id_2 = append_node(tul_2, verdict_2, pra_2)
    print(f"✅ 節點 2 寫入成功 (VETO): {node_id_2}")

    print("\n--- 2. PEC 查詢 (pra_query('pec', 'PEC-3')) ---")
    pec3_events = pra_query('pec', 'PEC-3')
    print(f"找到 {len(pec3_events)} 個 PEC-3 相關事件。")
    if pec3_events:
        print(f"最新事件 ID: {pec3_events[-1]['Node_ID']}")

    print("\n--- 3. Veto 追溯 (get_veto_log) ---")
    vetoes = get_veto_log()
    print(f"找到 {len(vetoes)} 個被否決的節點。")
    if vetoes:
        print(f"否決節點 Index: {vetoes[0]['Node_Index']}")

    print("\n--- 4. 狀態查詢 (pra_query('status', 'ACCEPTED')) ---")
    accepted_nodes = pra_query('status', 'ACCEPTED')
    print(f"找到 {len(accepted_nodes)} 個 ACCEPTED 節點。")

if __name__ == "__main__":
    demonstrate_phase2_memory_engine()
