"""
    MediMind AI - Speech to Text Transcription Module
Supports Hindi, Gujarati, and English voice input for symptom recording.
"""
import os
import io

def transcribe_audio(audio_data, language_code: str = "hi-IN") -> str:
    """
    Transcribes spoken audio into text using Google Speech Recognition API.
    Falls back gracefully if network is unavailable or speech is silent.
    """
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        
        if isinstance(audio_data, str) and os.path.exists(audio_data):
            with sr.AudioFile(audio_data) as source:
                audio = r.record(source)
        elif isinstance(audio_data, bytes):
            with sr.AudioFile(io.BytesIO(audio_data)) as source:
                audio = r.record(source)
        else:
            return ""
        text = r.recognize_google(audio, language=language_code)
        return text.strip() if text else ""
    except Exception as e:
        print(f"Speech recognition notice: {e}")
        return ""
