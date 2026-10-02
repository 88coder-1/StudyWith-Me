"""Build index.html (a standalone study page) for the Intro2SE midterm.

Inputs:  template.html, extra-questions.json, and the instructor's review guide in ../slide/
         (its 23 sample questions and answers are read straight from that file).
Run:     python3 build.py
View:    python3 -m http.server 8001   (then open the forwarded port), or download index.html and open it.
"""
import json
import re
from pathlib import Path

here = Path(__file__).parent
guide = here.parent / "slide" / "Intro2SE-Midterm-Review-Guide-2569 (2).html"
problems = []

PAIR = r'<span class="l-th">(.*?)</span><span class="l-en">(.*?)</span>'


def clean(fragment: str) -> str:
    """Keep only simple inline emphasis tags from the guide's HTML."""
    fragment = re.sub(r"<(?!/?(?:b|em|strong|code)\b)[^>]*>", "", fragment)
    return re.sub(r"\s+", " ", fragment).strip()


def plain(fragment: str) -> str:
    """Strip every tag."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]*>", "", fragment)).strip()


def teacher_questions() -> list:
    html = guide.read_text(encoding="utf-8")
    blocks = html.split('<details class="practice">')[1:]
    if len(blocks) != 6:
        problems.append(f"expected 6 practice blocks in the guide, found {len(blocks)}")
    out = []
    for ch, block in enumerate(blocks, start=1):
        for n, mcq in enumerate(block.split('<div class="mcq">')[1:], start=1):
            stem = re.search(r'<p class="qstem">.*?' + PAIR + r"</p>", mcq, re.S)
            opts = re.search(r'<ol class="opts">(.*?)</ol>', mcq, re.S)
            key = re.search(r'<span class="cor">([A-D])</span>' + PAIR, mcq, re.S)
            choices = re.findall(r"<li>" + PAIR + r"</li>", opts.group(1), re.S) if opts else []
            if not (stem and key and len(choices) == 4):
                problems.append(f"could not parse guide question ch{ch} #{n}")
                continue
            out.append({
                "id": f"t{ch}-{n}", "ch": ch, "src": "teacher",
                "q": [clean(stem.group(1)), clean(stem.group(2))],
                # the guide bolds key words in some options, which would give the answer away
                "a": [[plain(th), plain(en)] for th, en in choices],
                "c": "ABCD".index(key.group(1)),
                "ex": [clean(key.group(2)), clean(key.group(3))],
            })
    return out


def extra_questions(figure_ids: set) -> list:
    items = json.loads((here / "extra-questions.json").read_text(encoding="utf-8"))
    out = []
    for i, q in enumerate(items, start=1):
        if len(q["a"]) != 4 or not 0 <= q["c"] < 4:
            problems.append(f"extra #{i}: needs 4 choices and a valid answer index")
        if q.get("fig") and q["fig"] not in figure_ids:
            problems.append(f"extra #{i}: unknown figure {q['fig']!r}")
        out.append({"id": f"x{i}", "src": "extra", **q})
    return out


def expand_bilingual(text: str) -> str:
    """template.html writes bilingual text as U+27E6 Thai U+00A6 English U+27E7 (U+27EA/U+27EB inside SVG).

    Each marker becomes a pair of elements; CSS shows the one matching html[data-lang].
    """
    text = re.sub(r"⟦(.*?)¦(.*?)⟧", r'<span class="l-th">\1</span><span class="l-en">\2</span>', text, flags=re.S)
    text = re.sub(r"⟪(.*?)¦(.*?)⟫", r'<tspan class="l-th">\1</tspan><tspan class="l-en">\2</tspan>', text, flags=re.S)
    leftover = re.findall(r"[⟦⟧⟪⟫¦]", text)
    if leftover:
        problems.append(f"{len(leftover)} unbalanced bilingual markers left in the template")
    return text


template = expand_bilingual((here / "template.html").read_text(encoding="utf-8"))
figure_ids = set(re.findall(r'data-fig="([^"]+)"', template))
teacher = teacher_questions()
extra = extra_questions(figure_ids)
quiz = sorted(teacher + extra, key=lambda q: (q["ch"], q["src"] != "teacher"))

for p in problems:
    print("WARN", p)

data = json.dumps(quiz, ensure_ascii=False).replace("</", "<\\/")
page = template.replace("__QUIZ__", data)
# Inline the stick-figure actor: page styles did not reach it through <use> in Chrome.
actor = re.search(r'<g id="actor">(.*?)</g>', page, re.S).group(1)
page = re.sub(r'<use href="#actor" x="(\d+)" y="(\d+)"/>',
              lambda m: f'<g transform="translate({m.group(1)} {m.group(2)})">{actor}</g>', page)
# template.html is head content (title, fonts, style) followed by body content
head, body = page.split("</style>", 1)
html = (
    '<!doctype html>\n<html lang="th" data-lang="th">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    f"{head}</style>\n</head>\n<body>{body}</body>\n</html>\n"
)
(here / "index.html").write_text(html, encoding="utf-8")
per_ch = {ch: sum(1 for q in quiz if q["ch"] == ch) for ch in range(1, 7)}
print(f"index.html written: {len(html.encode('utf-8')) // 1024} KB · teacher {len(teacher)} + extra {len(extra)} "
      f"= {len(quiz)} questions · per chapter {per_ch} · {len(problems)} warnings")
