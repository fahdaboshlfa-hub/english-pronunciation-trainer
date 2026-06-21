"""
record.py
يسجّل صوت المستخدم من المايكروفون. يبدأ التسجيل فور تشغيل الدالة،
ويتوقف عند الضغط على Enter (تسجيل بطول مرن بدل مدة ثابتة).
"""

import threading
from pathlib import Path

import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000  # مناسب لـ Whisper مباشرة بدون إعادة تحويل


def record_until_enter(output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    frames = []
    stop_flag = threading.Event()

    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="float32", callback=callback
    )

    print("\n🎙️  اضغط Enter للبدء بالتسجيل...")
    input()
    stream.start()
    print("🔴 يسجل الآن... اضغط Enter مرة ثانية عشان توقف.")
    input()
    stream.stop()
    stream.close()

    if not frames:
        raise RuntimeError("ما تم تسجيل أي صوت. تأكد إن المايك متصل ومفعّل.")

    import numpy as np

    audio_data = np.concatenate(frames, axis=0)
    sf.write(str(output_path), audio_data, SAMPLE_RATE)
    print(f"✅ تم حفظ التسجيل: {output_path}")
    return output_path
