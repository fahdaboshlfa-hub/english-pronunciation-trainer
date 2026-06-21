"""
score.py
يقارن بين النص المستهدف والنص اللي تم التعرف عليه من تسجيلك،
ويحسب نسبة الدقة + يبرز الكلمات الصحيحة/الناقصة/الزايدة/المستبدلة.

ملاحظة مهمة: هذا التقييم يعتمد على دقة Whisper في "فهم" الكلام، يعني
يكشف بقوة الأخطاء اللي تغيّر الكلمة فعلياً (نطق غلط لدرجة الكلمة
تطلع مفهومة غلط)، لكنه أضعف في كشف فروقات دقيقة جداً بالصوت (زي نطق
TH بدل Z مع بقاء الكلمة مفهومة). لو تبي دقة على مستوى الصوت/الحرف
نفسه، الخطوة الجاية تكون دمج خدمة متخصصة زي Azure Pronunciation
Assessment - الكود مبني بطريقة يسهل تضيفها لاحقاً كـ scoring engine ثاني.
"""

import re
from difflib import SequenceMatcher

import jiwer


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s']", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def score_attempt(target_text: str, spoken_text: str) -> dict:
    target_norm = normalize(target_text)
    spoken_norm = normalize(spoken_text)

    wer = jiwer.wer(target_norm, spoken_norm)
    accuracy = max(0.0, (1 - wer)) * 100

    target_words = target_norm.split()
    spoken_words = spoken_norm.split()

    matcher = SequenceMatcher(None, target_words, spoken_words)
    diff_parts = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for w in target_words[i1:i2]:
                diff_parts.append({"word": w, "status": "correct"})
        elif tag == "replace":
            for w in target_words[i1:i2]:
                diff_parts.append({"word": w, "status": "wrong"})
        elif tag == "delete":
            for w in target_words[i1:i2]:
                diff_parts.append({"word": w, "status": "missing"})
        elif tag == "insert":
            for w in spoken_words[j1:j2]:
                diff_parts.append({"word": w, "status": "extra"})

    if accuracy >= 90:
        feedback = "ممتاز! نطقك قريب جداً من النطق الصحيح."
    elif accuracy >= 70:
        feedback = "جيد، فيه كلمات تحتاج تركيز أكثر."
    elif accuracy >= 40:
        feedback = "محتاج تمرين أكثر على الجملة، ركّز على الكلمات اللي تطلع غلط."
    else:
        feedback = "حاول تسمع الصوت المرجعي مرة ثانية وكرر ببطء أكثر."

    return {
        "accuracy": round(accuracy, 1),
        "wer": round(wer, 3),
        "diff": diff_parts,
        "feedback": feedback,
        "spoken_text": spoken_text,
        "target_text": target_text,
    }
