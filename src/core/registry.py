"""組件註冊機制"""

from typing import Dict, Type, Any
from ..engines.base import ASREngine
from ..preprocessors.base import AudioPreprocessor
from ..utils.exceptions import EngineNotFoundError, PreprocessorNotFoundError


class ComponentRegistry:
    """組件註冊表 - 管理 ASR 引擎和前處理器的註冊"""
    
    def __init__(self):
        """初始化註冊表"""
        self.engine_classes: Dict[str, Type[ASREngine]] = {}
        self.preprocessor_classes: Dict[str, Type[AudioPreprocessor]] = {}
    
    def register_engine(self, name: str, engine_class: Type[ASREngine]):
        """註冊 ASR 引擎類
        
        Args:
            name: 引擎名稱
            engine_class: 引擎類
        """
        self.engine_classes[name] = engine_class
    
    def register_preprocessor(self, name: str, preprocessor_class: Type[AudioPreprocessor]):
        """註冊前處理器類
        
        Args:
            name: 處理器名稱
            preprocessor_class: 處理器類
        """
        self.preprocessor_classes[name] = preprocessor_class
    
    def create_engine(self, name: str, config: Dict[str, Any]) -> ASREngine:
        """創建 ASR 引擎實例
        
        Args:
            name: 引擎名稱
            config: 引擎配置
            
        Returns:
            ASR 引擎實例
            
        Raises:
            EngineNotFoundError: 找不到指定的引擎
        """
        if name not in self.engine_classes:
            raise EngineNotFoundError(f"找不到 ASR 引擎: {name}")
        
        engine_class = self.engine_classes[name]
        return engine_class(config)
    
    def create_preprocessor(self, name: str, config: Dict[str, Any]) -> AudioPreprocessor:
        """創建前處理器實例
        
        Args:
            name: 處理器名稱
            config: 處理器配置
            
        Returns:
            前處理器實例
            
        Raises:
            PreprocessorNotFoundError: 找不到指定的處理器
        """
        if name not in self.preprocessor_classes:
            raise PreprocessorNotFoundError(f"找不到前處理器: {name}")
        
        preprocessor_class = self.preprocessor_classes[name]
        return preprocessor_class(config)
    
    def list_engines(self) -> list:
        """列出所有已註冊的引擎名稱
        
        Returns:
            引擎名稱列表
        """
        return list(self.engine_classes.keys())
    
    def list_preprocessors(self) -> list:
        """列出所有已註冊的處理器名稱
        
        Returns:
            處理器名稱列表
        """
        return list(self.preprocessor_classes.keys())
    
    def is_engine_registered(self, name: str) -> bool:
        """檢查引擎是否已註冊
        
        Args:
            name: 引擎名稱
            
        Returns:
            True 如果已註冊，否則 False
        """
        return name in self.engine_classes
    
    def is_preprocessor_registered(self, name: str) -> bool:
        """檢查處理器是否已註冊
        
        Args:
            name: 處理器名稱
            
        Returns:
            True 如果已註冊，否則 False
        """
        return name in self.preprocessor_classes


# 全域註冊表實例
registry = ComponentRegistry()