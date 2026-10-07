"""把各單元簡報 PDF 每頁轉成 WebP 圖片（網站簡報顯示用），並用 Windows 內建繁中 OCR 取文字（查詢用）。

用法：python tools/ocr.py
產出：slides/NN/PP.webp、ocr.json（{單元編號: [每頁文字, ...]}）
需要：pip install pymupdf winocr pillow（Windows 10/11，需安裝繁體中文 OCR 語言）
"""
import json
import re
import sys
from pathlib import Path

import pymupdf
import winocr
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ocr.json"
SLIDES = ROOT / "slides"
WIDTH = 1376  # 簡報原始寬度，網頁顯示已足夠清晰


def main():
    done = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    for pdf in sorted(ROOT.glob("[0-9][0-9]*.pdf")):
        unit = re.match(r"\d+", pdf.name).group()
        if unit in done:
            continue
        doc = pymupdf.open(pdf)
        (SLIDES / unit).mkdir(parents=True, exist_ok=True)
        texts = []
        for i, page in enumerate(doc):
            zoom = WIDTH / page.rect.width
            pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
            img = Image.frombytes("RGB", (pix.w, pix.h), pix.samples)
            img.save(SLIDES / unit / f"{i + 1:02d}.webp", "WEBP", quality=82, method=6)
            r = winocr.recognize_pil_sync(img, "zh-Hant-TW")
            # 中文字之間 OCR 會插空白，去掉；英數之間保留
            lines = [re.sub(r"(?<=[^\x00-\x7f]) (?=[^\x00-\x7f])", "", l["text"]) for l in r["lines"]]
            texts.append("\n".join(lines))
        done[unit] = texts
        OUT.write_text(json.dumps(done, ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"{pdf.name}: {len(texts)} 頁", file=sys.stderr, flush=True)
    print("done", file=sys.stderr)


if __name__ == "__main__":
    main()
