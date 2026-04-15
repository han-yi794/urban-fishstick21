import pyttsx3
import threading
import platform

# 只在Windows系统上需要处理COM初始化
if platform.system() == "Windows":
    import pythoncom

class Speak:
    def __init__(self, text, rate=200, volume=1.0):
        self.text = text
        self.rate = rate
        self.volume = volume
    
    def _speak_chinese_sync(self):
        """同步播放中文语音的内部方法"""
        # Windows系统需要初始化COM
        if platform.system() == "Windows":
            pythoncom.CoInitialize()
        
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            
            # 查找中文语音
            voices = engine.getProperty("voices")
            for voice in voices:
                if "chinese" in voice.name.lower() or "zh" in voice.id.lower():
                    engine.setProperty("voice", voice.id)
                    break
            
            engine.say(self.text)
            engine.runAndWait()
        finally:
            # 清理资源
            if 'engine' in locals():
                engine.stop()
                del engine
            # Windows系统需要反初始化COM
            if platform.system() == "Windows":
                pythoncom.CoUninitialize()
    
    def _speak_english_sync(self):
        """同步播放英文语音的内部方法"""
        # Windows系统需要初始化COM
        if platform.system() == "Windows":
            pythoncom.CoInitialize()
        
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            voices = engine.getProperty("voices")
            if len(voices) > 1:
                engine.setProperty("voice", voices[1].id)
            engine.say(self.text)
            engine.runAndWait()
        finally:
            # 清理资源
            if 'engine' in locals():
                engine.stop()
                del engine
            # Windows系统需要反初始化COM
            if platform.system() == "Windows":
                pythoncom.CoUninitialize()
    
    def chinese(self, async_mode=True):
        """播放中文语音，可选择同步或异步模式"""
        if async_mode:
            # 异步播放，不阻塞主线程
            thread = threading.Thread(target=self._speak_chinese_sync)
            thread.daemon = True  # 设置为守护线程
            thread.start()
        else:
            # 同步播放（会阻塞）
            self._speak_chinese_sync()
    
    def english(self, async_mode=True):
        """播放英文语音，可选择同步或异步模式"""
        if async_mode:
            # 异步播放，不阻塞主线程
            thread = threading.Thread(target=self._speak_english_sync)
            thread.daemon = True
            thread.start()
        else:
            # 同步播放（会阻塞）
            self._speak_english_sync()

def speak_chinese(text, rate=200, volume=1.0):
    """播放中文语音的函数"""
    Speak(text, rate, volume).chinese()

def speak_english(text, rate=200, volume=1.0):
    """播放英文语音的函数"""
    Speak(text, rate, volume).english()