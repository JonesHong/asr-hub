"""簡化的音訊處理測試 - 驗證採樣率問題修復"""

import sys
import os
import wave
import numpy as np

# 添加專案根目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessors.noise_reduction import NoiseReductionProcessor


def read_wav_file(file_path):
    """讀取 WAV 檔案"""
    with wave.open(file_path, 'rb') as wav_file:
        channels = wav_file.getnchannels()
        sample_rate = wav_file.getframerate()
        frames = wav_file.getnframes()
        duration = frames / sample_rate
        audio_bytes = wav_file.readframes(frames)
        
        print(f"📄 原始檔案: {os.path.basename(file_path)}")
        print(f"   採樣率: {sample_rate} Hz")
        print(f"   聲道數: {channels}")
        print(f"   時長: {duration:.2f} 秒")
        print(f"   樣本數: {frames}")
        
        return audio_bytes, sample_rate, channels, duration


def save_wav_file(audio_bytes, file_path, sample_rate, channels):
    """保存 WAV 檔案"""
    with wave.open(file_path, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_bytes)
    
    # 驗證保存的檔案
    with wave.open(file_path, 'rb') as wav_file:
        saved_sample_rate = wav_file.getframerate()
        saved_channels = wav_file.getnchannels()
        saved_frames = wav_file.getnframes()
        saved_duration = saved_frames / saved_sample_rate
        
        print(f"💾 保存檔案: {os.path.basename(file_path)}")
        print(f"   採樣率: {saved_sample_rate} Hz")
        print(f"   聲道數: {saved_channels}")
        print(f"   時長: {saved_duration:.2f} 秒")
        print(f"   樣本數: {saved_frames}")


def main():
    """主測試程式"""
    print("🧪 簡化音訊處理測試")
    print("=" * 40)
    
    input_file = "./examples/test_audio.wav"
    
    if not os.path.exists(input_file):
        print(f"❌ 找不到測試檔案: {input_file}")
        return
    
    # 讀取原始檔案
    audio_bytes, sample_rate, channels, duration = read_wav_file(input_file)
    
    # 創建降噪處理器 - 關鍵：不改變採樣率
    noise_config = {
        'enabled': True,
        'strength': 0.8,  # 降噪強度
        'sample_rate': sample_rate,  # 使用原始採樣率
        'frame_length': 2048,
        'hop_length': 512
    }
    
    print(f"\n🔧 創建降噪處理器 (採樣率: {sample_rate} Hz)")
    processor = NoiseReductionProcessor(noise_config)
    
    # 執行處理 - 傳遞正確的原始參數
    print("\n🎵 執行降噪處理...")
    try:
        processed_bytes = processor.process(
            audio_bytes,
            original_sample_rate=sample_rate,
            original_channels=channels
        )
        
        print("✅ 處理完成")
        
        # 保存結果 - 使用原始格式
        output_file = "./examples/simple_test_denoised.wav"
        save_wav_file(processed_bytes, output_file, sample_rate, channels)
        
        # 驗證處理結果
        print(f"\n📊 處理結果分析:")
        original_array = np.frombuffer(audio_bytes, dtype=np.int16)
        processed_array = np.frombuffer(processed_bytes, dtype=np.int16)
        
        print(f"   原始樣本數: {len(original_array)}")
        print(f"   處理後樣本數: {len(processed_array)}")
        print(f"   樣本數是否一致: {'✅' if len(original_array) == len(processed_array) else '❌'}")
        
        # 計算處理效果
        original_rms = np.sqrt(np.mean(original_array.astype(np.float32)**2))
        processed_rms = np.sqrt(np.mean(processed_array.astype(np.float32)**2))
        
        print(f"   原始 RMS: {original_rms:.1f}")
        print(f"   處理後 RMS: {processed_rms:.1f}")
        print(f"   降噪效果: {((original_rms - processed_rms) / original_rms * 100):.1f}%")
        
    except Exception as e:
        print(f"❌ 處理失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()