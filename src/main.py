"""
main.py
الواجهة الرئيسية: اختر فئة → اختر جملة → اسمع النطق الصحيح →
سجّل صوتك → شوف تقييمك → تابع تقدمك مع الوقت.

تشغيل: python src/main.py
"""

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from playback import play_audio
from progress import get_summary, log_attempt
from record import record_until_enter
from score import score_attempt
from transcribe import transcribe_audio

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "conversations.json"
REF_AUDIO_DIR = ROOT / "audio" / "reference"
ATTEMPTS_DIR = ROOT / "audio" / "attempts"

console = Console()


def load_data() -> dict:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def print_diff(diff_parts: list) -> None:
    colors = {
        "correct": "green",
        "wrong": "red",
        "missing": "yellow",
        "extra": "magenta",
    }
    rendered = []
    for part in diff_parts:
        color = colors.get(part["status"], "white")
        rendered.append(f"[{color}]{part['word']}[/{color}]")
    console.print(" ".join(rendered))
    console.print(
        "[green]أخضر = صحيح[/green]  [red]أحمر = غلط[/red]  "
        "[yellow]أصفر = ناقصة[/yellow]  [magenta]بنفسجي = زايدة[/magenta]"
    )


def choose_category(data: dict):
    table = Table(title="اختر فئة")
    table.add_column("#")
    table.add_column("الفئة")
    for i, cat in enumerate(data["categories"], 1):
        table.add_row(str(i), f"{cat['name_ar']} ({cat['name_en']})")
    console.print(table)
    choice = console.input("اختر رقم الفئة (أو 0 للخروج): ").strip()
    if choice == "0":
        return None
    try:
        return data["categories"][int(choice) - 1]
    except (ValueError, IndexError):
        console.print("[red]اختيار غير صحيح.[/red]")
        return choose_category(data)


def choose_sentence(category: dict):
    table = Table(title=category["name_ar"])
    table.add_column("#")
    table.add_column("الجملة")
    table.add_column("التركيز")
    for i, s in enumerate(category["sentences"], 1):
        table.add_row(str(i), s["text"], s["focus"])
    console.print(table)
    choice = console.input("اختر رقم الجملة (أو 0 للرجوع): ").strip()
    if choice == "0":
        return None
    try:
        return category["sentences"][int(choice) - 1]
    except (ValueError, IndexError):
        console.print("[red]اختيار غير صحيح.[/red]")
        return choose_sentence(category)


def practice_sentence(sentence: dict):
    ref_path = REF_AUDIO_DIR / f"{sentence['id']}.mp3"
    if not ref_path.exists():
        console.print(
            "[red]ما لقيت الصوت المرجعي. شغّل أولاً: python src/generate_audio.py[/red]"
        )
        return

    console.print(f"\n[bold cyan]الجملة:[/bold cyan] {sentence['text']}")
    console.print(f"[bold]نقطة التركيز:[/bold] {sentence['focus']}")

    while True:
        console.print("\n1) اسمع النطق الصحيح   2) سجّل وقيّم نطقك   3) ارجع للقائمة")
        action = console.input("اختيارك: ").strip()

        if action == "1":
            play_audio(ref_path)

        elif action == "2":
            ATTEMPTS_DIR.mkdir(parents=True, exist_ok=True)
            attempt_path = ATTEMPTS_DIR / f"{sentence['id']}_latest.wav"
            record_until_enter(attempt_path)

            console.print("[cyan]جاري تحليل صوتك...[/cyan]")
            spoken_text = transcribe_audio(attempt_path)
            result = score_attempt(sentence["text"], spoken_text)

            console.print(f"\n[bold]سمعت منك:[/bold] {result['spoken_text']}")
            console.print(f"[bold]نسبة الدقة:[/bold] {result['accuracy']}%")
            print_diff(result["diff"])
            console.print(f"[bold]ملاحظة:[/bold] {result['feedback']}")

            log_attempt(sentence["id"], sentence["text"], result["accuracy"])

        elif action == "3":
            break
        else:
            console.print("[red]اختيار غير صحيح.[/red]")


def show_progress():
    summary = get_summary()
    if summary["total_attempts"] == 0:
        console.print("[yellow]ما عندك محاولات مسجلة بعد.[/yellow]")
        return

    console.print(f"\n[bold]عدد المحاولات الكلي:[/bold] {summary['total_attempts']}")
    console.print(f"[bold]متوسط الدقة العام:[/bold] {summary['overall_avg']}%")

    if summary["trend"] is not None:
        trend = summary["trend"]
        arrow = "📈" if trend > 0 else ("📉" if trend < 0 else "➡️")
        console.print(f"[bold]اتجاه التحسن (آخر 5 مقابل أول 5):[/bold] {trend:+}% {arrow}")

    table = Table(title="أضعف الجمل (تحتاج تمرين أكثر)")
    table.add_column("الجملة")
    table.add_column("متوسط الدقة")
    for sid, avg in summary["weakest_sentences"]:
        table.add_row(sid, f"{round(avg, 1)}%")
    console.print(table)


def main():
    data = load_data()
    console.print("[bold green]🎙️  برنامج تدريب النطق الإنجليزي[/bold green]\n")

    while True:
        console.print("\n[bold]القائمة الرئيسية[/bold]")
        console.print("1) تمرين على جملة")
        console.print("2) عرض تقدمي")
        console.print("3) خروج")
        choice = console.input("اختيارك: ").strip()

        if choice == "1":
            category = choose_category(data)
            if category:
                sentence = choose_sentence(category)
                if sentence:
                    practice_sentence(sentence)
        elif choice == "2":
            show_progress()
        elif choice == "3":
            console.print("[cyan]بالتوفيق في التدريب! 💪[/cyan]")
            break
        else:
            console.print("[red]اختيار غير صحيح.[/red]")


if __name__ == "__main__":
    main()
