## 📝 **完整 TODO 清單 (複製到代碼開頭)**

```python
"""
記憶模組實作 (v0.1-alpha)

🔴 CRITICAL (必須完成才符合契約):
- [ ] retrieve_relevant_memories: 補完 time_range 篩選
- [ ] retrieve_relevant_memories: 補完 severity 篩選
- [ ] retrieve_relevant_memories: 補完 keywords 篩選
- [ ] retrieve_relevant_memories: 實作解密邏輯 (_decrypt_and_serialize)
- [ ] MemoryManager: 實作 IGovernanceFeedbackReceiver.receive_feedback()

🟡 HIGH (應盡快完成以提升品質):
- [ ] log_system_events_batch: 返回詳細失敗資訊
- [ ] MemoryManager: 建立 event_type/severity 索引以提升查詢效能
- [ ] observe_performance: 加入效能警告閾值

🟢 LOW (優化項,可之後完成):
- [ ] MetaDAGError: 加 to_dict() 方法
- [ ] MemoryCard: 加 from_dict() 工廠方法
- [ ] 實作真實 AES-256-GCM 加密/解密
- [ ] 整合 TimescaleDB 替換 in-memory store

📅 計劃:
- Phase 1 (現在): 完成 🔴 CRITICAL 項目
- Phase 2 (v0.2): 完成 🟡 HIGH 項目  
- Phase 3 (v1.0): 完成 🟢 LOW 項目 + TimescaleDB 整合
"""
```


import uuid
import time
import functools
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# 設置結構化日誌（滿足契約第 8 章：可觀測性）
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 0. 標準錯誤與可觀測性定義 ---
class MetaDAGError(Exception):
    """
    自定義異常類，用於返回契約第 5 章定義的標準錯誤格式。
    """
    def __init__(self, error_code: str, message: str, detail: Optional[Dict] = None):
        self.error_code = error_code
        self.message = message
        self.detail = detail or {}
        super().__init__(message)

def observe_performance(metric_name: str):
    """
    可觀測性裝飾器：自動記錄 API 調用指標和日誌（契約第 8 章）。
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.perf_counter()
            # 記錄調用開始（生產環境需對敏感參數脫敏）
            logger.info(f"API Called: {func.__name__}", extra={"metric": metric_name})
            
            try:
                result = func(self, *args, **kwargs)
                duration = (time.perf_counter() - start_time) * 1000  # 毫秒
                
                # 記錄成功指標 (應發送到 Prometheus/StatsD)
                # metrics.timing(f"memory_api.{metric_name}.duration", duration)
                logger.info(f"API Success: {func.__name__}", extra={"duration_ms": duration, "result_size": len(result) if isinstance(result, list) else 1})
                
                return result
            except Exception as e:
                duration = (time.perf_counter() - start_time) * 1000
                # 記錄失敗指標並標準化錯誤
                # metrics.incr(f"memory_api.{metric_name}.error")
                logger.exception(f"API Error: {func.__name__}", extra={"error": str(e), "duration_ms": duration})
                # 重新拋出標準化錯誤 (契約第 5 章)
                raise self._standardize_error(e)
        return wrapper
    return decorator

# --- 1. MemoryCard 數據模型 (對應契約 system_event_memory_format_v1) ---
@dataclass(frozen=True)
class MemoryCard:
    """
    不可變的記憶卡數據模型。
    """
    
    # 契約版本 (新增，滿足契約第 6 章)
    api_version: str = "1.0"
    
    # Core Fields for Indexing (TimescaleDB Hypertable Primary Key)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Governance & Severity
    event_type: str  # VETO_APPLIED | EXTERNAL_FAILURE | NOISE_BLOCKED | INTERNAL_ANOMALY
    severity: str    # high | medium | low
    description: str
    dag_hash: Optional[str] = None  # Related DAG Node Hash
    
    # 加密數據 (新增，滿足契約第 4 章：安全與加密規範)
    encrypted_data_ciphertext: Optional[bytes] = None
    encrypted_data_key_id: Optional[str] = None
    
    # 用於高效查詢的索引字段 (新增，優化 retrieve_relevant_memories 性能)
    indexed_keywords: List[str] = field(default_factory=list)
    
    @property
    def is_encrypted(self) -> bool:
        """檢查敏感數據是否已加密。"""
        return self.encrypted_data_ciphertext is not None


# --- 2. 抽象接口：INarrativeEventSender & IGovernanceFeedbackReceiver (契約 2.2/2.3) ---
class INarrativeEventSender:
    """抽象接口：將記憶系統中檢測到的事件發送給治理層。"""
    API_VERSION = "1.0"
    def send_event(self, event_type: str, memory_id: str, context: Dict[str, Any], api_version: str = API_VERSION) -> bool:
        raise NotImplementedError

class IGovernanceFeedbackReceiver:
    """抽象回調接口：用於接收治理層的最終決策。"""
    API_VERSION = "1.0"
    def receive_feedback(self, event_id: str, decision: str, notes: Dict[str, Any], api_version: str = API_VERSION) -> bool:
        raise NotImplementedError


# --- 3. 核心管理類：MemoryManager (實現契約 Core APIs) ---
class MemoryManager:
    """
    記憶模組的核心管理器，實現所有契約要求。
    將優先使用記憶體 (in-memory) 模擬存儲，以快速驗證邏輯。
    """
    API_VERSION = "1.0"
    
    def __init__(self, event_sender: INarrativeEventSender):
        self._event_sender = event_sender
        # In-memory store for rapid prototyping (will be replaced by TimescaleDB)
        self._memory_store: List[MemoryCard] = [] 
        logger.info("MemoryManager initialized. Ready for in-memory logic testing.")


    @observe_performance("log_system_event")
    def log_system_event(self, event: Dict[str, Any], api_version: str = API_VERSION) -> str:
        """
        契約接口：單條事件記錄。必須滿足 P95 < 50ms。
        """
        # 1. 確保 API 版本相符
        if api_version != self.API_VERSION:
            raise MetaDAGError("UNSUPPORTED_API_VERSION", f"API version {api_version} is not supported.")
            
        # 2. 創建 MemoryCard 並加密 raw_data
        memory_card = self._create_and_encrypt_card(event)
        
        # 3. 數據庫寫入 (In-memory Placeholder)
        self._memory_store.append(memory_card)
        
        # 4. 觸發事件發送者 (回調給 Meta-DAG)
        self._event_sender.send_event(
            event_type=memory_card.event_type,
            memory_id=memory_card.event_id,
            context={"description": memory_card.description, "dag_hash": memory_card.dag_hash}
        )
        
        return memory_card.event_id

    @observe_performance("log_system_events_batch")
    def log_system_events_batch(self, events: List[Dict[str, Any]], api_version: str = API_VERSION) -> List[str]:
        """
        契約接口：高性能批次記錄事件。必須滿足 P95 < 200ms (100 events)。
        """
        if api_version != self.API_VERSION:
            raise MetaDAGError("UNSUPPORTED_API_VERSION", f"API version {api_version} is not supported.")
            
        if len(events) > 1000:  # 執行契約 7.2 容量限制
            raise MetaDAGError("BATCH_TOO_LARGE", f"Batch size ({len(events)}) exceeds 1000 event limit.")

        memory_cards: List[MemoryCard] = []
        for event in events:
            try:
                card = self._create_and_encrypt_card(event)
                memory_cards.append(card)
            except MetaDAGError:
                # 批次處理中遇到單個錯誤不應中斷整個批次，但應記錄並跳過
                logger.error("Skipping malformed event in batch.")
                continue
        
        # 3. 數據庫批量寫入 (In-memory Placeholder - 關鍵是使用 DB 的批量插入優化)
        self._memory_store.extend(memory_cards)
        
        # 4. 觸發事件發送者 (通常批次寫入後，通知也會以批次或定期方式發送)
        logger.info(f"Successfully processed batch of {len(memory_cards)} events.")
        
        return [card.event_id for card in memory_cards]

    @observe_performance("retrieve_relevant_memories")
    def retrieve_relevant_memories(self, query: Dict[str, Any], api_version: str = API_VERSION) -> List[Dict[str, Any]]:
        """
        契約接口：結構化查詢，支持 keywords, event_types, time_range, severity。
        必須滿足 P95 < 100ms。
        """
        # 查詢邏輯將嚴重依賴 TimescaleDB 的時間索引和 FTS 查詢。
        # In-memory 實現僅為邏輯驗證的 Placeholder。
        
        # 根據契約 7.2 限制單次查詢結果
        limit = min(query.get("limit", 100), 100)
        
        # In-memory 模擬查詢
        results = [card for card in self._memory_store if card.event_type in query.get("event_types", [card.event_type])]
        
        if not results:
            raise MetaDAGError("MEMORY_NOT_FOUND", "No relevant memory found within the given time window.")

        # 返回結果必須轉換為字典格式，並解密 raw_data
        # Placeholder: 實際應從 DB 獲取，並呼叫 self._decrypt_card(card)
        return [card.__dict__ for card in results[:limit]]

    
    # --- 內部輔助方法 ---
    
    def _create_and_encrypt_card(self, event_data: Dict[str, Any]) -> MemoryCard:
        """
        內部方法：創建 MemoryCard 並對 raw_data 進行加密。
        """
        # 1. 驗證核心必填字段 (契約精神)
        required_fields = ["event_type", "severity", "description"]
        if not all(field in event_data for field in required_fields):
             raise MetaDAGError("INVALID_EVENT_FORMAT", "Missing required fields in event data.")
        
        raw_data = event_data.get('raw_data', {})
        ciphertext = None
        key_id = None
        
        if raw_data:
            # 2. 加密邏輯 (模擬 AES-256-GCM - 契約第 4 章)
            key_id = "key_2025_12"  # 應來自 KMS
            # ciphertext = encryption_service.encrypt(json.dumps(raw_data), key_id)
            ciphertext = b"SIMULATED_AES256_CIPHERTEXT"
            logger.debug(f"[Encryption Simulated] Raw data encrypted with key: {key_id}")

        # 3. 提取索引關鍵字
        indexed_keywords = self._extract_keywords(event_data.get('description', ''), raw_data)
        
        return MemoryCard(
            api_version=self.API_VERSION,
            event_type=event_data['event_type'],
            severity=event_data['severity'],
            description=event_data['description'],
            dag_hash=event_data.get('dag_hash'),
            encrypted_data_ciphertext=ciphertext,
            encrypted_data_key_id=key_id,
            indexed_keywords=indexed_keywords
        )

    def _extract_keywords(self, description: str, raw_data: Dict[str, Any]) -> List[str]:
        """
        內部方法：從數據中提取用於快速查詢的關鍵字。
        (生產環境中會使用更複雜的 NLP 技術)
        """
        keywords = set(description.lower().split())
        if 'tul_marker' in raw_data:
            keywords.add(raw_data['tul_marker'])
        # 移除通用詞彙
        return list(keywords - {'a', 'the', 'is', 'in', 'of', 'and', 'or', 'to', 'from'})

    def _standardize_error(self, e: Exception) -> MetaDAGError:
        """
        內部方法：將所有異常轉換為契約第 5 章定義的標準錯誤格式。
        """
        if isinstance(e, MetaDAGError):
            # 已經是標準錯誤，直接返回
            return e
        
        if "BATCH_TOO_LARGE" in str(e):
            return MetaDAGError("BATCH_TOO_LARGE", "Batch size exceeds contract limit.", {"limit": 1000})
        
        # 默認的內部錯誤處理
        return MetaDAGError("INTERNAL_ERROR", "An unhandled internal error occurred.", {"exception": type(e).__name__})



# 🎯 **分類建議!**

---

## 📋 **建議分類:**

### **🔴 必須「現在」改 (會導致契約不符)**

```python
# 1. 完整查詢邏輯 (契約要求,現在缺失)
# 位置: retrieve_relevant_memories()

def retrieve_relevant_memories(self, query: Dict[str, Any], api_version: str = API_VERSION) -> List[Dict[str, Any]]:
    """
    TODO (CRITICAL): 補完契約要求的查詢邏輯
    - [ ] time_range 篩選
    - [ ] severity 篩選  
    - [ ] keywords 篩選
    當前只實作了 event_types 查詢
    """
    # 現有代碼...
    
    # TODO: 加入以下篩選邏輯
    # time_range = query.get("time_range")
    # if time_range:
    #     start = datetime.fromisoformat(time_range["start"])
    #     end = datetime.fromisoformat(time_range["end"])
    #     results = [card for card in results if start <= card.timestamp <= end]
    
    # severity_filter = query.get("severity")
    # if severity_filter:
    #     results = [card for card in results if card.severity in severity_filter]
    
    # keywords = query.get("keywords", [])
    # if keywords:
    #     results = [card for card in results if any(kw.lower() in card.indexed_keywords for kw in keywords)]
```

```python
# 2. 解密邏輯 (契約要求返回解密數據)
# 位置: retrieve_relevant_memories()

def retrieve_relevant_memories(self, query: Dict[str, Any], api_version: str = API_VERSION) -> List[Dict[str, Any]]:
    """
    TODO (CRITICAL): 返回解密後的數據
    當前返回 card.__dict__ 包含加密的 ciphertext
    契約要求返回解密的 raw_data
    """
    # return [card.__dict__ for card in results[:limit]]  # 舊代碼
    return [self._decrypt_and_serialize(card) for card in results[:limit]]  # 新代碼

# TODO: 實作 _decrypt_and_serialize() 方法
def _decrypt_and_serialize(self, card: MemoryCard) -> Dict[str, Any]:
    """將 MemoryCard 轉為字典並解密敏感數據"""
    result = {
        "event_id": card.event_id,
        "timestamp": card.timestamp.isoformat(),
        "event_type": card.event_type,
        "severity": card.severity,
        "description": card.description,
        "dag_hash": card.dag_hash,
        "api_version": card.api_version
    }
    
    if card.is_encrypted:
        # TODO: 實作真實解密 (現在先模擬)
        # decrypted = self._decrypt_data(card.encrypted_data_ciphertext, card.encrypted_data_key_id)
        result['raw_data'] = {"SIMULATED": "decrypted_data"}
    
    return result
```

```python
# 3. 實作 IGovernanceFeedbackReceiver (契約要求)
# 位置: MemoryManager 類定義

class MemoryManager(IGovernanceFeedbackReceiver):  # 加上繼承
    """
    TODO (CRITICAL): 實作 receive_feedback 介面
    契約 2.3 要求記憶模組能接收治理決策反饋
    """
    
    @observe_performance("receive_feedback")
    def receive_feedback(self, event_id: str, decision: str, notes: Dict[str, Any], api_version: str = "1.0") -> bool:
        """接收 Meta-DAG 的治理決策反饋 (契約 2.3)"""
        if api_version != self.API_VERSION:
            raise MetaDAGError("UNSUPPORTED_API_VERSION", f"API version {api_version} is not supported.")
        
        # 找到對應記憶卡
        card = next((c for c in self._memory_store if c.event_id == event_id), None)
        if not card:
            logger.warning(f"Feedback received for unknown event_id: {event_id}")
            return False
        
        logger.info(f"✓ Feedback received for {event_id}: {decision}")
        
        # TODO: 實際生產環境應更新 DB 中的記憶狀態
        # TODO: 可選擇性地將反饋記錄為新事件
        
        return True
```

---

### **🟡 應該「盡快」改 (影響功能品質)**

```python
# 4. 批次處理返回失敗資訊
# 位置: log_system_events_batch()

def log_system_events_batch(self, events: List[Dict[str, Any]], api_version: str = API_VERSION) -> Dict[str, Any]:
    """
    TODO (HIGH): 返回詳細的批次處理結果
    當前只返回成功的 event_ids
    應該告知哪些事件失敗及原因
    """
    # ...現有代碼...
    
    memory_cards: List[MemoryCard] = []
    failed_events: List[Dict[str, Any]] = []  # 新增
    
    for i, event in enumerate(events):
        try:
            card = self._create_and_encrypt_card(event)
            memory_cards.append(card)
        except MetaDAGError as e:
            logger.error(f"Skipping malformed event at index {i}")
            failed_events.append({"index": i, "error": e.error_code, "message": e.message})  # 新增
            continue
    
    self._memory_store.extend(memory_cards)
    logger.info(f"Successfully processed batch: {len(memory_cards)} success, {len(failed_events)} failed.")
    
    # 返回詳細結果
    return {
        "success_ids": [card.event_id for card in memory_cards],
        "success_count": len(memory_cards),
        "failed_count": len(failed_events),
        "failed_events": failed_events  # 新增
    }
```

```python
# 5. 查詢效能優化 (索引)
# 位置: MemoryManager __init__

def __init__(self, event_sender: INarrativeEventSender):
    """
    TODO (HIGH): 加入索引以提升查詢效能
    當前 retrieve_relevant_memories 使用全掃描
    """
    self._event_sender = event_sender
    self._memory_store: List[MemoryCard] = []
    
    # TODO: 建立索引 (TimescaleDB 前的臨時優化)
    self._event_type_index: Dict[str, List[MemoryCard]] = defaultdict(list)
    self._severity_index: Dict[str, List[MemoryCard]] = defaultdict(list)
    
    logger.info("MemoryManager initialized with in-memory indexes.")

# TODO: 在 log_system_event 和 log_system_events_batch 中更新索引
def _update_indexes(self, card: MemoryCard):
    """更新所有索引"""
    self._event_type_index[card.event_type].append(card)
    self._severity_index[card.severity].append(card)
```

---

### **🟢 可以「之後」改 (優化項)**

```python
# 6. MetaDAGError 加 to_dict()
# 位置: MetaDAGError 類

class MetaDAGError(Exception):
    """TODO (LOW): 加 to_dict() 方法便於序列化"""
    def __init__(self, error_code: str, message: str, detail: Optional[Dict] = None):
        self.error_code = error_code
        self.message = message
        self.detail = detail or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """返回契約第 5 章定義的標準錯誤格式"""
        return {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": self.message,
                "detail": self.detail,
                "api_version": "1.0"
            }
        }
```

```python
# 7. MemoryCard 加工廠方法
# 位置: MemoryCard 類

@dataclass(frozen=True)
class MemoryCard:
    """TODO (LOW): 加 from_dict() 工廠方法便於反序列化"""
    # ...現有欄位...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryCard':
        """從字典創建 MemoryCard (用於 DB 讀取)"""
        # 處理日期時間轉換
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)
```

```python
# 8. 效能警告閾值
# 位置: observe_performance 裝飾器

def observe_performance(metric_name: str):
    """TODO (LOW): 加效能警告閾值 (契約 7.1)"""
    # 定義 P95 閾值
    THRESHOLDS = {
        "log_system_event": 50,        # ms
        "log_system_events_batch": 200, # ms
        "retrieve_relevant_memories": 100 # ms
    }
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.perf_counter()
            # ...現有代碼...
            
            try:
                result = func(self, *args, **kwargs)
                duration = (time.perf_counter() - start_time) * 1000
                
                # 檢查是否超過閾值
                threshold = THRESHOLDS.get(metric_name, 1000)
                if duration > threshold:
                    logger.warning(f"⚠️ Performance Alert: {func.__name__} took {duration:.2f}ms (threshold: {threshold}ms)")
                
                logger.info(f"API Success: {func.__name__}", extra={"duration_ms": duration})
                return result
            # ...
```

```python
# 9. 真實加密實作
# 位置: _create_and_encrypt_card()

def _encrypt_data(self, data: Dict[str, Any], key_id: str) -> bytes:
    """
    TODO (LOW): 實作真實 AES-256-GCM 加密 (契約第 4 章)
    需要:
    - from cryptography.fernet import Fernet
    - 整合 KMS 密鑰管理
    """
    # key = self._get_key_from_kms(key_id)
    # f = Fernet(key)
    # return f.encrypt(json.dumps(data).encode())
    pass

def _decrypt_data(self, ciphertext: bytes, key_id: str) -> str:
    """解密數據"""
    # key = self._get_key_from_kms(key_id)
    # f = Fernet(key)
    # return f.decrypt(ciphertext).decode()
    pass
```

---

