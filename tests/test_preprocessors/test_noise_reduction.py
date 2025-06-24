"""測試降噪前處理器"""

import pytest
import numpy as np
from src.preprocessors.noise_reduction import NoiseReductionProcessor, AudioNormalizer
from src.utils.audio import bytes_to_numpy, numpy_to_bytes
from src.utils.exceptions import AudioProcessingError


class TestNoiseReductionProcessor:
    """測試 NoiseReductionProcessor 類"""
    
    def setup_method(self):
        """設置測試"""
        self.config = {
            'enabled': True,
            'strength': 0.5,
            'sample_rate': 16000,
            'frame_length': 2048,
            'hop_length': 512
        }
    
    def test_initialization_success(self):
        """測試成功初始化"""
        processor = NoiseReductionProcessor(self.config)
        
        assert processor.name == "noise_reduction"
        assert processor.enabled == True
        assert processor.strength == 0.5
        assert processor.sample_rate == 16000
    
    def test_initialization_invalid_strength(self):
        """測試無效強度參數"""
        config = self.config.copy()
        config['strength'] = 1.5  # 超出範圍
        
        with pytest.raises(AudioProcessingError):
            NoiseReductionProcessor(config)
    
    def test_initialization_invalid_sample_rate(self):
        """測試無效採樣率"""
        config = self.config.copy()
        config['sample_rate'] = -1
        
        with pytest.raises(AudioProcessingError):
            NoiseReductionProcessor(config)
    
    def test_process_disabled(self):
        """測試停用時直接返回原始音訊"""
        config = self.config.copy()
        config['enabled'] = False
        
        processor = NoiseReductionProcessor(config)
        test_audio = b"test_audio_data"
        
        result = processor.process(test_audio, original_sample_rate=16000, original_channels=1)
        assert result == test_audio
    
    def test_process_with_noise_reduction(self):
        """測試降噪處理功能"""
        processor = NoiseReductionProcessor(self.config)
        
        # 創建測試音訊：正弦波 + 噪音
        duration = 0.5  # 0.5 秒
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # 純正弦波信號
        clean_signal = np.sin(2 * np.pi * 440 * t)  # 440Hz
        
        # 添加噪音
        noise = np.random.normal(0, 0.1, len(clean_signal))
        noisy_signal = clean_signal + noise
        
        # 轉換為 int16 並轉為 bytes
        noisy_signal_int16 = (noisy_signal * 32767).astype(np.int16)
        audio_bytes = noisy_signal_int16.tobytes()
        
        # 處理音訊
        result_bytes = processor.process(audio_bytes, 
                                       original_sample_rate=sample_rate, 
                                       original_channels=1)
        
        # 驗證結果
        assert isinstance(result_bytes, bytes)
        assert len(result_bytes) > 0
        
        # 轉換回 numpy 檢查
        result_array, _, _ = bytes_to_numpy(result_bytes, sample_rate, 1)
        assert len(result_array) == len(noisy_signal_int16)
    
    def test_create_soft_mask(self):
        """測試軟遮罩創建"""
        processor = NoiseReductionProcessor(self.config)
        
        # 測試能量和閾值
        energy = np.array([0.1, 0.5, 1.0, 2.0, 0.3])
        threshold = 0.8
        
        mask = processor._create_soft_mask(energy, threshold)
        
        assert len(mask) == len(energy)
        assert np.all(mask >= 0.1)  # 最小值應該是 0.1
        assert np.all(mask <= 1.0)  # 最大值應該是 1.0
        
        # 高能量部分應該有較高的遮罩值
        assert mask[3] > mask[0]  # energy[3]=2.0 > energy[0]=0.1
    
    def test_process_with_parameters(self):
        """測試帶參數的處理功能"""
        processor = NoiseReductionProcessor(self.config)
        
        # 創建測試音訊（立體聲）
        duration = 0.1
        sample_rate = 48000  # 不同採樣率
        channels = 2
        samples_per_channel = int(sample_rate * duration)
        
        # 創建立體聲信號
        t = np.linspace(0, duration, samples_per_channel)
        left_channel = np.sin(2 * np.pi * 440 * t)
        right_channel = np.sin(2 * np.pi * 880 * t)
        
        # 組合為立體聲
        stereo_signal = np.column_stack([left_channel, right_channel])
        stereo_int16 = (stereo_signal * 16000).astype(np.int16)
        audio_bytes = stereo_int16.tobytes()
        
        # 處理
        result_bytes = processor.process(audio_bytes, 
                                       original_sample_rate=sample_rate, 
                                       original_channels=channels)
        
        # 驗證結果
        assert isinstance(result_bytes, bytes)
        assert len(result_bytes) > 0
        
        # 檢查結果格式（應該轉回立體聲）
        result_array, _, _ = bytes_to_numpy(result_bytes, sample_rate, channels)
        assert result_array.shape == stereo_int16.shape
    
    def test_process_without_parameters(self):
        """測試不提供參數時的處理（應該使用預設值）"""
        processor = NoiseReductionProcessor(self.config)
        
        # 創建簡單測試音訊
        test_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 1600))
        test_int16 = (test_signal * 16000).astype(np.int16)
        audio_bytes = test_int16.tobytes()
        
        # 不傳遞參數的處理
        result_bytes = processor.process(audio_bytes)
        
        # 應該正常處理
        assert isinstance(result_bytes, bytes)
        assert len(result_bytes) > 0
        """測試平滑處理"""
        processor = NoiseReductionProcessor(self.config)
        
        # 創建有尖峰的信號
        audio_array = np.array([1.0, 1.0, 10.0, 1.0, 1.0] * 100)
        
        smoothed = processor._apply_smoothing(audio_array)
        
        assert len(smoothed) == len(audio_array)
        # 尖峰應該被平滑
        max_original = np.max(audio_array)
        max_smoothed = np.max(smoothed)
        assert max_smoothed < max_original


class TestAudioNormalizer:
    """測試 AudioNormalizer 類"""
    
    def setup_method(self):
        """設置測試"""
        self.config = {
            'target_sample_rate': 16000,
            'target_channels': 1,
            'normalize_volume': True,
            'target_volume': 0.8
        }
    
    def test_initialization_success(self):
        """測試成功初始化"""
        normalizer = AudioNormalizer(self.config)
        
        assert normalizer.name == "audio_normalizer"
        assert normalizer.target_sample_rate == 16000
        assert normalizer.target_channels == 1
        assert normalizer.normalize_volume == True
        assert normalizer.target_volume == 0.8
    
    def test_initialization_invalid_sample_rate(self):
        """測試無效採樣率"""
        config = self.config.copy()
        config['target_sample_rate'] = 0
        
        with pytest.raises(AudioProcessingError):
            AudioNormalizer(config)
    
    def test_initialization_invalid_channels(self):
        """測試無效聲道數"""
        config = self.config.copy()
        config['target_channels'] = 3  # 不支援
        
        with pytest.raises(AudioProcessingError):
            AudioNormalizer(config)
    
    def test_initialization_invalid_volume(self):
        """測試無效目標音量"""
        config = self.config.copy()
        config['target_volume'] = 1.5  # 超出範圍
        
        with pytest.raises(AudioProcessingError):
            AudioNormalizer(config)
    
    def test_process_normalization(self):
        """測試標準化處理"""
        normalizer = AudioNormalizer(self.config)
        
        # 創建測試音訊
        duration = 0.1
        original_sample_rate = 8000  # 與目標不同
        t = np.linspace(0, duration, int(original_sample_rate * duration))
        signal = np.sin(2 * np.pi * 440 * t)
        
        # 轉換為 int16
        signal_int16 = (signal * 16000).astype(np.int16)  # 較低音量
        audio_bytes = signal_int16.tobytes()
        
        # 處理 - 傳遞原始參數
        result_bytes = normalizer.process(audio_bytes, 
                                        original_sample_rate=original_sample_rate, 
                                        original_channels=1)
        
        # 驗證結果
        assert isinstance(result_bytes, bytes)
        assert len(result_bytes) > 0
        
        # 檢查標準化效果
        result_array, _, _ = bytes_to_numpy(result_bytes, normalizer.target_sample_rate, normalizer.target_channels)
        
        # 音量應該被提升（因為有音量標準化）
        original_max = np.max(np.abs(signal_int16))
        result_max = np.max(np.abs(result_array))
        assert result_max > original_max
    
    def test_process_no_conversion_needed(self):
        """測試不需要轉換時的處理"""
        # 配置目標格式與原始格式相同
        config = self.config.copy()
        config['target_sample_rate'] = 16000
        config['target_channels'] = 1
        
        normalizer = AudioNormalizer(config)
        
        # 創建測試音訊
        test_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 1600))
        test_int16 = (test_signal * 16000).astype(np.int16)
        audio_bytes = test_int16.tobytes()
        
        # 處理（格式相同，只做音量標準化）
        result_bytes = normalizer.process(audio_bytes, 
                                        original_sample_rate=16000, 
                                        original_channels=1)
        
        # 應該有結果（經過音量標準化）
        assert isinstance(result_bytes, bytes)
        assert len(result_bytes) > 0
    
    def test_process_without_original_params(self):
        """測試不提供原始參數時的處理"""
        normalizer = AudioNormalizer(self.config)
        
        # 創建測試音訊
        test_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 1600))
        test_int16 = (test_signal * 16000).astype(np.int16)
        audio_bytes = test_int16.tobytes()
        
        # 不提供原始參數（應該只做音量標準化）
        result_bytes = normalizer.process(audio_bytes)
        
        # 應該有結果
        assert isinstance(result_bytes, bytes)
        assert len(result_bytes) > 0
        """測試零信號的音量標準化"""
        normalizer = AudioNormalizer(self.config)
        
        # 創建零信號
        zero_signal = np.zeros(1000, dtype=np.int16)
        audio_bytes = zero_signal.tobytes()
        
        # 處理（不應該出錯）
        result_bytes = normalizer._normalize_volume(audio_bytes)
        result_array, _, _ = bytes_to_numpy(result_bytes, normalizer.target_sample_rate, normalizer.target_channels)
        
        # 結果應該仍然是零
        assert np.all(result_array == 0)


class TestPreprocessorIntegration:
    """前處理器整合測試"""
    
    def test_noise_reduction_and_normalization_pipeline(self):
        """測試降噪和標準化管線"""
        # 創建處理器
        noise_config = {
            'enabled': True,
            'strength': 0.3,
            'sample_rate': 16000
        }
        norm_config = {
            'target_sample_rate': 16000,
            'target_channels': 1,
            'normalize_volume': True,
            'target_volume': 0.7
        }
        
        noise_processor = NoiseReductionProcessor(noise_config)
        normalizer = AudioNormalizer(norm_config)
        
        # 創建測試音訊
        duration = 0.2
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        clean_signal = np.sin(2 * np.pi * 440 * t)
        noise = np.random.normal(0, 0.2, len(clean_signal))
        noisy_signal = clean_signal + noise
        
        # 轉換為 bytes
        noisy_signal_int16 = (noisy_signal * 16000).astype(np.int16)
        audio_bytes = noisy_signal_int16.tobytes()
        
        # 依序處理 - 傳遞正確的原始參數
        step1_result = noise_processor.process(audio_bytes, 
                                             original_sample_rate=sample_rate, 
                                             original_channels=1)
        final_result = normalizer.process(step1_result, 
                                        original_sample_rate=sample_rate, 
                                        original_channels=1)
        
        # 驗證最終結果
        assert isinstance(final_result, bytes)
        assert len(final_result) > 0
        
        final_array, _, _ = bytes_to_numpy(final_result, sample_rate, 1)
        assert len(final_array) > 0


if __name__ == "__main__":
    # 執行基本測試
    print("開始測試前處理器...")
    
    try:
        # 測試降噪處理器
        test_noise = TestNoiseReductionProcessor()
        test_noise.setup_method()
        test_noise.test_initialization_success()
        test_noise.test_process_with_noise_reduction()
        test_noise.test_process_with_parameters()
        test_noise.test_process_without_parameters()
        print("✅ NoiseReductionProcessor 基本測試通過")
        
        # 測試標準化處理器
        test_norm = TestAudioNormalizer()
        test_norm.setup_method()
        test_norm.test_initialization_success()
        test_norm.test_process_normalization()
        test_norm.test_process_no_conversion_needed()
        test_norm.test_process_without_original_params()
        print("✅ AudioNormalizer 基本測試通過")
        
        # 測試整合
        test_integration = TestPreprocessorIntegration()
        test_integration.test_noise_reduction_and_normalization_pipeline()
        print("✅ 前處理器整合測試通過")
        
        print("🎉 所有前處理器測試完成！")
        print("執行 'pytest tests/test_preprocessors/' 進行完整測試")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()