# Meta-DAG Engine Baseline v1.1-XSTABLE

此封存為 **Meta-DAG Engine** 在完成「2000 句 X 級壓力測試」後，
由 sandbox 專案中的 engine 目錄建立的「穩定可重建」基準版本。

## 來源 (Source)
- Source Root (sandbox): `D:\AlanProjects\meta_dag_engine_sandbox`
- 狀態：TUL + Phase2 Memory + Phase4 Collab 已通過壓力測試

## 內容 (Included Files)
- `engine/engine_v2.py`
    - SHA256: `ea9650fe4b1463d697045a0c9ad7ec2019d38848c96aa9be632e882660893a8e`
- `engine/phase2_memory_engine.py`
    - SHA256: `8f5652229ae80c24c9e93ea233819ada7f1c16bdc24876ed395740de87b478b1`
- `engine/phase4_collab.py`
    - SHA256: `1d5cb24d17a501f094bbc0f328a647576c66a66286e3bb41e901738c2e717b52`
- `engine/tul_map.py`
    - SHA256: `ba676154106f81e14be702e2e477ed06ec3e15f6c78017eab61327f01a31e20f`

## 用途 (Usage)
1. 當作未來任何版本的 **重建起點 (baseline)**。
2. 如遇到殘影 / 污染懷疑時，可以直接從此 baseline 重置 engine 模組。
3. 正式壓力測試與治理設計可標記為：
   - `engine_baseline=v1.1-XSTABLE`。
