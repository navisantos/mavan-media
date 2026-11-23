"""Capa do vídeo C de 23/11/2026 (custo da falha): python3 -I cover_falha.py -> out20/capa_falha.png"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys
sys.path.insert(0, HERE)
import gen4 as g
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
OL, GOLD, CHAR, WHITE, RED = g.OL, g.GOLD, g.CHAR, g.WHITE, g.RED
img = Image.new('RGB', (W, H), g.CREAM)
d = ImageDraw.Draw(img)
for k in range(0, H + 54, 54):
    d.line((0, k, W, k), fill=g.LINEC, width=2)
g.logo_bug(img, 540, 270, 300)

def title(lines, y0, size=124, hl=-1):
    f = ImageFont.truetype(g.FB, size)
    for i, t in enumerate(lines):
        y = y0 + int(i * size * 1.22)
        wl = f.getlength(t)
        x = 540 - wl / 2
        if i == hl:
            d.rounded_rectangle((x - 18, y - size * 0.62, x + wl + 18, y + size * 0.62), radius=20, fill=GOLD)
        d.text((x, y), t, font=f, fill=CHAR, anchor='lm')

title(['SEU FILAMENTO', 'É BARATO?', 'ATÉ FALHAR'], 560, 112, hl=2)
# cinco peças, uma falha
for k in range(5):
    x, y, w = 150 + k * 195, 1130, 160
    bad = k == 4
    d.rounded_rectangle((x - w / 2, y - w * 0.45, x + w / 2, y + w * 0.45), radius=22, fill=RED if bad else GOLD, outline=OL, width=6)
    if bad:
        q = 34
        d.line((x - q, y - q, x + q, y + q), fill=WHITE, width=14)
        d.line((x - q, y + q, x + q, y - q), fill=WHITE, width=14)
    else:
        d.line([(x - 26, y), (x - 6, y + 22), (x + 30, y - 24)], fill=OL, width=12, joint='curve')
f = ImageFont.truetype(g.FB, 230)
d.text((540, 1380), '20%', font=f, fill=RED, anchor='mm')
def chip(cx, cy, txt, ang=0, gold=False):
    g.paste_center(img, g.pill(txt, 34, OL, GOLD if gold else WHITE).rotate(ang, expand=True, resample=Image.BICUBIC), cx, cy)
chip(320, 1600, 'R$ 100 / KG', -3, gold=True)
chip(760, 1620, 'TAXA DE FALHA', 3)
out = g.D + '/out20/capa_falha.png'
img.save(out)
print(out)
