# 記憶模組與 Meta‑DAG 交互接口契約（完整版）

## 1. 核心設計原則
- **松耦合**：透過抽象接口（如 `INarrativeEventSender`）定義交互邊界。  
- **契約優先**：數據格式、錯誤碼、加密方式均在此明確約定。  
- **向前兼容**：所有接口需支持版本化，允許新舊版本共存和平滑遷移。  

---

## 2. 核心 API 與接口設計

### 2.1 記憶模組對外提供的能力 (Core APIs)
```python
class MemoryManager:
    API_VERSION = "1.0"
    
    def retrieve_relevant_memories(self, query: Dict[str, Any], api_version: str = API_VERSION) -> List[Dict[str, Any]]:
        """結構化查詢，支持 keywords, event_types, time_range, severity"""
        pass
    
    def log_system_event(self, event: Dict[str, Any], api_version: str = API_VERSION) -> str:
        """單條事件記錄"""
        pass
    
    def log_system_events_batch(self, events: List[Dict[str, Any]], api_version: str = API_VERSION) -> List[str]:
        """批次事件記錄"""
        pass
    
    def update_context_anchor(self, anchor_id: str, new_state: Dict[str, Any]) -> bool:
        """更新語境錨點狀態"""
        pass
```

### 2.2 抽象事件發送接口
```python
class INarrativeEventSender:
    API_VERSION = "1.0"
    def send_event(self, event_type: str, memory_id: str, context: Dict[str, Any], api_version: str = API_VERSION) -> bool:
        raise NotImplementedError
```

### 2.3 治理回饋回調接口
```python
class IGovernanceFeedbackReceiver:
    API_VERSION = "1.0"
    def receive_feedback(self, event_id: str, decision: str, notes: Dict[str, Any], api_version: str = API_VERSION) -> bool:
        raise NotImplementedError
```

---

## 3. 數據交換協議格式
```python
system_event_memory_format_v1 = {
    "event_id": "uuid",
    "event_type": "VETO_APPLIED | EXTERNAL_FAILURE | NOISE_BLOCKED | INTERNAL_ANOMALY",
    "severity": "low | medium | high",
    "dag_hash": "abc123",
    "timestamp": "2025-12-13T19:30:00Z",
    "description": "人類可讀描述",
    "raw_data": {
        "ciphertext": "...",
        "key_id": "key_2025_12"
    }
}
```

---

## 4. 安全與加密規範
- **傳輸層**：TLS 1.3  
- **敏感數據**：AES-256-GCM 加密，密鑰分離存儲  
- **存儲加密**：所有持久化數據必須啟用靜態加密  

---

## 5. 錯誤處理與狀態碼
### 標準錯誤響應
```json
{
  "success": false,
  "error": {
    "code": "INVALID_EVENT_FORMAT",
    "message": "The 'event_type' field is missing.",
    "detail": {},
    "api_version": "1.0"
  }
}
```

### 錯誤碼列表
- MEMORY_NOT_FOUND  
- INVALID_EVENT_FORMAT  
- INVALID_TIME_WINDOW  
- ENCRYPTION_FAILED  
- PERMISSION_DENIED  
- BATCH_TOO_LARGE  
- UNSUPPORTED_API_VERSION  

---

## 6. 變更與兼容性策略
- **版本標識**：所有接口與數據格式需包含 `API_VERSION`  
- **向後兼容**：破壞性變更需新版本，舊版維護一段時間  
- **棄用流程**：返回 `DEPRECATED_API` 警告，引導升級  

---

## 7. 效能與限制
- **響應時間**：  
  - `retrieve_relevant_memories` < 100ms (95th percentile)  
  - `log_system_event` < 50ms  
  - `log_system_events_batch` < 200ms (100 events)  
- **容量限制**：  
  - 單批次 ≤ 1000 events  
  - 單次查詢 ≤ 100 條記憶  
  - 單事件大小 ≤ 1MB (加密後)  
- **並發限制**：  
  - 最大查詢 100 QPS  
  - 批次寫入 10 TPS  

---

## 8. 可觀測性
- **必須記錄的指標**：API 調用次數、響應時間分佈、錯誤率、批次大小分佈  
- **必須記錄的日誌**：所有 API 調用、所有錯誤、加密/解密操作（不含密鑰）  

---

## 9. 測試要求
- **單元測試**：覆蓋率 ≥ 80%  
- **集成測試**：必須包含 VETO_APPLIED、批次操作、加密流程、版本相容性、錯誤處理  
- **壓力測試**：100 QPS 查詢、10 TPS 批次寫入、持續 1 小時  

---

## 📌 總結
這份契約已經升級為 **技術規範**，涵蓋：
- 接口表  
- 抽象接口  
- 數據格式  
- 安全規範  
- 錯誤處理  
- 版本策略  
- 效能限制  
- 可觀測性  
- 測試要求  

它能確保記憶模組與 Meta‑DAG 在沒有彼此程式碼的情況下，仍能安全、清晰、可演進地對接。
```

---

