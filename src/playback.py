"""
playback.py
يفتح الملف الصوتي المرجعي بمشغل النظام الافتراضي (يعمل على
ويندوز / ماك / لينكس بدون مكتبات تشغيل صوت إضافية معقدة).
"""

import platform
import subprocess
from pathlib import Path


def play_audio(path: Path) -> None:
    system = platform.system()
    try:
        if system == "Windows":
            import os

            os.startfile(str(path))  # noqa: S606
        elif system == "Darwin":
            subprocess.run(["afplay", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except Exception as e:
        print(f"⚠️ ما قدرت أشغل الصوت تلقائياً ({e}). افتح الملف يدوياً من: {path}")
