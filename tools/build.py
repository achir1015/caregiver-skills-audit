"""整理稽核表（題號、說明）與各單元簡報 OCR 文字，產生網站資料 data.js。

用法：python tools/build.py   （先跑 tools/ocr.py 產生 ocr.json 與 slides/）
"""
import json
import re
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
CHECKLIST = ROOT / "照服技術稽核.pdf"
DRIVE = "https://drive.google.com/drive/folders/103fuY5-RcAzJ-aCYnueIWs1fNSx4tjSB?usp=sharing"


def parse_checklist():
    text = "\n".join(p.get_text() for p in pymupdf.open(CHECKLIST))
    source = text.strip().splitlines()[0].strip()
    text = text[: text.find("如果需要")]  # 文末 AI 產生的附註
    lines = []
    for raw in text.splitlines():
        s = raw.strip().lstrip("●").strip()
        if not s or re.fullmatch(r"\d+\.", s) or re.fullmatch(r"[가-힯\s]+", s):
            continue  # 空行、單元 15 的流水號、亂碼符號
        lines.append(s)
    units, cur, item = [], None, None
    for s in lines[1:]:
        m = re.match(r"單元\s*(\d+)：(.+)", s)
        if m:
            cur = {"no": m.group(1).zfill(2), "title": m.group(2).strip(), "items": []}
            units.append(cur)
            item = None
            continue
        m = re.match(r"(\d{2})\.\s*(.*)", s)
        if m:
            item = {"no": m.group(1), "text": m.group(2), "sub": []}
            cur["items"].append(item)
        elif item and item["text"].endswith("步驟：") and not item["sub"]:
            item["sub"].append(s)  # 子步驟（如會陰沖洗女性／男性）
        elif item and item["sub"] and not s.endswith("："):
            if item["sub"][-1].endswith(("。", "：")):
                item["sub"].append(s)
            else:
                item["sub"][-1] += s
        elif item and item["sub"]:
            item["sub"].append(s)
        elif item:
            item["text"] += s  # PDF 換行斷開的同一題
    for u in units:
        for it in u["items"]:
            for key in ("text",):
                it[key] = clean(it[key])
            it["sub"] = [clean(x) for x in it["sub"]]
            if not it["sub"]:
                del it["sub"]
    return source, units


def clean(s):
    s = re.sub(r"\s+(\d+(-\d+)?)\s*。$", "。", s)  # 文末引用編號（如「1-3。」「22。」）
    s = re.sub(r"\s*。$", "。", s)
    s = re.sub(r"(?<=[^\x00-\x7f])\s+(?=[^\x00-\x7f])", "", s)
    return s.strip()


def main():
    source, units = parse_checklist()
    ocr = json.loads((ROOT / "ocr.json").read_text(encoding="utf-8"))
    decks = {re.match(r"\d+", p.name).group(): p for p in ROOT.glob("[0-9][0-9]*.pdf")}
    for u in units:
        u["pdf"] = decks[u["no"]].name
        u["deck"] = re.sub(r"^\d+", "", decks[u["no"]].stem).replace("_", " ")
        u["slides"] = [re.sub(r"[ \t]+", " ", t) for t in ocr[u["no"]]]
    data = {"source": source, "drive": DRIVE, "units": units}
    (ROOT / "data.js").write_text(
        "window.AUDIT_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8"
    )
    for u in units:
        print(u["no"], u["title"], len(u["items"]), "題", len(u["slides"]), "頁")


if __name__ == "__main__":
    main()
