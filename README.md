# ASR Core

A universal Python ASR (Automatic Speech Recognition) framework supporting multiple engines with flexible audio preprocessing pipelines.

## Features

- **Multiple ASR Engines**: Support for FunASR, Whisper, Vosk, Google API, Microsoft API, OpenAI API
- **Flexible Preprocessing**: Configurable audio preprocessing pipeline (noise reduction, voice enhancement)
- **Multiple Modes**: Both offline and streaming transcription
- **Multiple Protocols**: RESTful API, WebSocket, Redis, gRPC support
- **Configuration-Driven**: Easy configuration management with INI files
- **Extensible**: Simple to add new engines and preprocessors

## Installation

```bash
git clone https://github.com/yourusername/asr-core.git
cd asr-core
pip install -r requirements.txt
```

## Quick Start

```python
from src.core.facade import ASRFacadeService
from src.config.manager import ConfigManager

# Initialize
config = ConfigManager()
asr_service = ASRFacadeService(config)

# Transcribe audio
with open("audio.wav", "rb") as f:
    audio_bytes = f.read()
    
result = asr_service.transcribe(audio_bytes)
print(result)
```

## Configuration

See `config/config.ini` for configuration options.

## Development Status

This project is in active development. See `todo_list.md` for current progress.

## License

MIT License