from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator


class ASREngine(ABC):
    """ASR 引擎抽象基類"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 ASR 引擎
        
        Args:
            config: 引擎配置字典
        """
        self.config = config
        self._initialize()
    
    @abstractmethod
    def _initialize(self):
        """初始化引擎（載入模型等）"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """返回引擎名稱"""
        pass
    
    @abstractmethod
    def transcribe(self, audio_bytes: bytes, **kwargs) -> str:
        """離線轉譯音訊
        
        Args:
            audio_bytes: 音訊資料（bytes格式）
            **kwargs: 其他參數
            
        Returns:
            轉譯結果文字
        """
        pass
    
    @property
    def supports_streaming(self) -> bool:
        """是否支援串流轉譯
        
        Returns:
            True 如果支援串流，否則 False
        """
        return False
    
    async def transcribe_streaming(self, 
                                 audio_stream: AsyncGenerator[bytes, None], 
                                 **kwargs) -> AsyncGenerator[str, None]:
        """串流轉譯音訊
        
        Args:
            audio_stream: 音訊串流
            **kwargs: 其他參數
            
        Yields:
            轉譯結果文字片段
        """
        if not self.supports_streaming:
            # 後備方案：收集全部音訊後一次轉譯
            audio_buffer = b""
            async for chunk in audio_stream:
                audio_buffer += chunk
            
            if audio_buffer:
                result = self.transcribe(audio_buffer, **kwargs)
                yield result
            return
        
        # 如果引擎聲稱支援串流，必須覆寫此方法
        raise NotImplementedError(f"{self.name} 必須實作 transcribe_streaming 方法")