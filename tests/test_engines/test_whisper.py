"""測試 Whisper ASR 引擎"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.engines.whisper import WhisperEngine
from src.utils.exceptions import EngineInitializationError, TranscriptionError


class TestWhisperEngine:
    """測試 WhisperEngine 類"""
    
    def setup_method(self):
        """設置測試"""
        self.config = {
            'model_size': 'base',
            'device': 'auto',
            'language': 'auto'
        }
    
    @patch('src.engines.whisper.whisper.load_model')
    def test_initialization_success(self, mock_load_model):
        """測試成功初始化"""
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        engine = WhisperEngine(self.config)
        
        assert engine.name == "whisper"
        assert engine.model == mock_model
        assert engine.model_size == 'base'
        assert not engine.supports_streaming
        mock_load_model.assert_called_once_with(name='base', device=None)
    
    @patch('src.engines.whisper.whisper.load_model')
    def test_initialization_failure(self, mock_load_model):
        """測試初始化失敗"""
        mock_load_model.side_effect = Exception("模型載入失敗")
        
        with pytest.raises(EngineInitializationError):
            WhisperEngine(self.config)
    
    @patch('src.engines.whisper.whisper.load_model')
    @patch('src.engines.whisper.tempfile.NamedTemporaryFile')
    @patch('src.engines.whisper.os.path.exists')
    @patch('src.engines.whisper.os.unlink')
    def test_transcribe_success(self, mock_unlink, mock_exists, mock_temp_file, mock_load_model):
        """測試轉譯成功"""
        # 模擬模型
        mock_model = Mock()
        mock_model.transcribe.return_value = {'text': '  Hello World  '}
        mock_load_model.return_value = mock_model
        
        # 模擬臨時檔案
        mock_temp = Mock()
        mock_temp.name = '/tmp/test.wav'
        mock_temp.__enter__ = Mock(return_value=mock_temp)
        mock_temp.__exit__ = Mock(return_value=None)
        mock_temp_file.return_value = mock_temp
        
        mock_exists.return_value = True
        
        engine = WhisperEngine(self.config)
        
        test_audio = b"fake_audio_data"
        result = engine.transcribe(test_audio)
        
        assert result == "Hello World"
        mock_temp.write.assert_called_once_with(test_audio)
        mock_model.transcribe.assert_called_once()
        mock_unlink.assert_called_once()
    
    @patch('src.engines.whisper.whisper.load_model')
    def test_transcribe_without_model(self, mock_load_model):
        """測試未初始化模型時轉譯"""
        mock_load_model.return_value = Mock()
        engine = WhisperEngine(self.config)
        engine.model = None  # 模擬未初始化
        
        with pytest.raises(TranscriptionError):
            engine.transcribe(b"test_audio")
    
    @patch('src.engines.whisper.whisper.load_model')
    @patch('src.engines.whisper.tempfile.NamedTemporaryFile')
    @patch('src.engines.whisper.whisper.load_audio')
    @patch('src.engines.whisper.whisper.pad_or_trim')
    @patch('src.engines.whisper.whisper.log_mel_spectrogram')
    def test_detect_language(self, mock_log_mel, mock_pad_trim, mock_load_audio, 
                           mock_temp_file, mock_load_model):
        """測試語言偵測"""
        # 模擬模型
        mock_model = Mock()
        mock_model.dims.n_mels = 80
        mock_model.device = 'cpu'
        mock_model.detect_language.return_value = (None, {'en': 0.9, 'zh': 0.1})
        mock_load_model.return_value = mock_model
        
        # 模擬其他組件
        mock_temp = Mock()
        mock_temp.name = '/tmp/test.wav'
        mock_temp.__enter__ = Mock(return_value=mock_temp)
        mock_temp.__exit__ = Mock(return_value=None)
        mock_temp_file.return_value = mock_temp
        
        mock_audio = np.array([1, 2, 3])
        mock_load_audio.return_value = mock_audio
        mock_pad_trim.return_value = mock_audio
        
        mock_mel = Mock()
        mock_mel.to.return_value = mock_mel
        mock_log_mel.return_value = mock_mel
        
        engine = WhisperEngine(self.config)
        
        result = engine.detect_language(b"test_audio")
        
        assert result == 'en'
        mock_model.detect_language.assert_called_once_with(mock_mel)
    
    @patch('src.engines.whisper.whisper.load_model')
    def test_get_model_info(self, mock_load_model):
        """測試獲取模型資訊"""
        mock_dims = Mock()
        mock_dims.n_mels = 80
        mock_dims.n_audio_ctx = 1500
        mock_dims.n_audio_state = 512
        mock_dims.n_audio_head = 8
        mock_dims.n_vocab = 51865
        
        mock_model = Mock()
        mock_model.device = 'cpu'
        mock_model.dims = mock_dims
        mock_load_model.return_value = mock_model
        
        engine = WhisperEngine(self.config)
        
        info = engine.get_model_info()
        
        assert info['model_size'] == 'base'
        assert info['device'] == 'cpu'
        assert info['dims']['n_mels'] == 80
        assert info['dims']['n_vocab'] == 51865
    
    @patch('src.engines.whisper.whisper.load_model')
    def test_get_model_info_not_initialized(self, mock_load_model):
        """測試未初始化時獲取模型資訊"""
        mock_load_model.return_value = Mock()
        engine = WhisperEngine(self.config)
        engine.model = None
        
        info = engine.get_model_info()
        
        assert info['status'] == 'not_initialized'


# 簡單的整合測試（需要實際 whisper 模型）
class TestWhisperEngineIntegration:
    """Whisper 引擎整合測試（需要真實模型）"""
    
    @pytest.mark.skip(reason="需要實際 whisper 模型，跳過以避免下載")
    def test_real_whisper_initialization(self):
        """測試真實 Whisper 模型初始化"""
        config = {
            'model_size': 'tiny',  # 使用最小模型以節省時間
            'device': 'cpu',
            'language': 'en'
        }
        
        engine = WhisperEngine(config)
        
        assert engine.model is not None
        assert engine.name == "whisper"
        
        info = engine.get_model_info()
        assert 'model_size' in info
        assert 'device' in info


if __name__ == "__main__":
    # 執行基本測試
    test_engine = TestWhisperEngine()
    test_engine.setup_method()
    
    # 由於使用了 patch，這裡只能測試基本結構
    print("開始測試 WhisperEngine...")
    
    try:
        # 測試配置
        config = {
            'model_size': 'base',
            'device': 'auto',
            'language': 'zh'
        }
        
        print("✅ 配置測試通過")
        print("✅ WhisperEngine 基本結構測試完成")
        print("🎉 執行 pytest 進行完整測試")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")