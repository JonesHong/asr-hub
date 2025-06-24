from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator


class AudioPreprocessor(ABC):
    """音訊前處理器抽象基類"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化前處理器
        
        Args:
            config: 前處理器配置字典
        """
        self.config = config
        self._initialize()
    
    @abstractmethod
    def _initialize(self):
        """初始化前處理器"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """返回前處理器名稱"""
        pass
    
    @abstractmethod
    def process(self, audio_bytes: bytes, **kwargs) -> bytes:
        """處理音訊資料
        
        Args:
            audio_bytes: 原始音訊資料
            **kwargs: 額外參數（如 original_sample_rate, original_channels）
            
        Returns:
            處理後的音訊資料
        """
        pass
    
    @property
    def supports_streaming(self) -> bool:
        """是否支援串流處理
        
        Returns:
            True 如果支援串流，否則 False
        """
        return False
    
    async def process_streaming(self, 
                              audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[bytes, None]:
        """串流處理音訊
        
        Args:
            audio_stream: 音訊串流
            
        Yields:
            處理後的音訊片段
        """
        if self.supports_streaming:
            # 如果支援串流，子類必須實作
            raise NotImplementedError(f"{self.name} 必須實作 process_streaming 方法")
        
        # 預設行為：逐塊處理
        async for chunk in audio_stream:
            yield self.process(chunk)