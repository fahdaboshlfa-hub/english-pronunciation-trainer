"""
transcribe.py
يحوّل تسجيل صوت المستخدم إلى نص باستخدام faster-whisper (يعمل محلياً
بعد أول تحميل للنموذج - ما يحتاج إنترنت أو API key).
"""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from faster_whisper import WhisperModel

load_dotenv()

MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")


@lru_cache(maxsize=1)
def get_model() -> WhisperModel:
    # compute_type="int8" أخف على المعالج، مناسب لأجهزة بدون GPU قوي
    return WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")


def transcribe_audio(audio_path: Path) -> str:
    model = get_model()
    segments, _ = model.transcribe(str(audio_path), language="en", beam_size=5)
    text = " ".join(segment.text.strip() for segment in segments)
    return text.strip()
