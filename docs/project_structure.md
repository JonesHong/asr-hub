# ASR Core 專案結構

```
asr_core/
├── README.md
├── requirements.txt
├── setup.py
├── config/
│   └── config.ini                    # 主配置檔案
├── src/
│   ├── __init__.py
│   ├── config/                       # 配置管理
│   │   ├── __init__.py
│   │   ├── manager.py               # ConfigManager
│   │   └── schema.py                # 使用 ini2py 的配置 schema
│   ├── core/                        # 核心業務邏輯
│   │   ├── __init__.py
│   │   ├── facade.py                # ASR Facade Service
│   │   ├── pipeline.py              # Audio Pipeline Manager
│   │   └── registry.py              # 組件註冊管理
│   ├── engines/                     # ASR 引擎池
│   │   ├── __init__.py
│   │   ├── base.py                  # ASR Engine 抽象基類
│   │   ├── funasr.py                # FunASR 引擎
│   │   ├── whisper.py               # Whisper 引擎
│   │   ├── vosk.py                  # Vosk 引擎
│   │   └── cloud/                   # 雲端 API 引擎
│   │       ├── __init__.py
│   │       ├── google.py
│   │       ├── microsoft.py
│   │       └── openai.py
│   ├── preprocessors/               # 音訊前處理器
│   │   ├── __init__.py
│   │   ├── base.py                  # AudioPreprocessor 抽象基類
│   │   ├── noise_reduction.py       # 降噪處理器
│   │   └── voice_enhancement.py     # 人聲增強處理器
│   ├── services/                    # 服務層
│   │   ├── __init__.py
│   │   └── audio_capture.py         # 音訊擷取服務 (你現有的程式碼)
│   ├── adapters/                    # 通訊協定適配器
│   │   ├── __init__.py
│   │   ├── rest.py                  # RESTful API
│   │   ├── websocket.py             # WebSocket (未來)
│   │   └── redis.py                 # Redis (未來)
│   └── utils/                       # 工具類
│       ├── __init__.py
│       ├── audio.py                 # 音訊處理工具
│       ├── exceptions.py            # 自定義異常
│       └── logger.py                # 日誌工具
├── tests/                           # 測試
│   ├── __init__.py
│   ├── test_engines/
│   ├── test_preprocessors/
│   └── test_core/
├── examples/                        # 使用範例
│   ├── simple_transcribe.py
│   └── streaming_demo.py
└── docs/                           # 文檔
    ├── api.md
    └── configuration.md
```

## 設計說明

### 核心目錄職責

1. **`src/config/`**: 配置管理，使用 ini2py 處理配置轉換
2. **`src/core/`**: 核心業務邏輯，包含 Facade 和 Pipeline 管理
3. **`src/engines/`**: ASR 引擎池，所有 ASR 引擎實作
4. **`src/preprocessors/`**: 音訊前處理器
5. **`src/services/`**: 服務層，包含你的音訊擷取服務
6. **`src/adapters/`**: 通訊協定適配器
7. **`src/utils/`**: 共用工具類

### 檔案放置說明

- **ASR Facade Service** → `src/core/facade.py`
- **Audio Pipeline Manager** → `src/core/pipeline.py`  
- **ASR Engine Pool** → `src/engines/` 目錄下的各個引擎
- **音訊擷取服務** → `src/services/audio_capture.py`

### 設計優勢

1. **職責分離**: 每個目錄都有明確的職責
2. **擴展性**: 新增引擎或處理器只需在對應目錄新增檔案
3. **測試友好**: 清晰的結構便於編寫單元測試
4. **維護性**: 遵循 KISS 原則，結構簡潔明瞭