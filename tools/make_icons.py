"""產生網站圖示：網址列 favicon、主畫面捷徑 apple-touch-icon、PWA 圖示（含 maskable）。

用法：python tools/make_icons.py
需要：pip install pillow；字型使用 Windows 微軟正黑體粗體
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "icons"
FONT = "C:/Windows/Fonts/msjhbd.ttc"
BLUE = (37, 92, 140)
CREAM = (248, 246, 240)
S = 1024  # 先畫大圖再縮小，邊緣較平滑


def draw(full_bleed: bool) -> Image.Image:
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if full_bleed:
        d.rectangle([0, 0, S, S], fill=BLUE)
        scale = 0.72  # maskable：主體留在安全區內
    else:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=BLUE)
        scale = 0.9

    def p(x, y):  # 以 0–1 座標定位，並依 scale 縮放到中心
        return (S / 2 + (x - 0.5) * S * scale, S / 2 + (y - 0.5) * S * scale)

    # 稽核板：板身 + 上方夾子
    d.rounded_rectangle([p(0.17, 0.14), p(0.83, 0.92)], radius=int(S * scale * 0.07), fill=CREAM)
    d.rounded_rectangle([p(0.35, 0.07), p(0.65, 0.21)], radius=int(S * scale * 0.04), fill=BLUE)
    d.rounded_rectangle([p(0.38, 0.10), p(0.62, 0.18)], radius=int(S * scale * 0.025), fill=CREAM)
    # 「稽」字
    font = ImageFont.truetype(FONT, int(S * scale * 0.46), index=0)
    x, y = p(0.5, 0.56)
    d.text((x, y), "稽", font=font, fill=BLUE, anchor="mm")
    return img


def main():
    OUT.mkdir(exist_ok=True)
    rounded, bleed = draw(False), draw(True)
    for size in (16, 32, 48):
        rounded.resize((size, size), Image.LANCZOS).save(OUT / f"favicon-{size}.png")
    rounded.resize((48, 48), Image.LANCZOS).save(
        ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)]
    )
    for size in (192, 512):
        rounded.resize((size, size), Image.LANCZOS).save(OUT / f"icon-{size}.png")
        bleed.resize((size, size), Image.LANCZOS).save(OUT / f"maskable-{size}.png")
    # iOS 主畫面圖示不支援透明，用滿版底色
    bleed.convert("RGB").resize((180, 180), Image.LANCZOS).save(OUT / "apple-touch-icon.png")
    print("icons written to", OUT)


if __name__ == "__main__":
    main()
