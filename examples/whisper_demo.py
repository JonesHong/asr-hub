"""Whisper 引擎使用範例"""

import sys
import os

# 添加專案根目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engines.whisper import WhisperEngine
from src.core.registry import registry


def main():
    """Whisper 引擎示範"""
    
    print("🎙️ Whisper ASR 引擎示範")
    print("-" * 40)
    
    # 配置 Whisper 引擎
    config = {
        'model_size': 'tiny',  # 使用 tiny 模型以節省下載時間
        'device': 'auto',
        'language': 'auto'  # 自動偵測語言
    }
    
    try:
        # 初始化引擎
        print("正在初始化 Whisper 引擎...")
        engine = WhisperEngine(config)
        
        print(f"✅ 引擎初始化成功")
        print(f"引擎名稱: {engine.name}")
        print(f"支援串流: {engine.supports_streaming}")
        
        # 顯示模型資訊
        info = engine.get_model_info()
        print(f"模型大小: {info.get('model_size')}")
        print(f"設備: {info.get('device')}")
        
        # 註冊到全域註冊表
        registry.register_engine('whisper', WhisperEngine)
        print("✅ 引擎已註冊到全域註冊表")
        
        # 測試從註冊表創建引擎
        engine2 = registry.create_engine('whisper', config)
        print("✅ 從註冊表成功創建引擎實例")
        
        print("\n📝 注意事項:")
        print("- 首次使用會下載模型檔案")
        print("- tiny 模型較小但精確度較低")
        print("- 建議在實際使用時選擇 base 或 small 模型")
        print("- 使用 language='auto' 可自動偵測語言")
        
        # 如果有音訊檔案，可以進行轉譯測試
        test_audio_path = "./examples/test_audio.wav"
        if os.path.exists(test_audio_path):
            print(f"\n🔍 發現測試音訊檔案: {test_audio_path}")
            with open(test_audio_path, 'rb') as f:
                audio_bytes = f.read()
            
            print("正在進行轉譯...")
            result = engine.transcribe(audio_bytes)
            print(f"轉譯結果: {result}")
            
            # 測試語言偵測
            detected_lang = engine.detect_language(audio_bytes)
            print(f"偵測語言: {detected_lang}")
        else:
            print(f"\n💡 提示: 將音訊檔案命名為 '{test_audio_path}' 放在此目錄下可測試轉譯功能")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        print("請確保已安裝 openai-whisper: pip install openai-whisper")


if __name__ == "__main__":
    main()