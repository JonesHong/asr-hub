"""音訊處理管線"""

from typing import List, AsyncGenerator
from ..preprocessors.base import AudioPreprocessor
from ..utils.exceptions import PreprocessorError, AudioProcessingError


class AudioPipeline:
    """音訊處理管線 - 處理器鏈"""
    
    def __init__(self, processors: List[AudioPreprocessor]):
        """初始化處理管線
        
        Args:
            processors: 前處理器列表（按執行順序）
        """
        self.processors = processors
    
    
    def process(self, audio_bytes: bytes, **kwargs) -> bytes:
        """處理音訊資料
        
        Args:
            audio_bytes: 原始音訊資料
            **kwargs: 音訊參數（如 original_sample_rate, original_channels）
            
        Returns:
            處理後的音訊資料
            
        Raises:
            AudioProcessingError: 處理過程中發生錯誤
        """
        try:
            result = audio_bytes
            for processor in self.processors:
                result = processor.process(result, **kwargs)
            return result
        except Exception as e:
            raise AudioProcessingError(f"音訊處理管線執行失敗: {str(e)}")
    
    async def process_streaming(self, 
                              audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[bytes, None]:
        """串流處理音訊
        
        Args:
            audio_stream: 音訊串流
            
        Yields:
            處理後的音訊片段
        """
        try:
            current_stream = audio_stream
            
            # 依序通過每個處理器
            for processor in self.processors:
                current_stream = processor.process_streaming(current_stream)
            
            # 輸出最終結果
            async for chunk in current_stream:
                yield chunk
                
        except Exception as e:
            raise AudioProcessingError(f"串流音訊處理管線執行失敗: {str(e)}")
    
    def __len__(self) -> int:
        """返回管線中處理器的數量"""
        return len(self.processors)
    
    def __str__(self) -> str:
        """返回管線描述"""
        if not self.processors:
            return "Empty Pipeline"
        
        processor_names = [p.name for p in self.processors]
        return f"Pipeline: {' -> '.join(processor_names)}"


class AudioPipelineManager:
    """音訊處理管線管理器"""
    
    def __init__(self):
        """初始化管線管理器"""
        self.registered_processors = {}
    
    def register_processor(self, processor: AudioPreprocessor):
        """註冊前處理器
        
        Args:
            processor: 前處理器實例
        """
        self.registered_processors[processor.name] = processor
    
    def get_processor(self, name: str) -> AudioPreprocessor:
        """獲取前處理器
        
        Args:
            name: 處理器名稱
            
        Returns:
            前處理器實例
            
        Raises:
            PreprocessorError: 找不到指定的處理器
        """
        if name not in self.registered_processors:
            raise PreprocessorError(f"找不到前處理器: {name}")
        return self.registered_processors[name]
    
    def create_pipeline(self, processor_names: List[str]) -> AudioPipeline:
        """創建處理管線
        
        Args:
            processor_names: 處理器名稱列表（按執行順序）
            
        Returns:
            音訊處理管線實例
            
        Raises:
            PreprocessorError: 處理器不存在
        """
        if not processor_names:
            return AudioPipeline([])
        
        processors = []
        for name in processor_names:
            processor = self.get_processor(name)
            processors.append(processor)
        
        return AudioPipeline(processors)
    
    def list_processors(self) -> List[str]:
        """列出所有已註冊的處理器名稱
        
        Returns:
            處理器名稱列表
        """
        return list(self.registered_processors.keys())
    
    def is_registered(self, name: str) -> bool:
        """檢查處理器是否已註冊
        
        Args:
            name: 處理器名稱
            
        Returns:
            True 如果已註冊，否則 False
        """
        return name in self.registered_processors
    