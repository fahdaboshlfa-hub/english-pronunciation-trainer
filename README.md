# 🎙️ مدرّب النطق الإنجليزي | English Pronunciation Trainer

برنامج تدريب على النطق الإنجليزي يعمل بالكامل من سطر الأوامر (CLI). يولّد
أصوات مرجعية احترافية بالذكاء الاصطناعي (ElevenLabs)، يسجّل صوتك من المايك،
يحوّله نص محلياً عبر Whisper، يقارنه بالنص الأصلي، ويتابع تقدمك مع الوقت.

## وش يسوي بالضبط

1. تختار جملة من بنك جمل مصنف (تحيات، حياة يومية، رياضة، عمل).
2. تسمع نطقها الصحيح (مولّد بصوت AI احترافي).
3. تسجل نفسك وأنت تقرأها.
4. البرنامج يحوّل صوتك لنص (محلياً، بدون إنترنت بعد أول تحميل للنموذج)
   ويقارنه بالجملة الأصلية، ويعطيك نسبة دقة + يلوّن الكلمات (صح/غلط/ناقصة/زايدة).
5. كل محاولة تنحفظ، وتقدر تشوف تقدمك واتجاه تحسّنك من قائمة "عرض تقدمي".

## ⚠️ حدود مهمة (مهم تعرفها)

التقييم مبني على **دقة التعرف على الكلام (Whisper)**، يعني يكشف بقوة لما النطق
يخلي الكلمة تطلع مفهومة غلط. لكنه أضعف في كشف فروقات دقيقة جداً على مستوى
الصوت نفسه (مثلاً نطق TH قريب من Z لكن الكلمة لسا مفهومة). هذا أفضل حل مجاني
ومحلي متوفر بدون اشتراكات. لو احتجت لاحقاً دقة على مستوى الفونيم/الحرف، فيه
خدمات متخصصة (مثل Azure Pronunciation Assessment) يمكن دمجها لاحقاً كمحرك
تقييم بديل - الكود مبني بطريقة `score.py` منفصلة عشان يسهل استبدالها.

## المتطلبات

- Python 3.10+
- مايك متصل بالجهاز
- مفتاح API من [ElevenLabs](https://elevenlabs.io/app/settings/api-keys) (فيه باقة مجانية)

## التثبيت

```bash
git clone <رابط_المستودع_بعد_رفعه>
cd english-pronunciation-trainer

python -m venv venv
source venv/bin/activate      # ويندوز: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# افتح .env وحط مفتاح ElevenLabs الخاص فيك
```

## التشغيل

```bash
# أول مرة فقط - يولّد كل الأصوات المرجعية (يستهلك رصيد ElevenLabs مرة وحدة)
python src/generate_audio.py

# تشغيل البرنامج
python src/main.py
```

## هيكل المشروع

```
english-pronunciation-trainer/
├── data/
│   └── conversations.json    # بنك الجمل، مصنف حسب الفئة ونوع التحدي النطقي
├── audio/
│   ├── reference/             # الأصوات المرجعية المولّدة (تتولد مرة وحدة)
│   └── attempts/              # تسجيلاتك (تتحدث كل مرة، ما تتراكم)
├── results/
│   └── progress.json          # سجل كل محاولاتك مع الوقت
├── src/
│   ├── generate_audio.py      # توليد الصوت المرجعي عبر ElevenLabs
│   ├── record.py               # تسجيل صوتك من المايك
│   ├── transcribe.py           # تحويل صوتك لنص عبر Whisper المحلي
│   ├── score.py                 # مقارنة النص وحساب نسبة الدقة
│   ├── progress.py              # تتبع تقدمك مع الوقت
│   ├── playback.py              # تشغيل الصوت المرجعي
│   └── main.py                   # الواجهة الرئيسية (CLI)
├── requirements.txt
├── .env.example
└── .gitignore
```

## إضافة جمل جديدة

افتح `data/conversations.json` وضيف جملة جديدة داخل أي فئة (أو فئة جديدة بالكامل)
بنفس الشكل:

```json
{ "id": "g6", "text": "Your new sentence here.", "focus": "اكتب نوع التحدي" }
```

بعدها شغّل `python src/generate_audio.py` مرة ثانية - بيولّد الصوت
للجمل الجديدة فقط (الجمل القديمة ما تتعاد).

## رفعه على GitHub

```bash
cd english-pronunciation-trainer
git init
git add .
git commit -m "Initial commit: English pronunciation trainer"
git branch -M main
git remote add origin https://github.com/<اسم_حسابك>/english-pronunciation-trainer.git
git push -u origin main
```

(ملف `.gitignore` مجهز عشان ما يرفع مفتاح API ولا تسجيلاتك الصوتية ولا
سجل تقدمك - تبقى محلية عندك فقط).
