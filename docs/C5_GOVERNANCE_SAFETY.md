"Meta-DAG Compliance & Safety Policy" 
powershell -Command ^
"@'
# Meta-DAG Compliance & Safety Policy (Public)

Version: C-5.1 (Public Release)
Maintainer: Alan
Applies to: Meta-DAG Engine Public Edition

## 1. Purpose & Scope
此政策適用於公開 GitHub 版本，確保合法、安全、合規運作。

## 2. Legal & Ethical Commitments
- 只使用 **對齊模型 (Aligned Models)**
- 禁止協助違法與危害性內容
- **兒童保護機制為最高優先**
- 所有資料與模型存取受審計控管

## 3. Restricted-Model Governance
具審查繞過能力的模型：
- 僅限私人研究使用
- 不提供載點與使用指南
- 開機需 Research Key
- 所有風險行為由使用者承擔

## 4. Audit Transparency
- Engine 所有決策具審計紀錄
- 治理邏輯版本與異動可追溯
- 所有公開版本均經 Tag 標示

## 5. Developer Liability
本專案目的為研究治理
使用者須遵守法律與安全規範
嚴禁用於犯罪與人身危害

> 工具中立，使用者負責

## 6. Release Classification Matrix

| Class | 模型可用性 | 用途 | 法律狀態 |
|------|------------|------|---------|
| **L1 Public Edition** | Aligned Only | GitHub 發行 | ✔ 安全 |
| **L2 Research Mode** | Restricted Model | 私有研究 | ⚠ 需審慎 |
| (L3 強制封鎖)** | Unfiltered models | 禁止散佈 | ❌ 不會公開 |

'@ | Set-Content docs/C5_GOVERNANCE_SAFETY.md -Encoding UTF8"
