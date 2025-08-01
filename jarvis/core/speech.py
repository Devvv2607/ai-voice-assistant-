"""
Speech recognition and text-to-speech functionality for Jarvis.
Handles voice input and output operations.
"""

import speech_recognition as sr
import sounddevice as sd
import pyttsx3
import numpy as np
from typing import Optional
from ..core.config import config


class SpeechManager:
    """Manages speech recognition and text-to-speech operations."""
    
    def __init__(self):
        """Initialize speech recognition and TTS engines."""
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        self.samplerate = 16000  # 16kHz is a common value for speech
        self.channels = 1
    
    def setup_tts(self):
        """Configure text-to-speech settings."""
        speech_config = config.get_speech_config()
        
        # Set voice preference
        voices = self.tts_engine.getProperty('voices')
        if voices:
            voice_preference = speech_config['voice_preference'].lower()
            
            for voice in voices:
                if voice_preference in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            else:
                self.tts_engine.setProperty('voice', voices[0].id)
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', speech_config['rate'])
        self.tts_engine.setProperty('volume', speech_config['volume'])
    
    def _record_audio(self, duration=5) -> Optional[sr.AudioData]:
        """Record audio from the microphone."""
        print(f"🎙️  Recording for {duration} seconds...")
        try:
            audio = sd.rec(int(duration * self.samplerate), samplerate=self.samplerate, channels=self.channels, dtype='int16')
            sd.wait()
            audio = np.squeeze(audio)
            # Convert numpy array to bytes
            audio_bytes = audio.tobytes()
            return sr.AudioData(audio_bytes, self.samplerate, 2)  # 2 bytes per sample (16-bit)
        except Exception as e:
            print(f"❌ Error recording audio: {e}")
            return None
    
    def speak(self, text: str):
        """Convert text to speech and display text."""
        print(f"\n🤖 {config.assistant_name}: {text}")
        print("-" * 60)
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen_for_wake_word(self) -> bool:
        """Listen specifically for the wake word."""
        audio = self._record_audio(duration=3)
        if not audio:
            return False
        try:
            print(f"👂 Listening for '{config.wake_words[0]}'...")
            text = self.recognizer.recognize_google(audio).lower()
            print(f"🎯 Heard: {text}")
            
            for wake_word in config.wake_words:
                if wake_word in text:
                    return True
            return False
        
        except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
            return False
    
    def listen(self) -> Optional[str]:
        """Listen for voice input and convert to text."""
        audio = self._record_audio(duration=8)
        if not audio:
            return None
        try:
            print("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio).lower()
            print(f"📝 You said: {text}")
            return text
        
        except sr.WaitTimeoutError:
            return "timeout"
        except sr.UnknownValueError:
            self.speak("I couldn't understand that. Could you please repeat?")
            return None
        except sr.RequestError as e:
            self.speak("There's an issue with speech recognition.")
            print(f"Speech recognition error: {e}")
            return None
    
    def get_voice_list(self) -> list:
        """Get list of available voices."""
        voices = self.tts_engine.getProperty('voices')
        return [voice.name for voice in voices] if voices else []