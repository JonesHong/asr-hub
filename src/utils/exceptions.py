"""ASR Core 自定義異常類"""


class ASRCoreError(Exception):
    """ASR Core 基礎異常類"""
    pass


class ConfigurationError(ASRCoreError):
    """配置相關錯誤"""
    pass


class EngineError(ASRCoreError):
    """ASR 引擎相關錯誤"""
    pass


class EngineNotFoundError(EngineError):
    """找不到指定的 ASR 引擎"""
    pass


class EngineInitializationError(EngineError):
    """ASR 引擎初始化失敗"""
    pass


class TranscriptionError(EngineError):
    """轉譯過程錯誤"""
    pass


class PreprocessorError(ASRCoreError):
    """前處理器相關錯誤"""
    pass


class PreprocessorNotFoundError(PreprocessorError):
    """找不到指定的前處理器"""
    pass


class AudioProcessingError(PreprocessorError):
    """音訊處理錯誤"""
    pass


class APIError(ASRCoreError):
    """API 相關錯誤"""
    pass


class InvalidAudioFormatError(ASRCoreError):
    """無效的音訊格式"""
    pass


class ServiceUnavailableError(ASRCoreError):
    """服務不可用"""
    pass