"""
generate_audio.py
يولّد ملفات صوتية مرجعية (نطق صحيح) لكل جملة في data/conversations.json
باستخدام ElevenLabs API، ويخزنها محلياً في audio/reference/ حتى لا تتكرر
عملية التوليد (وبالتالي ما يكلفك رصيد إضافي من ElevenLabs).
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from rich.console import Console
from rich.progress import track

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "conversations.json"
AUDIO_DIR = ROOT / "audio" / "reference"

console = Console()


def load_sentences():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    sentences = []
    for cat in data["categories"]:
        for s in cat["sentences"]:
            sentences.append(s)
    return sentences


def main():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

    if not api_key or api_key == "your_api_key_here":
        console.print(
            "[bold red]خطأ:[/bold red] لازم تضيف ELEVENLABS_API_KEY في ملف .env أولاً."
        )
        return

    client = ElevenLabs(api_key=api_key)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    sentences = load_sentences()
    to_generate = [s for s in sentences if not (AUDIO_DIR / f"{s['id']}.mp3").exists()]

    if not to_generate:
        console.print("[green]كل الملفات الصوتية موجودة بالفعل. ما في شي نولّده.[/green]")
        return

    console.print(f"[cyan]رح يتم توليد {len(to_generate)} ملف صوتي...[/cyan]")

    for s in track(to_generate, description="توليد الصوت..."):
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            text=s["text"],
        )
        out_path = AUDIO_DIR / f"{s['id']}.mp3"
        with open(out_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

    console.print("[bold green]تم توليد كل الملفات الصوتية بنجاح.[/bold green]")


if __name__ == "__main__":
    main()
