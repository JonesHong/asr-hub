"""音訊處理工具函數"""

import numpy as np
from typing import Tuple, Optional
from .exceptions import InvalidAudioFormatError, AudioProcessingError


def bytes_to_numpy(audio_bytes: bytes, 
                  sample_rate: int = 16000, 
                  channels: int = 1,
                  dtype: str = 'int16') -> tuple:
    """將音訊 bytes 轉換為 numpy array
    
    Args:
        audio_bytes: 音訊資料（bytes格式）
        sample_rate: 採樣率
        channels: 聲道數
        dtype: 資料類型
        
    Returns:
        tuple: (audio_array, actual_sample_rate, actual_channels)
        
    Raises:
        InvalidAudioFormatError: 音訊格式無效
    """
    try:
        if dtype == 'int16':
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        elif dtype == 'float32':
            audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
        else:
            raise InvalidAudioFormatError(f"不支援的資料類型: {dtype}")
        
        # 如果是多聲道，重新整形
        if channels > 1:
            if len(audio_array) % channels != 0:
                # 截斷到正確的長度
                audio_array = audio_array[:-(len(audio_array) % channels)]
            audio_array = audio_array.reshape(-1, channels)
            
        return audio_array, sample_rate, channels
    except Exception as e:
        raise InvalidAudioFormatError(f"音訊格式轉換失敗: {str(e)}")


def numpy_to_bytes(audio_array: np.ndarray, dtype: str = 'int16') -> bytes:
    """將 numpy array 轉換為音訊 bytes
    
    Args:
        audio_array: numpy array 格式的音訊資料
        dtype: 目標資料類型
        
    Returns:
        bytes 格式的音訊資料
        
    Raises:
        InvalidAudioFormatError: 轉換失敗
    """
    try:
        # 確保 array 是連續的
        if not audio_array.flags.c_contiguous:
            audio_array = np.ascontiguousarray(audio_array)
            
        if dtype == 'int16':
            return audio_array.astype(np.int16).tobytes()
        elif dtype == 'float32':
            return audio_array.astype(np.float32).tobytes()
        else:
            raise InvalidAudioFormatError(f"不支援的資料類型: {dtype}")
    except Exception as e:
        raise InvalidAudioFormatError(f"音訊格式轉換失敗: {str(e)}")


def convert_to_mono(audio_array: np.ndarray) -> np.ndarray:
    """將多聲道音訊轉為單聲道
    
    Args:
        audio_array: 音訊陣列，可能是多聲道
        
    Returns:
        單聲道音訊陣列
    """
    if len(audio_array.shape) == 1:
        return audio_array  # 已經是單聲道
    elif len(audio_array.shape) == 2:
        # 多聲道取平均
        return np.mean(audio_array, axis=1).astype(audio_array.dtype)
    else:
        raise AudioProcessingError(f"不支援的音訊陣列形狀: {audio_array.shape}")


def normalize_audio(audio_bytes: bytes, 
                   original_sample_rate: int,
                   original_channels: int,
                   target_sample_rate: int = 16000,
                   target_channels: int = 1) -> bytes:
    """標準化音訊格式
    
    Args:
        audio_bytes: 原始音訊資料
        original_sample_rate: 原始採樣率
        original_channels: 原始聲道數
        target_sample_rate: 目標採樣率
        target_channels: 目標聲道數
        
    Returns:
        標準化後的音訊資料
        
    Raises:
        AudioProcessingError: 處理失敗
    """
    try:
        # 將 bytes 轉為 numpy array
        audio_array, _, _ = bytes_to_numpy(audio_bytes, original_sample_rate, original_channels)
        
        # 轉換聲道數
        if original_channels > 1 and target_channels == 1:
            audio_array = convert_to_mono(audio_array)
        elif original_channels == 1 and target_channels > 1:
            # 單聲道轉多聲道（複製）
            audio_array = np.column_stack([audio_array] * target_channels)
        
        # 簡單的採樣率轉換（線性插值）
        if original_sample_rate != target_sample_rate:
            audio_array = _resample_audio(audio_array, original_sample_rate, target_sample_rate)
        
        return numpy_to_bytes(audio_array)
    except Exception as e:
        raise AudioProcessingError(f"音訊標準化失敗: {str(e)}")


def _resample_audio(audio_array: np.ndarray, 
                   original_rate: int, 
                   target_rate: int) -> np.ndarray:
    """簡單的音訊重採樣
    
    Args:
        audio_array: 原始音訊陣列
        original_rate: 原始採樣率
        target_rate: 目標採樣率
        
    Returns:
        重採樣後的音訊陣列
    """
    if original_rate == target_rate:
        return audio_array
    
    # 計算新的長度
    ratio = target_rate / original_rate
    new_length = int(len(audio_array) * ratio)
    
    # 線性插值重採樣
    old_indices = np.linspace(0, len(audio_array) - 1, len(audio_array))
    new_indices = np.linspace(0, len(audio_array) - 1, new_length)
    
    # 如果是多聲道
    if len(audio_array.shape) > 1:
        resampled = np.zeros((new_length, audio_array.shape[1]), dtype=audio_array.dtype)
        for channel in range(audio_array.shape[1]):
            resampled[:, channel] = np.interp(new_indices, old_indices, audio_array[:, channel])
    else:
        resampled = np.interp(new_indices, old_indices, audio_array)
    
    return resampled.astype(audio_array.dtype)


def get_audio_info(audio_bytes: bytes, sample_rate: int = 16000, channels: int = 1) -> dict:
    """獲取音訊基本資訊
    
    Args:
        audio_bytes: 音訊資料
        sample_rate: 採樣率
        channels: 聲道數
        
    Returns:
        包含音訊資訊的字典
    """
    try:
        audio_array, _, _ = bytes_to_numpy(audio_bytes, sample_rate, channels)
        
        info = {
            'duration_samples': len(audio_array),
            'duration_seconds': len(audio_array) / sample_rate,
            'channels': channels,
            'sample_rate': sample_rate,
            'dtype': str(audio_array.dtype),
            'size_bytes': len(audio_bytes)
        }
        
        return info
    except Exception as e:
        return {'error': str(e)}


def validate_audio_format(audio_bytes: bytes, 
                         min_size: int = 1024,
                         max_size: Optional[int] = None) -> bool:
    """驗證音訊格式是否有效
    
    Args:
        audio_bytes: 音訊資料
        min_size: 最小檔案大小（bytes）
        max_size: 最大檔案大小（bytes），None 表示不限制
        
    Returns:
        True 如果格式有效，否則 False
    """
    try:
        if len(audio_bytes) < min_size:
            return False
            
        if max_size and len(audio_bytes) > max_size:
            return False
            
        # 嘗試轉換為 numpy array 來驗證格式
        bytes_to_numpy(audio_bytes)
        return True
    except Exception:
        return False