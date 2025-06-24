# 通用 ASR 架構設計

## 1. 整體架構

```
┌─────────────────────────────────────────┐
│              通訊層 (Adapters)           │
│  RESTful → WebSocket → gRPC → Redis     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           ASR Facade Service            │
│  - 統一入口點                           │
│  - 根據 config/參數選擇引擎和前處理      │
│  - 處理同步/異步轉換                    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Audio Pipeline Manager          │
│  - 管理前處理器鏈                       │
│  - 支援動態組合和配置                   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            ASR Engine Pool              │
│  funasr │ whisper │ vosk │ cloud APIs   │
└─────────────────────────────────────────┘
```

## 2. 核心抽象類設計

### ASR Engine 抽象類

```python
from abc import ABC, abstractmethod
from typing import Union, AsyncGenerator, Dict, Any
from enum import Enum

class ASRMode(Enum):
    OFFLINE = "offline"      # 一次性轉譯
    STREAMING = "streaming"  # 串流轉譯

class ASREngine(ABC):
    """ASR 引擎抽象基類"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self._get_name()
        self._initialize()
    
    @abstractmethod
    def _get_name(self) -> str:
        """返回引擎名稱"""
        pass
    
    @abstractmethod 
    def _initialize(self):
        """初始化引擎"""
        pass
    
    @abstractmethod
    def transcribe(self, audio_bytes: bytes, **kwargs) -> str:
        """離線轉譯"""
        pass
    
    @property
    def supports_streaming(self) -> bool:
        """是否支援串流"""
        return False
    
    async def transcribe_streaming(self, 
                                 audio_stream: AsyncGenerator[bytes, None], 
                                 **kwargs) -> AsyncGenerator[str, None]:
        """串流轉譯 - 預設實作為收集全部音訊後轉譯"""
        if not self.supports_streaming:
            # 後備方案：收集全部音訊
            audio_buffer = b""
            async for chunk in audio_stream:
                audio_buffer += chunk
            
            if audio_buffer:
                result = self.transcribe(audio_buffer, **kwargs)
                yield result
            return
        
        raise NotImplementedError("子類必須實作串流轉譯")
```

### Audio Preprocessor 抽象類

```python
class AudioPreprocessor(ABC):
    """音訊前處理器抽象基類"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self._get_name()
        self._initialize()
    
    @abstractmethod
    def _get_name(self) -> str:
        pass
    
    @abstractmethod
    def _initialize(self):
        pass
    
    @abstractmethod
    def process(self, audio_bytes: bytes) -> bytes:
        """處理音訊"""
        pass
    
    @property
    def supports_streaming(self) -> bool:
        """是否支援串流處理"""
        return False
    
    async def process_streaming(self, 
                              audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[bytes, None]:
        """串流處理 - 預設為逐塊處理"""
        async for chunk in audio_stream:
            yield self.process(chunk)
```

## 3. 管理器類設計

### Configuration Manager

```python
import configparser
from typing import Dict, List, Optional, Any

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
    
    def get_default_asr_engine(self) -> str:
        return self.config.get("DEFAULT", "asr_engine", fallback="funasr")
    
    def get_default_preprocessors(self) -> List[str]:
        processors_str = self.config.get("DEFAULT", "preprocessors", fallback="")
        return [p.strip() for p in processors_str.split(",") if p.strip()]
    
    def get_asr_config(self, engine_name: str) -> Dict[str, Any]:
        section = f"asr.{engine_name}"
        return dict(self.config.items(section)) if self.config.has_section(section) else {}
    
    def get_preprocessor_config(self, processor_name: str) -> Dict[str, Any]:
        section = f"preprocessor.{processor_name}"
        return dict(self.config.items(section)) if self.config.has_section(section) else {}
```

### Audio Pipeline Manager

```python
class AudioPipelineManager:
    """音訊處理管線管理器"""
    
    def __init__(self):
        self.preprocessors: Dict[str, AudioPreprocessor] = {}
    
    def register_preprocessor(self, processor: AudioPreprocessor):
        """註冊前處理器"""
        self.preprocessors[processor.name] = processor
    
    def create_pipeline(self, processor_names: List[str]) -> 'AudioPipeline':
        """創建處理管線"""
        processors = []
        for name in processor_names:
            if name in self.preprocessors:
                processors.append(self.preprocessors[name])
            else:
                raise ValueError(f"Preprocessor '{name}' not found")
        return AudioPipeline(processors)

class AudioPipeline:
    """音訊處理管線"""
    
    def __init__(self, processors: List[AudioPreprocessor]):
        self.processors = processors
    
    def process(self, audio_bytes: bytes) -> bytes:
        """處理音訊"""
        result = audio_bytes
        for processor in self.processors:
            result = processor.process(result)
        return result
    
    async def process_streaming(self, 
                              audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[bytes, None]:
        """串流處理"""
        current_stream = audio_stream
        for processor in self.processors:
            if processor.supports_streaming:
                current_stream = processor.process_streaming(current_stream)
            else:
                # 對於不支援串流的處理器，收集音訊後處理
                audio_buffer = b""
                async for chunk in current_stream:
                    audio_buffer += chunk
                processed = processor.process(audio_buffer)
                
                async def single_chunk_stream():
                    yield processed
                current_stream = single_chunk_stream()
        
        async for chunk in current_stream:
            yield chunk
```

## 4. Facade 服務

```python
class ASRFacadeService:
    """ASR Facade 服務"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.asr_engines: Dict[str, ASREngine] = {}
        self.pipeline_manager = AudioPipelineManager()
        self._setup_engines()
        self._setup_preprocessors()
    
    def _setup_engines(self):
        """設置 ASR 引擎"""
        # 這裡可以用工廠模式或註冊模式
        pass
    
    def _setup_preprocessors(self):
        """設置前處理器"""
        # 同上
        pass
    
    def transcribe(self, 
                  audio_bytes: bytes,
                  engine_name: Optional[str] = None,
                  preprocessors: Optional[List[str]] = None,
                  **kwargs) -> str:
        """離線轉譯"""
        
        # 選擇引擎
        engine_name = engine_name or self.config_manager.get_default_asr_engine()
        engine = self.asr_engines.get(engine_name)
        if not engine:
            raise ValueError(f"Engine '{engine_name}' not available")
        
        # 設置前處理管線
        preprocessor_names = preprocessors or self.config_manager.get_default_preprocessors()
        pipeline = self.pipeline_manager.create_pipeline(preprocessor_names)
        
        # 處理音訊
        processed_audio = pipeline.process(audio_bytes)
        
        # 轉譯
        return engine.transcribe(processed_audio, **kwargs)
    
    async def transcribe_streaming(self,
                                 audio_stream: AsyncGenerator[bytes, None],
                                 engine_name: Optional[str] = None,
                                 preprocessors: Optional[List[str]] = None,
                                 **kwargs) -> AsyncGenerator[str, None]:
        """串流轉譯"""
        
        # 選擇引擎
        engine_name = engine_name or self.config_manager.get_default_asr_engine()
        engine = self.asr_engines.get(engine_name)
        if not engine:
            raise ValueError(f"Engine '{engine_name}' not available")
        
        # 設置前處理管線
        preprocessor_names = preprocessors or self.config_manager.get_default_preprocessors()
        pipeline = self.pipeline_manager.create_pipeline(preprocessor_names)
        
        # 處理音訊流
        processed_stream = pipeline.process_streaming(audio_stream)
        
        # 轉譯
        async for result in engine.transcribe_streaming(processed_stream, **kwargs):
            yield result
```

## 5. 配置檔案範例

```ini
[DEFAULT]
asr_engine = funasr
preprocessors = noise_reduce, voice_enhance

[asr.funasr]
model_path = /models/funasr/speech_paraformer-large
device = cuda

[asr.whisper]
model_size = base
device = cuda

[asr.google_api]
api_key = ${GOOGLE_API_KEY}
language_code = zh-CN

[preprocessor.noise_reduce]
type = rnnoise
model_path = /models/rnnoise/model.bin

[preprocessor.voice_enhance] 
type = basic_enhancer
gain_db = 3.0
```

## 6. RESTful API 範例 (FastAPI)

```python
from fastapi import FastAPI, UploadFile, Query
from typing import Optional, List

app = FastAPI()
facade_service = ASRFacadeService(ConfigManager())

@app.post("/transcribe")
async def transcribe(
    audio: UploadFile,
    engine: Optional[str] = Query(None),
    preprocessors: Optional[str] = Query(None)
):
    """一次性轉譯"""
    audio_bytes = await audio.read()
    preprocessor_list = preprocessors.split(",") if preprocessors else None
    
    result = facade_service.transcribe(
        audio_bytes=audio_bytes,
        engine_name=engine,
        preprocessors=preprocessor_list
    )
    
    return {"transcript": result}

@app.websocket("/transcribe_stream")
async def transcribe_stream(websocket: WebSocket):
    """串流轉譯"""
    await websocket.accept()
    
    async def audio_stream():
        while True:
            data = await websocket.receive_bytes()
            if not data:
                break
            yield data
    
    async for result in facade_service.transcribe_streaming(audio_stream()):
        await websocket.send_text(result)
```

## 7. 設計優勢

1. **KISS 原則**：核心概念簡單，每個類職責單一
2. **擴展性**：新增 ASR 引擎或前處理器只需實作介面
3. **彈性配置**：支援預設配置和動態指定
4. **漸進式開發**：可以先實作離線功能，再擴展串流
5. **通訊協定無關**：Facade 層與通訊層分離
6. **容錯性**：提供後備方案，降低複雜度

這個設計在保持簡潔的同時，提供了足夠的擴展性和彈性。