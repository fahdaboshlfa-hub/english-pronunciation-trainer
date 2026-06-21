"""
progress.py
يسجّل نتيجة كل محاولة (تاريخ، الجملة، نسبة الدقة) في results/progress.json
عشان تقدر تشوف تحسّنك مع الوقت بدل ما كل محاولة تروح وتنسى.
"""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROGRESS_FILE = ROOT / "results" / "progress.json"


def _load() -> list:
    if not PROGRESS_FILE.exists():
        return []
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: list) -> None:
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def log_attempt(sentence_id: str, target_text: str, accuracy: float) -> None:
    data = _load()
    data.append(
        {
            "sentence_id": sentence_id,
            "target_text": target_text,
            "accuracy": accuracy,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
    )
    _save(data)


def get_summary() -> dict:
    data = _load()
    if not data:
        return {"total_attempts": 0}

    per_sentence: dict = {}
    for entry in data:
        sid = entry["sentence_id"]
        per_sentence.setdefault(sid, []).append(entry["accuracy"])

    weakest = sorted(
        ((sid, sum(v) / len(v)) for sid, v in per_sentence.items()),
        key=lambda x: x[1],
    )[:5]

    overall_avg = sum(e["accuracy"] for e in data) / len(data)

    # اتجاه التحسن: متوسط أول 5 محاولات مقابل آخر 5 محاولات
    trend = None
    if len(data) >= 6:
        first_avg = sum(e["accuracy"] for e in data[:5]) / 5
        last_avg = sum(e["accuracy"] for e in data[-5:]) / 5
        trend = round(last_avg - first_avg, 1)

    return {
        "total_attempts": len(data),
        "overall_avg": round(overall_avg, 1),
        "weakest_sentences": weakest,
        "trend": trend,
    }
