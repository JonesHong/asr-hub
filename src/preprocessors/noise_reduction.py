"""基礎降噪前處理器"""

import numpy as np
from typing import Dict, Any
from .base import AudioPreprocessor
from ..utils.audio import bytes_to_numpy, convert_to_mono, numpy_to_bytes, normalize_audio
from ..utils.exceptions import AudioProcessingError


class NoiseReductionProcessor(AudioPreprocessor):
    """基礎降噪前處理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化降噪處理器
        
        Args:
            config: 處理器配置
        """
        self.enabled = config.get('enabled', True)
        self.strength = float(config.get('strength', 0.5))  # 降噪強度 0.0-1.0
        self.sample_rate = int(config.get('sample_rate', 16000))
        self.frame_length = int(config.get('frame_length', 2048))
        self.hop_length = int(config.get('hop_length', 512))
        super().__init__(config)
    
    def _initialize(self):
        """初始化處理器"""
        # 驗證參數
        if not 0.0 <= self.strength <= 1.0:
            raise AudioProcessingError("降噪強度必須在 0.0 到 1.0 之間")
        
        if self.sample_rate <= 0:
            raise AudioProcessingError("採樣率必須大於 0")
    
    @property
    def name(self) -> str:
        """返回處理器名稱"""
        return "noise_reduction"
    
    def process(self, audio_bytes: bytes, original_sample_rate: int = None, original_channels: int = None) -> bytes:
        """處理音訊進行降噪
        
        Args:
            audio_bytes: 原始音訊資料
            original_sample_rate: 原始採樣率
            original_channels: 原始聲道數
            
        Returns:
            降噪後的音訊資料
            
        Raises:
            AudioProcessingError: 處理失敗
        """
        if not self.enabled:
            return audio_bytes
        
        try:
            # 使用原始參數或預設值
            sample_rate = original_sample_rate or self.sample_rate
            channels = original_channels or 1
            
            # 轉換為 numpy array
            audio_array, _, _ = bytes_to_numpy(audio_bytes, sample_rate, channels)
            
            # 如果是多聲道，轉為單聲道處理
            if len(audio_array.shape) > 1:
                mono_array = convert_to_mono(audio_array)
            else:
                mono_array = audio_array
            
            # 執行降噪
            processed_mono = self._apply_noise_reduction(mono_array)
            
            # 如果原始是多聲道，復原多聲道（簡單複製）
            if len(audio_array.shape) > 1 and channels > 1:
                processed_array = np.column_stack([processed_mono] * channels)
            else:
                processed_array = processed_mono
            
            # 轉換回 bytes
            return numpy_to_bytes(processed_array)
            
        except Exception as e:
            raise AudioProcessingError(f"降噪處理失敗: {str(e)}")
    
    def _apply_noise_reduction(self, audio_array: np.ndarray) -> np.ndarray:
        """應用降噪算法
        
        Args:
            audio_array: 音訊 numpy array
            
        Returns:
            降噪後的音訊 array
        """
        # 基礎降噪實作：頻譜減法方法的簡化版本
        
        # 1. 計算音訊的能量
        energy = np.abs(audio_array)
        
        # 2. 估計噪音水平（使用前面一小段音訊）
        noise_sample_size = min(len(audio_array) // 10, self.sample_rate // 2)
        if noise_sample_size > 0:
            noise_level = np.mean(energy[:noise_sample_size])
        else:
            noise_level = np.mean(energy) * 0.1
        
        # 3. 計算動態閾值
        threshold = noise_level * (1 + self.strength)
        
        # 4. 應用軟閾值降噪
        mask = self._create_soft_mask(energy, threshold)
        processed_audio = audio_array * mask
        
        # 5. 平滑處理避免突然的音量變化
        processed_audio = self._apply_smoothing(processed_audio)
        
        return processed_audio
    
    def _create_soft_mask(self, energy: np.ndarray, threshold: float) -> np.ndarray:
        """創建軟遮罩進行平滑降噪
        
        Args:
            energy: 音訊能量
            threshold: 閾值
            
        Returns:
            軟遮罩 array
        """
        # 軟閾值函數：漸進式降噪而非硬切
        ratio = energy / (threshold + 1e-8)  # 避免除零
        
        # 使用 sigmoid 函數創建平滑遮罩
        mask = 1.0 / (1.0 + np.exp(-5 * (ratio - 1)))
        
        # 確保遮罩值在合理範圍內
        mask = np.clip(mask, 0.1, 1.0)  # 保留至少 10% 的原始信號
        
        return mask
    
    def _apply_smoothing(self, audio_array: np.ndarray) -> np.ndarray:
        """應用平滑處理
        
        Args:
            audio_array: 音訊 array
            
        Returns:
            平滑後的音訊 array
        """
        # 簡單的移動平均平滑
        window_size = max(3, int(self.sample_rate * 0.001))  # 1ms 窗口
        
        if len(audio_array) <= window_size:
            return audio_array
        
        # 使用 numpy 的卷積進行移動平均
        kernel = np.ones(window_size) / window_size
        
        # 處理邊界問題
        padded_audio = np.pad(audio_array, window_size//2, mode='edge')
        smoothed = np.convolve(padded_audio, kernel, mode='valid')
        
        return smoothed[:len(audio_array)]


class AudioNormalizer(AudioPreprocessor):
    """音訊格式標準化處理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化標準化處理器
        
        Args:
            config: 處理器配置
        """
        self.target_sample_rate = int(config.get('target_sample_rate', 16000))
        self.target_channels = int(config.get('target_channels', 1))
        self.normalize_volume = config.get('normalize_volume', True)
        self.target_volume = float(config.get('target_volume', 0.8))  # 目標音量 0.0-1.0
        super().__init__(config)
    
    def _initialize(self):
        """初始化處理器"""
        if self.target_sample_rate <= 0:
            raise AudioProcessingError("目標採樣率必須大於 0")
        
        if self.target_channels not in [1, 2]:
            raise AudioProcessingError("目標聲道數必須是 1 或 2")
        
        if not 0.0 <= self.target_volume <= 1.0:
            raise AudioProcessingError("目標音量必須在 0.0 到 1.0 之間")
    
    @property
    def name(self) -> str:
        """返回處理器名稱"""
        return "audio_normalizer"
    
    def process(self, audio_bytes: bytes, original_sample_rate: int = None, original_channels: int = None) -> bytes:
        """標準化音訊格式
        
        Args:
            audio_bytes: 原始音訊資料
            original_sample_rate: 原始採樣率
            original_channels: 原始聲道數
            
        Returns:
            標準化後的音訊資料
            
        Raises:
            AudioProcessingError: 處理失敗
        """
        try:
            # 如果不提供原始參數，直接返回
            if original_sample_rate is None or original_channels is None:
                if self.normalize_volume:
                    return self._normalize_volume(audio_bytes)
                return audio_bytes
            
            # 檢查是否需要轉換
            need_conversion = (
                original_sample_rate != self.target_sample_rate or 
                original_channels != self.target_channels
            )
            
            if need_conversion:
                # 基本格式標準化
                normalized_bytes = normalize_audio(
                    audio_bytes, 
                    original_sample_rate,
                    original_channels,
                    self.target_sample_rate, 
                    self.target_channels
                )
            else:
                normalized_bytes = audio_bytes
            
            # 音量標準化
            if self.normalize_volume:
                normalized_bytes = self._normalize_volume(normalized_bytes)
            
            return normalized_bytes
            
        except Exception as e:
            raise AudioProcessingError(f"音訊標準化失敗: {str(e)}")
    
    def _normalize_volume(self, audio_bytes: bytes) -> bytes:
        """標準化音量
        
        Args:
            audio_bytes: 音訊資料
            
        Returns:
            音量標準化後的音訊資料
        """
        try:
            # 轉換為 numpy array - 使用目標格式
            audio_array, _, _ = bytes_to_numpy(audio_bytes, self.target_sample_rate, self.target_channels)
            
            # 計算當前最大音量
            current_max = np.max(np.abs(audio_array))
            
            if current_max > 0:
                # 計算縮放因子
                target_max = self.target_volume * np.iinfo(np.int16).max
                scale_factor = target_max / current_max
                
                # 應用縮放，但避免超出範圍
                if scale_factor > 1.0:
                    scale_factor = min(scale_factor, target_max / current_max)
                
                normalized_array = audio_array * scale_factor
                
                # 確保在有效範圍內
                normalized_array = np.clip(
                    normalized_array, 
                    np.iinfo(np.int16).min, 
                    np.iinfo(np.int16).max
                )
            else:
                normalized_array = audio_array
            
            return numpy_to_bytes(normalized_array.astype(np.int16))
            
        except Exception as e:
            raise AudioProcessingError(f"音量標準化失敗: {str(e)}")