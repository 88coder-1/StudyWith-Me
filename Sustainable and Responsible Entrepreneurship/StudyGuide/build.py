"""Build index.html (a standalone page) from template.html + ../Exam/m*-quiz.json + answers.json.

Run:  python3 build.py
View: python3 -m http.server 8000   (then open the forwarded port), or download index.html and open it.
"""
import json
from pathlib import Path

here = Path(__file__).parent
exam = here.parent / "Exam"
answers = json.loads((here / "answers.json").read_text(encoding="utf-8"))

quiz, problems = {}, []
for m in ["m1", "m2", "m3", "m4", "m5"]:
    questions = json.loads((exam / f"{m}-quiz.json").read_text(encoding="utf-8"))
    key = answers[m]
    if len(questions) != len(key):
        problems.append(f"{m}: {len(questions)} questions but {len(key)} answers")
    items = []
    for q, (correct, kw, explanation) in zip(questions, key):
        text = q["q"].replace("**", "")
        kws = [k for k in kw.split("|") if k]
        if not 0 <= correct < len(q["a"]):
            problems.append(f"{m}-{q['no']}: answer index {correct} out of range")
        for k in kws:
            if k.lower() not in text.lower():
                problems.append(f"{m}-{q['no']}: keyword not in question: {k!r}")
        items.append({"q": q["q"], "a": q["a"], "c": correct, "kw": kws, "ex": explanation})
    quiz[m] = items

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
(here / "index.html").write_text(html, encoding="utf-8")
print(f"index.html written: {len(html.encode('utf-8')) // 1024} KB, "
      f"{sum(len(v) for v in quiz.values())} questions, {len(problems)} warnings")
