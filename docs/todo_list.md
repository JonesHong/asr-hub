# ASR Core 執行計畫書

## 🎯 專案概述
建立一個通用的 Python ASR 架構，支援多種 ASR 引擎（funasr, whisper, vosk, 雲端 API），具備彈性的音訊前處理管線，並提供統一的 Facade 介面。架構設計支援未來擴展事件驅動系統和多用戶支援。

---

## 📋 Phase 1: 基礎架構建立

### 1.1 專案初始化
- [x] 建立專案目錄結構
- [x] 設置 `requirements.txt`
- [x] 建立 `setup.py`
- [x] 初始化 git repository
- [x] 建立 `.gitignore`

### 1.2 配置管理系統
- [x] 安裝和設置 `ini2py` 庫
- [x] 建立基礎 `config/config.ini` 檔案
- [x] 執行 `ini2py` 自動產生 `src/config/manager.py`, `src/config/schema.py` - ConfigManager 類, 配置 schema 定義
- [x] 測試配置讀取功能

### 1.3 核心抽象類定義
- [x] 實作 `src/engines/base.py` - ASREngine 抽象基類
- [x] 實作 `src/preprocessors/base.py` - AudioPreprocessor 抽象基類
- [x] 建立 `src/utils/exceptions.py` - 自定義異常類
- [x] 建立 `src/utils/audio.py` - 音訊處理工具函數

---

## 📋 Phase 2: 核心組件實作

### 2.1 管線管理器
- [x] 實作 `src/core/pipeline.py` - AudioPipelineManager 類
- [x] 實作 AudioPipeline 類（處理器鏈）
- [x] 建立組件註冊機制 `src/core/registry.py`
- [x] 測試管線創建和執行功能

### 2.2 第一個 ASR 引擎 (Whisper)
- [x] 實作 `src/engines/whisper.py` - WhisperEngine 類
- [x] 實作離線轉譯功能
- [x] 實作串流轉譯功能（後備方案）
- [x] 建立 Whisper 相關配置選項
- [x] 單元測試

### 2.3 第一個前處理器
- [x] 實作 `src/preprocessors/noise_reduction.py` - 基礎降噪處理器
- [x] 實作音訊格式標準化功能
- [x] 建立前處理器配置選項
- [x] 單元測試

---

## 📋 Phase 3: Facade 服務建立

### 3.1 ASR Facade Service
- [ ] 實作 `src/core/facade.py` - ASRFacadeService 類
- [ ] 實作引擎選擇邏輯
- [ ] 實作前處理管線整合
- [ ] 實作離線轉譯功能
- [ ] 實作串流轉譯功能
- [ ] 錯誤處理和日誌記錄

### 3.2 音訊擷取服務整合
- [ ] 重構現有 `audio_input_capture.py` 到 `src/services/audio_capture.py`
- [ ] 與 ASR Facade Service 整合
- [ ] 建立音訊串流到轉譯的完整流程
- [ ] 測試即時音訊轉譯功能

---

## 📋 Phase 4: RESTful API 實作

### 4.1 REST API 適配器
- [ ] 安裝 FastAPI 和相關依賴
- [ ] 實作 `src/adapters/rest.py` - RESTful API 適配器
- [ ] 建立 `/transcribe` 端點（一次性轉譯）
- [ ] 建立 `/transcribe_stream` WebSocket 端點（串流轉譯）
- [ ] 實作參數驗證和錯誤處理

### 4.2 API 測試和文檔
- [ ] 建立 API 測試案例
- [ ] 撰寫 API 文檔 `docs/api.md`
- [ ] 建立使用範例 `examples/simple_transcribe.py`
- [ ] 建立串流範例 `examples/streaming_demo.py`

---

## 📋 Phase 5: 擴展更多 ASR 引擎

### 5.1 FunASR 引擎
- [ ] 實作 `src/engines/funasr.py` - FunasrEngine 類
- [ ] 支援離線和串流模式
- [ ] 建立 FunASR 配置選項
- [ ] 單元測試

### 5.2 Vosk 引擎
- [ ] 實作 `src/engines/vosk.py` - VoskEngine 類
- [ ] 支援離線和串流模式
- [ ] 建立 Vosk 配置選項
- [ ] 單元測試

### 5.3 雲端 API 引擎
- [ ] 實作 `src/engines/cloud/google.py` - Google Cloud Speech API
- [ ] 實作 `src/engines/cloud/microsoft.py` - Azure Speech API  
- [ ] 實作 `src/engines/cloud/openai.py` - OpenAI Whisper API
- [ ] 建立 API 金鑰管理機制
- [ ] 單元測試

---

## 📋 Phase 6: 擴展前處理器

### 6.1 更多前處理器
- [ ] 實作 `src/preprocessors/voice_enhancement.py` - 人聲增強
- [ ] 實作音量正規化處理器
- [ ] 實作音訊格式轉換處理器
- [ ] 支援前處理器的串流模式

### 6.2 前處理器管線優化
- [ ] 實作條件式前處理（根據音訊特性選擇）
- [ ] 優化串流前處理效能
- [ ] 建立前處理器效能基準測試

---

## 📋 Phase 7: 事件驅動系統 🆕

### 7.1 PyStoreX 狀態管理整合
- [ ] 安裝和設置 `pystorex` 依賴
- [ ] 建立 `src/core/asr_store.py` - ASR 狀態管理
- [ ] 定義 ASR Actions（啟動事件、停止事件）
- [ ] 實作 ASR Reducer
- [ ] 實作 ASR Effects

### 7.2 事件觸發機制
- [ ] 擴展 ASR Facade Service 支援事件驅動
- [ ] 實作視覺觸發啟動 (`trigger_visual_start`)
- [ ] 實作 UI 按鈕觸發 (`trigger_ui_start`, `trigger_ui_stop`)
- [ ] 實作關鍵詞觸發 (`trigger_keyword_start`)
- [ ] 實作超時停止機制 (`trigger_timeout_stop`)

### 7.3 背景 ASR 支援
- [ ] 實作背景 ASR 模式（用於關鍵詞偵測）
- [ ] 整合音訊擷取服務的背景模式
- [ ] 建立關鍵詞偵測配置
- [ ] 測試事件驅動流程

---

## 📋 Phase 8: 多用戶支援 🆕

### 8.1 混合模式架構
- [ ] 擴展 ASR State 支援單用戶/多用戶模式
- [ ] 實作用戶會話管理
- [ ] 建立並發控制機制
- [ ] 實作用戶隔離

### 8.2 多用戶 Actions 和 Reducers
- [ ] 定義多用戶相關 Actions
- [ ] 實作多用戶 Reducer 邏輯
- [ ] 建立用戶會話 Effects
- [ ] 實作資源管理和限制

### 8.3 配置驅動模式切換
- [ ] 建立模式配置選項
- [ ] 實作智能 Reducer（根據模式選擇邏輯）
- [ ] 建立多用戶 API 端點
- [ ] 效能測試和優化

---

## 📋 Phase 9: 進階功能

### 9.1 更多通訊協定
- [ ] 實作 `src/adapters/websocket.py` - WebSocket 適配器
- [ ] 實作 `src/adapters/redis.py` - Redis 佇列適配器
- [ ] 規劃 gRPC 支援

### 9.2 系統優化
- [ ] 實作連接池管理
- [ ] 實作快取機制
- [ ] 效能監控和指標收集
- [ ] 記憶體使用優化

---

## 📋 Phase 10: 測試和文檔

### 10.1 完整測試套件
- [ ] 完善單元測試覆蓋率
- [ ] 建立整合測試
- [ ] 建立效能測試
- [ ] 建立 CI/CD 流程

### 10.2 文檔完善
- [ ] 撰寫完整的 `README.md`
- [ ] 撰寫配置文檔 `docs/configuration.md`
- [ ] 撰寫事件驅動使用指南
- [ ] 撰寫多用戶部署指南
- [ ] 建立開發者指南

---

## 🚀 執行策略

### 當前優先級（Phase 1-6）
專注於建立穩定的核心架構：
1. **Phase 3**: 完成 Facade 服務，建立核心轉譯能力
2. **Phase 4**: 實作 REST API，提供基本服務能力
3. **Phase 5-6**: 擴展引擎和前處理器，增強功能性

### 未來擴展（Phase 7-8）
在核心架構穩定後加入進階功能：
1. **Phase 7**: 事件驅動系統，提升用戶體驗
2. **Phase 8**: 多用戶支援，擴展服務能力

### 設計原則
- **KISS 原則**: 保持每個階段的實作簡潔明瞭
- **漸進式開發**: 每個 Phase 都能獨立運行和測試
- **向後相容**: 新功能不破壞現有 API
- **配置驅動**: 新功能可以透過配置開啟/關閉

每個 Phase 完成後建議進行簡單的整合測試，確保各組件能正常協作。