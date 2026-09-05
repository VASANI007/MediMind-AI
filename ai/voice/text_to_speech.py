"""
    MediMind AI - Text to Speech Audio Synthesis Module
"""
import os
import io
import base64
import re

def synthesize_speech(text: str, lang: str = "en") -> str:
    """
    Synthesizes speech into an in-memory base64 audio string for browser playback.
    """
    if not text or not text.strip():
        return ""

    # Clean markdown formatting before speech
    clean = re.sub(r"[\*\_#`~>]", "", text)
    clean = re.sub(r"\s+", " ", clean).strip()

    try:
        from gtts import gTTS
        lang_code = "hi" if lang == "hi" else "gu" if lang == "gu" else "en"
        tts = gTTS(text=clean[:300], lang=lang_code, slow=False)
        
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_b64 = base64.b64encode(fp.read()).decode("utf-8")
        return f"data:audio/mp3;base64,{audio_b64}"
    except Exception as e:
        print(f"TTS synthesis notice: {e}")
        return ""
