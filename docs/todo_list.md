# ASR Core 執行計畫書

## 🎯 專案概述
建立一個通用的 Python ASR 架構，支援多種 ASR 引擎（funasr, whisper, vosk, 雲端 API），具備彈性的音訊前處理管線，並提供統一的 Facade 介面。

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

## 📋 Phase 7: 進階功能

### 7.1 更多通訊協定
- [ ] 實作 `src/adapters/websocket.py` - WebSocket 適配器
- [ ] 實作 `src/adapters/redis.py` - Redis 佇列適配器
- [ ] 規劃 gRPC 支援

### 7.2 系統優化
- [ ] 實作連接池管理
- [ ] 實作快取機制
- [ ] 效能監控和指標收集
- [ ] 記憶體使用優化

---

## 📋 Phase 8: 測試和文檔

### 8.1 完整測試套件
- [ ] 完善單元測試覆蓋率
- [ ] 建立整合測試
- [ ] 建立效能測試
- [ ] 建立 CI/CD 流程

### 8.2 文檔完善
- [ ] 撰寫完整的 `README.md`
- [ ] 撰寫配置文檔 `docs/configuration.md`
- [ ] 撰寫開發者指南
- [ ] 建立部署指南

---

## 🚀 快速開始建議

建議從 **Phase 1.2** 開始，因為配置管理是整個系統的基礎。接著完成 **Phase 1.3** 的抽象類定義，這樣後續的實作會更順暢。

每個 Phase 完成後建議進行簡單的整合測試，確保各組件能正常協作。