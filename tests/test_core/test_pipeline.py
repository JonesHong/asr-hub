"""測試音訊處理管線功能"""

import pytest
from typing import Dict, Any
from src.core.pipeline import AudioPipeline, AudioPipelineManager
from src.core.registry import ComponentRegistry
from src.preprocessors.base import AudioPreprocessor
from src.utils.exceptions import PreprocessorError


class MockPreprocessor(AudioPreprocessor):
    """模擬前處理器，用於測試"""
    
    def __init__(self, config: Dict[str, Any]):
        self.test_name = config.get('name', 'mock')
        super().__init__(config)
    
    def _initialize(self):
        pass
    
    @property
    def name(self) -> str:
        return self.test_name
    
    def process(self, audio_bytes: bytes) -> bytes:
        # 簡單的測試處理：在音訊前加上處理器名稱
        return f"{self.name}:".encode() + audio_bytes


class TestAudioPipeline:
    """測試 AudioPipeline 類"""
    
    def test_empty_pipeline(self):
        """測試空管線"""
        pipeline = AudioPipeline([])
        test_audio = b"test_audio"
        
        result = pipeline.process(test_audio)
        assert result == test_audio
        assert len(pipeline) == 0
        assert str(pipeline) == "Empty Pipeline"
    
    def test_single_processor_pipeline(self):
        """測試單一處理器管線"""
        processor = MockPreprocessor({'name': 'test1'})
        pipeline = AudioPipeline([processor])
        
        test_audio = b"test_audio"
        result = pipeline.process(test_audio)
        
        assert result == b"test1:test_audio"
        assert len(pipeline) == 1
        assert str(pipeline) == "Pipeline: test1"
    
    def test_multiple_processors_pipeline(self):
        """測試多處理器管線"""
        processor1 = MockPreprocessor({'name': 'test1'})
        processor2 = MockPreprocessor({'name': 'test2'})
        pipeline = AudioPipeline([processor1, processor2])
        
        test_audio = b"test_audio"
        result = pipeline.process(test_audio)
        
        # 應該是 test2:test1:test_audio
        assert result == b"test2:test1:test_audio"
        assert len(pipeline) == 2
        assert str(pipeline) == "Pipeline: test1 -> test2"


class TestAudioPipelineManager:
    """測試 AudioPipelineManager 類"""
    
    def test_register_and_get_processor(self):
        """測試註冊和獲取處理器"""
        manager = AudioPipelineManager()
        processor = MockPreprocessor({'name': 'test'})
        
        manager.register_processor(processor)
        
        retrieved = manager.get_processor('test')
        assert retrieved == processor
        assert manager.is_registered('test')
        assert 'test' in manager.list_processors()
    
    def test_get_nonexistent_processor(self):
        """測試獲取不存在的處理器"""
        manager = AudioPipelineManager()
        
        with pytest.raises(PreprocessorError):
            manager.get_processor('nonexistent')
    
    def test_create_empty_pipeline(self):
        """測試創建空管線"""
        manager = AudioPipelineManager()
        pipeline = manager.create_pipeline([])
        
        assert len(pipeline) == 0
        assert isinstance(pipeline, AudioPipeline)
    
    def test_create_pipeline_with_processors(self):
        """測試創建含處理器的管線"""
        manager = AudioPipelineManager()
        
        processor1 = MockPreprocessor({'name': 'test1'})
        processor2 = MockPreprocessor({'name': 'test2'})
        
        manager.register_processor(processor1)
        manager.register_processor(processor2)
        
        pipeline = manager.create_pipeline(['test1', 'test2'])
        
        assert len(pipeline) == 2
        
        # 測試管線執行
        test_audio = b"test_audio"
        result = pipeline.process(test_audio)
        assert result == b"test2:test1:test_audio"
    
    def test_create_pipeline_with_nonexistent_processor(self):
        """測試創建包含不存在處理器的管線"""
        manager = AudioPipelineManager()
        
        with pytest.raises(PreprocessorError):
            manager.create_pipeline(['nonexistent'])


class TestComponentRegistry:
    """測試 ComponentRegistry 類"""
    
    def test_register_and_create_preprocessor(self):
        """測試註冊和創建前處理器"""
        registry = ComponentRegistry()
        
        registry.register_preprocessor('mock', MockPreprocessor)
        
        assert registry.is_preprocessor_registered('mock')
        assert 'mock' in registry.list_preprocessors()
        
        preprocessor = registry.create_preprocessor('mock', {'name': 'test'})
        assert isinstance(preprocessor, MockPreprocessor)
        assert preprocessor.name == 'test'


if __name__ == "__main__":
    # 簡單的測試執行
    test_pipeline = TestAudioPipeline()
    test_pipeline.test_empty_pipeline()
    test_pipeline.test_single_processor_pipeline()
    test_pipeline.test_multiple_processors_pipeline()
    print("✅ AudioPipeline 測試通過")
    
    test_manager = TestAudioPipelineManager()
    test_manager.test_register_and_get_processor()
    test_manager.test_create_empty_pipeline()
    test_manager.test_create_pipeline_with_processors()
    print("✅ AudioPipelineManager 測試通過")
    
    test_registry = TestComponentRegistry()
    test_registry.test_register_and_create_preprocessor()
    print("✅ ComponentRegistry 測試通過")
    
    print("🎉 所有測試通過！")