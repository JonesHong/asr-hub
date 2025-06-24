"""Whisper ASR 引擎實作"""

import whisper
import io
import tempfile
import os
from typing import Dict, Any, AsyncGenerator
from .base import ASREngine
from ..utils.exceptions import EngineInitializationError, TranscriptionError


class WhisperEngine(ASREngine):
    """Whisper ASR 引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 Whisper 引擎
        
        Args:
            config: 引擎配置
        """
        self.model = None
        self.model_size = config.get('model_size', 'base')
        self.device = config.get('device', 'auto')
        self.language = config.get('language', 'auto')
        super().__init__(config)
    
    def _initialize(self):
        """初始化 Whisper 模型"""
        try:
            # 載入 Whisper 模型
            self.model = whisper.load_model(
                name=self.model_size,
                device=self.device if self.device != 'auto' else None
            )
        except Exception as e:
            raise EngineInitializationError(f"Whisper 模型載入失敗: {str(e)}")
    
    @property
    def name(self) -> str:
        """返回引擎名稱"""
        return "whisper"
    
    def transcribe(self, audio_bytes: bytes, **kwargs) -> str:
        """轉譯音訊
        
        Args:
            audio_bytes: 音訊資料
            **kwargs: 其他參數（如 language）
            
        Returns:
            轉譯結果文字
            
        Raises:
            TranscriptionError: 轉譯失敗
        """
        if not self.model:
            raise TranscriptionError("Whisper 模型未初始化")
        
        try:
            # 創建臨時檔案來儲存音訊
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            try:
                # 設定轉譯選項
                options = {
                    'language': kwargs.get('language', self.language),
                    'task': kwargs.get('task', 'transcribe'),
                    'fp16': kwargs.get('fp16', False)
                }
                
                # 如果語言設定為 auto，則不指定語言讓 Whisper 自動偵測
                if options['language'] == 'auto':
                    options.pop('language')
                
                # 進行轉譯
                result = self.model.transcribe(temp_file_path, **options)
                
                return result['text'].strip()
                
            finally:
                # 清理臨時檔案
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            raise TranscriptionError(f"Whisper 轉譯失敗: {str(e)}")
    
    @property
    def supports_streaming(self) -> bool:
        """Whisper 原生不支援串流，使用後備方案"""
        return False
    
    async def transcribe_streaming(self, 
                                 audio_stream: AsyncGenerator[bytes, None], 
                                 **kwargs) -> AsyncGenerator[str, None]:
        """串流轉譯（後備方案）
        
        Args:
            audio_stream: 音訊串流
            **kwargs: 其他參數
            
        Yields:
            轉譯結果
        """
        # 使用父類的後備實作：收集全部音訊後一次轉譯
        async for result in super().transcribe_streaming(audio_stream, **kwargs):
            yield result
    
    def detect_language(self, audio_bytes: bytes) -> str:
        """偵測音訊語言
        
        Args:
            audio_bytes: 音訊資料
            
        Returns:
            偵測到的語言代碼
            
        Raises:
            TranscriptionError: 語言偵測失敗
        """
        if not self.model:
            raise TranscriptionError("Whisper 模型未初始化")
        
        try:
            # 創建臨時檔案
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            try:
                # 載入音訊並處理
                audio = whisper.load_audio(temp_file_path)
                audio = whisper.pad_or_trim(audio)
                
                # 產生 Mel 頻譜圖
                mel = whisper.log_mel_spectrogram(
                    audio, 
                    n_mels=self.model.dims.n_mels
                ).to(self.model.device)
                
                # 偵測語言
                _, probs = self.model.detect_language(mel)
                detected_language = max(probs, key=probs.get)
                
                return detected_language
                
            finally:
                # 清理臨時檔案
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            raise TranscriptionError(f"語言偵測失敗: {str(e)}")
    
    def get_model_info(self) -> dict:
        """獲取模型資訊
        
        Returns:
            模型資訊字典
        """
        if not self.model:
            return {'status': 'not_initialized'}
        
        return {
            'model_size': self.model_size,
            'device': str(self.model.device),
            'dims': {
                'n_mels': self.model.dims.n_mels,
                'n_audio_ctx': self.model.dims.n_audio_ctx,
                'n_audio_state': self.model.dims.n_audio_state,
                'n_audio_head': self.model.dims.n_audio_head,
                'n_vocab': self.model.dims.n_vocab
            } if hasattr(self.model, 'dims') else {}
        }