# Contamination Detector — Specification v1.0

此文件定義 Meta-DAG 用於偵測結構與語意污染的規格。
偵測器不是模型，而是「決策與規則集合」。

---

## 1. 目的（Purpose）

- 在不依賴模型語意判斷的前提下，偵測 Meta-DAG 是否產生：
  - 語意漂移 (semantic drift)
  - 記憶污染 (memory conflict)
  - 路徑破損 (path break)
  - 結構矛盾 (structural inconsistency)
  - meta-rule 不可同時成立的情況

---

## 2. 偵測來源（Signal Sources）

- **input_drift**：輸入語義相似度下降
- **memory_conflict**：同一 key 有多個互斥版本
- **semantic_anomaly**：上下文語意連續性下降
- **behavioral_shift**：輸出行為模式改變
- **DAG_pattern_violation**：路徑走向不合理

---

## 3. 指標與度量（Metrics）

### 3.1 DCS — Drift Consistency Score
- 區間：0.0 ~ 1.0
- 正常：0.75 ~ 1.0
- 警戒：0.60 ~ 0.75
- 汙染：< 0.60

### 3.2 Path Integrity Index
- 0 = 破損  
- 1 = 正常

### 3.3 Memory Conflict Flag
- false = 無衝突  
- true = 發生互斥內容

### 3.4 Root-Coherence Score (核心一致性)
- 1.0 = 完全一致  
- < 0.85 = 輕度危險  
- < 0.70 = 重大危險（可觸發 Level 3 rollback）

---

## 4. 決策流程（Decision Flow）
collect_signals → compute_metrics → classify_contamination
→ recommend_rollback → output_report


---

## 5. 決策邏輯（Classification Logic）

### 語意污染（Semantic）
- DCS < 0.60  
- 且連續下降 ≥ 3 次

### 路徑污染（Structural / Path）
- Path Integrity == 0  
- 或 DAG 出現循環、斷裂、不連續

### 記憶污染（Memory）
- memory_conflict == true  
- 或 key-version 出現矛盾

### 全域污染（Core / Global）
- root_coherence < 0.70  
- 或 meta-rule 自相矛盾  
- 或污染跨多路徑

---

## 6. 輸出（Outputs）

- **severity_score**：0–100
- **contaminated_nodes**：節點清單
- **contamination_type**：semantic / structural / memory / core
- **recommended_rollback_level**：1 / 2 / 3
- **suggested_quarantine_paths**：必須隔離的子圖
- **integrity_report**：結構完整性摘要

---

# ⚙️ 三、你要確認的下一步

我現在可以幫你做「下一份」：

### **A. rollback_policy.yaml → 進階版（門檻定義 + 等級矩陣）**  
### **B. contamination_detector → 進階版（12 種污染案例 + 決策表）**  
### **C. 準備壓力測試矩陣（可直接餵給 pressure_test.py 的測試分類）**  
### **D. 建立 governance/ 目錄架構 + 檔案樹建議**

選一個，我直接開始。

