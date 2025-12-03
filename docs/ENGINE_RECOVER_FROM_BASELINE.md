# 📄 **ENGINE_RECOVER_FROM_BASELINE.md（標準版）**

**Meta-DAG Engine — Baseline Recovery Manual（Standard Edition）**
Version: **v1.0-standard**
Applicable Paths:

* `D:/AlanProjects/meta_dag_engine_sandbox/`
* `D:/AlanProjects/meta_dag_engine/`

---

# 1. 🎯 Recovery 的適用情況（什麼時候要執行）

### 在以下情況必須進行 baseline recovery：

1. 壓力測試後（尤其是 500+ / 2000+ case）
2. 發現 SHA256 不一致 / contamination_detector 警告
3. sandbox 中的 `engine/` 出現額外檔案（Final、old、v0.9…）
4. 模組 import 錯誤（例如：phase2 找不到、tul_map mismatch）
5. GPT 出現殘影症狀（回覆不穩定、模組調用錯誤）
6. baseline builder 執行後，準備做新一輪調整或壓測

---

# 2. 🧼 Recovery 流程（5 steps）

以下流程 **只動 sandbox**（因為 formal 你目前保持乾淨）。

---

## **STEP 1 — 清理 engine/ 目錄與殘影**

執行：

```
del /F /Q engine\*.old
del /F /Q engine\*v0*
del /F /Q engine\engine_v2_Final.py
rmdir /S /Q engine\__pycache__
```

（不用怕誤刪，baseline 會覆蓋回來）

---

## **STEP 2 — 用 baseline 覆蓋 engine/**

執行：

```
py recover_engine.py
```

你剛才已經成功執行一次，結果：

```
[COPY] engine_v2.py
[COPY] phase2_memory_engine.py
[COPY] phase4_collab.py
[COPY] tul_map.py
[DONE] SANDBOX RECOVERED OK
```

---

## **STEP 3 — 用 SHA256 再驗證（一定要做）**

PowerShell 執行：

```powershell
$code = @"
import hashlib, pathlib, json

ROOT = pathlib.Path(r"D:/AlanProjects/meta_dag_engine_sandbox")
BASE = ROOT / "baseline" / "v1.1_xstable" / "engine"
TARGET = ROOT / "engine"

def sha256(p):
    return hashlib.sha256(open(p,'rb').read()).hexdigest()

report = {}

for name in ["engine_v2.py","phase2_memory_engine.py","phase4_collab.py","tul_map.py"]:
    b = BASE / name
    t = TARGET / name
    report[name] = {
        "baseline": sha256(b),
        "engine": sha256(t)
    }

print(json.dumps(report, indent=2))
"@

py -c $code
```

你剛執行結果 **已完全一致**：

```
engine_v2.py → MATCH
phase2_memory_engine.py → MATCH
phase4_collab.py → MATCH
tul_map.py → MATCH
```

✔ 表示已完全乾淨。

---

## **STEP 4 — 啟動一次 live mode 確認 import 正常**

```
py run_engine.py
```

預期畫面：

```
Core Loaded
Phase2 Memory Hooks Active
Phase3 TUL Translation Active
Engine Ready
=== META-DAG LIVE MODE ===
```

如正常 → 引擎可運作。

---

## **STEP 5 — 執行一次 smoke test（短測）**

```
py tests/pressure_test_tul_short.py
```

預期結果應如你剛剛的：

```
[OK] 引擎載入成功
[... verdict = None]
[DONE] TUL Short Stress Test Finished.
```

---

# 3. 📦 Baseline Recovery 完成後要做什麼？

### **（A）準備正式進入下一輪壓力測試**

可以直接跑：

```
py tests/attack_test.py
```

### **（B）要開始開發新的引擎功能**

→ 建議先建立：

```
baseline/v1.2_dev
```

不動 v1.1_xstable。

### **（C）要回到正式引擎（formal project）**

sandbox 驗證完全乾淨後，再同步到 formal。

---

# 4. 🚫 避免再次污染的固定規則（超重要）

以下是 **不變的 Meta-DAG 引擎治理原則**：

### 1. sandbox 與 formal 永不互相 import

只同步 baseline，不 copy random file。

### 2. live mode 只能在 sandbox 啟動

formal 是封存層，不能跑互動。

### 3. 所有新功能先在 sandbox 進行壓測

壓測通過後 → baseline builder → 再進 formal。

### 4. engine/ 下只允許 **4 個檔案 + init.py**

* engine_v2.py
* phase2_memory_engine.py
* phase4_collab.py
* tul_map.py
* **init**.py

其他一律殘影 → 刪。

### 5. 每做一次大測試後，一律 baseline recover

讓 contamination 永遠無法累積。

---

# 5. 📁 本文件如何使用？

你可以把它存成：

```
docs/ENGINE_RECOVER_FROM_BASELINE.md
```

每次：

* 測試後
* 引擎怪怪的時候
* GPT 行為偏移的時候
  → 就照這份文件重跑一次。

---

# 全部完成 ✔️

你要我直接輸出成 **真正的 md 檔（可貼進 VSCode）** 嗎？
或是你要加入你自己的語氣/備註版本？
