# Meta-DAG 真引擎壓力測試入口（Minimum Viable Version）

本壓力測試腳本 **直接 import 真引擎 `engine_v2.py`**，  
不透過 HTTP API / FastAPI / dummy server。

根目錄：`D:\AlanProjects\meta_dag_engine_sandbox\`

## Import Target

```python
from engine_v2 import run_model
本專案在 tests/pressure_test_runner.py 中會：

將專案根目錄加入 sys.path

直接 import engine_v2

呼叫 run_model(user_input: str) 進行壓力測試

在 sandbox 的 state/, memory/, logs/ 上觀察變化（僅 read，不做破壞性寫入）

壓力測試階段（T1 / T2 / T3）

壓測入口檔案：tests/pressure_test_runner.py

T1：煙霧測試 Smoke (50)

指令：py tests\pressure_test_runner.py --stage smoke

測試數量：50 筆

目的：

確認 run_model() 可被穩定呼叫

測試輸入 / 輸出記錄功能

確認 state/memory/log 變更偵測流程正常

T2：耐力測試 Endurance (800)

指令：py tests\pressure_test_runner.py --stage endurance

測試數量：約 800 筆

每 100 筆會記錄一次 state/memory/log 快照摘要

目的：

測引擎在中等壓力下是否保持穩定

觀察 state/memory/log 是否有異常成長或結構變化

T3：終極壓力測試 Final (5000)

指令：py tests\pressure_test_runner.py --stage final

測試數量：約 5000 筆

每 500 筆記錄一次 state/memory/log 快照摘要

僅在 T1 + T2 完全通過後執行

目的：

測量長時間高壓下的穩定性與「零汙染」能力

也可以一次跑完三個階段：

py tests\pressure_test_runner.py --stage all

輸出結果

所有壓測結果會輸出到：

tests/pressure_reports/pressure_report_YYYYMMDDTHHMMSSZ.json

tests/pressure_reports/pressure_report_YYYYMMDDTHHMMSSZ.md

JSON 內容包括：

engine_available: 是否成功 import 真引擎

stage_results: 每個階段（smoke / endurance / final）的：

測試次數

成功 / 失敗統計

平均/最大延遲

state/memory/log 是否有變化（摘要）

Markdown 內容是 JSON 的可讀版摘要，可直接提供給審核者或外部合作方。

安全性說明（Sandbox 限定）

壓測程式只在 D:\AlanProjects\meta_dag_engine_sandbox\ 執行

不會訪問 meta_dag_engine\ 正式目錄

對 state/, memory/, logs/ 只做「讀取 + 摘要」，不做破壞性寫入

若無法成功 import 真引擎，報告會標註 engine_available = false，不會強制執行

備註

本壓測入口為 Minimum Viable Version，以「簡單、可審計、可重現」為優先。

若未來治理規範補充 rollback / 汙染偵測規則，可在此基礎上擴充：

將 state 差異餵入 contamination_detector

根據 rollback_policy.yaml 決定是否觸發復原。