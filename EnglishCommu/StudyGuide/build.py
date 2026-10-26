"""Build ../Conclu.html (a standalone page) from template.html + questions.json.

Run:  python3 build.py
View: python3 -m http.server 8000   (then open the forwarded port), or download Conclu.html and open it.
"""
import json
from pathlib import Path

here = Path(__file__).parent
quiz = json.loads((here / "questions.json").read_text(encoding="utf-8"))

# Vocabulary Review answers: word -> explanation shown after answering
VOCAB = {
    "abandoned": "(adj.) ถูกทิ้งร้าง ไม่มีคนอยู่",
    "alleviate": "(v.) บรรเทา ทำให้เบาลง",
    "appreciate": "(v.) เห็นคุณค่า ซาบซึ้ง",
    "appropriate": "(adj.) เหมาะสม",
    "bully": "(v.) กลั่นแกล้ง รังแก",
    "catch up": "(v.) ตามให้ทัน ทำสิ่งที่พลาดไป",
    "compromise": "(n.) การประนีประนอม ต่างฝ่ายต่างยอม",
    "constructive": "(adj.) สร้างสรรค์ ช่วยให้ดีขึ้น (constructive feedback)",
    "crush on": "(phrasal v.) แอบชอบ (have a crush on somebody)",
    "diagnosis": "(n.) การวินิจฉัยโรค (make a diagnosis)",
    "diligence": "(n.) ความขยัน ช่องว่างอยู่หลัง with จึงต้องเป็นคำนาม",
    "diligently": "(adv.) อย่างขยัน ขยายกริยา studied จึงต้องเป็น adverb",
    "disappear": "(v.) หายไป",
    "disseminate": "(v.) เผยแพร่ข้อมูล",
    "distraction": "(n.) สิ่งที่ทำให้เสียสมาธิ",
    "donation": "(n.) การบริจาค (make a donation)",
    "emergence": "(n.) การเกิดขึ้น การปรากฏ",
    "etiquette": "(n.) มารยาททางสังคม",
    "extracurricular": "(adj.) นอกหลักสูตร (extracurricular activities)",
    "fetch": "(v.) ไปหยิบมา",
    "illness": "(n.) ความเจ็บป่วย",
    "infrastructure": "(n.) โครงสร้างพื้นฐาน เช่น ถนน ไฟฟ้า ระบบสาธารณสุข",
    "instruct": "(v.) สั่ง สอน (instruct somebody to do)",
    "intruder": "(n.) ผู้บุกรุก",
    "look after": "(v.) ดูแล",
    "migraine": "(n.) ไมเกรน ปวดหัวรุนแรง",
    "minimise": "(v.) ลดให้น้อยที่สุด",
    "misperception": "(n.) การเข้าใจผิด",
    "mitigate": "(v.) บรรเทา ลดผลเสีย",
    "nauseous": "(adj.) คลื่นไส้ คำใบ้คือ vomit (อาเจียน)",
    "organized": "(adj.) เป็นระเบียบ วางแผนเป็น",
    "outbreak": "(n.) การระบาดของโรค",
    "outline": "(v.) สรุปประเด็นหลัก · (n.) โครงร่าง",
    "precautionary": "(adj.) เชิงป้องกัน ช่องว่างอยู่หน้าคำนาม measures จึงต้องเป็น adjective",
    "prescribed": "(v.) สั่งยา (prescribe → prescribed)",
    "prioritize": "(v.) จัดลำดับความสำคัญ",
    "proactive": "(adj.) เชิงรุก ลงมือก่อนเกิดปัญหา",
    "proofread": "(v.) ตรวจทานแก้คำผิด",
    "pursue": "(v.) มุ่งไปสู่ (pursue a degree, pursue a career)",
    "rash": "(n.) ผื่น",
    "reciprocal": "(adj.) ซึ่งกันและกัน ตอบแทนกัน",
    "scratchy": "(adj.) ระคายเคือง (a scratchy throat)",
    "shelter": "(n.) ที่หลบภัย (take shelter)",
    "submit": "(v.) ส่งงาน (submit an assignment)",
    "suggests": "(v.) แนะนำ เสนอ (suggest → suggests)",
    "swell": "(v.) บวม",
    "symptom": "(n.) อาการ",
    "thirsty": "(adj.) กระหายน้ำ",
    "visual aids": "(n.) สื่อภาพประกอบ เช่น รูป แผนที่ วิดีโอ",
    "witness": "(n.) พยาน ผู้เห็นเหตุการณ์",
}

problems = []
ids = set()
for q in quiz:
    where = q.get("id", "?")
    if q["id"] in ids:
        problems.append(f"{where}: duplicate id")
    ids.add(q["id"])
    if not 0 <= q["c"] < len(q["a"]):
        problems.append(f"{where}: answer index {q['c']} out of range")
    if len(set(q["a"])) != len(q["a"]):
        problems.append(f"{where}: duplicate choices")
    if q["topic"] == "vocab" and not q["ex"]:
        word = q["a"][q["c"]]
        if word in VOCAB:
            q["ex"] = f"<b>{word}</b> {VOCAB[word]}"
        else:
            problems.append(f"{where}: no explanation for vocab answer {word!r}")
    if not q["ex"]:
        problems.append(f"{where}: empty explanation")

for p in problems:
    print("WARN", p)

data = json.dumps(quiz, ensure_ascii=False).replace("</", "<\\/")
template = (here / "template.html").read_text(encoding="utf-8").replace("__QUIZ__", data)
# template.html is head content (title, fonts, style) followed by body content
head, body = template.split("</style>", 1)
html = (
    '<!doctype html>\n<html lang="th">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    f"{head}</style>\n</head>\n<body>{body}</body>\n</html>\n"
)
out = here.parent / "Conclu.html"
out.write_text(html, encoding="utf-8")
print(f"{out.name} written: {len(html.encode('utf-8')) // 1024} KB, {len(quiz)} questions, {len(problems)} warnings")
