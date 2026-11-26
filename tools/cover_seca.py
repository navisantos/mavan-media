"""Capa do vídeo C de 26/11/2026 (secar filamento sem estufa): python3 -I cover_seca.py -> out22/capa_seca.png"""
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

def title(lines, y0, size=118, hl=-1):
    f = ImageFont.truetype(g.FB, size)
    for i, t in enumerate(lines):
        y = y0 + int(i * size * 1.22)
        wl = f.getlength(t)
        x = 540 - wl / 2
        if i == hl:
            d.rounded_rectangle((x - 18, y - size * 0.62, x + wl + 18, y + size * 0.62), radius=20, fill=GOLD)
        d.text((x, y), t, font=f, fill=CHAR, anchor='lm')

title(['SEU FILAMENTO', 'ESTÁ ESTALANDO?', 'SECA SEM ESTUFA'], 560, 104, hl=2)

# rolo com gotas
cx, cy, R = 330, 1250, 190
for r_, c in ((R, GOLD),):
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=GOLD, outline=OL, width=8)
for k in (0.78, 0.58):
    d.ellipse((cx - R * k, cy - R * k, cx + R * k, cy + R * k), outline=OL, width=3)
d.ellipse((cx - R * 0.36, cy - R * 0.36, cx + R * 0.36, cy + R * 0.36), fill=g.CREAM, outline=OL, width=8)
d.ellipse((cx - R * 0.12, cy - R * 0.12, cx + R * 0.12, cy + R * 0.12), fill=OL)
BLUE = (86, 136, 196)
for x, y, s in ((130, 1010, 1.3), (230, 960, 1.6), (360, 990, 1.2)):
    d.polygon([(x, y - 30 * s), (x - 17 * s, y + 4 * s), (x + 17 * s, y + 4 * s)], fill=BLUE, outline=OL)
    d.ellipse((x - 17 * s, y - 12 * s, x + 17 * s, y + 22 * s), fill=BLUE, outline=OL, width=3)

# microondas com X (o que não fazer)
mx, my = 760, 1250
d.rounded_rectangle((mx - 200, my - 130, mx + 200, my + 130), radius=22, fill=(226, 224, 220), outline=OL, width=7)
d.rounded_rectangle((mx - 176, my - 106, mx + 60, my + 106), radius=14, fill=(54, 58, 66), outline=OL, width=5)
for k in range(3):
    d.ellipse((mx + 100 - 18, my - 50 + k * 54 - 18, mx + 100 + 18, my - 50 + k * 54 + 18), fill=(90, 90, 96), outline=OL, width=3)
d.ellipse((mx + 40, my + 40, mx + 200, my + 200), fill=RED, outline=OL, width=6)
q = 36
d.line((mx + 120 - q, my + 120 - q, mx + 120 + q, my + 120 + q), fill=WHITE, width=16)
d.line((mx + 120 - q, my + 120 + q, mx + 120 + q, my + 120 - q), fill=WHITE, width=16)

def chip(cx, cy, txt, ang=0, gold=False):
    g.paste_center(img, g.pill(txt, 34, OL, GOLD if gold else WHITE).rotate(ang, expand=True, resample=Image.BICUBIC), cx, cy)
chip(330, 1540, 'FORNO · CAMA AQUECIDA', -3, gold=True)
chip(720, 1650, 'MICRO-ONDAS: NÃO', 3)
out = g.D + '/out22/capa_seca.png'
img.save(out)
print(out)
