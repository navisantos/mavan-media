"""Capas dos vídeos explicativos sem personagem (21/11/2026).
    python3 -I cover_explica.py tt   -> out17/capa_praia.png
    python3 -I cover_explica.py ig   -> out18/capa_kettlebell.png
"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, math
sys.path.insert(0, HERE)
import gen4 as g
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
KEY = sys.argv[1] if len(sys.argv) > 1 else 'tt'
SKY, SAND, SEA, SEAD = (206, 232, 244), (238, 218, 170), (110, 178, 214), (72, 140, 190)
OL, GOLD, GOLDL, CHAR, WHITE = g.OL, g.GOLD, g.GOLDL, g.CHAR, g.WHITE

img = Image.new('RGB', (W, H), g.CREAM)
d = ImageDraw.Draw(img)
for k in range(0, H + 54, 54):
    d.line((0, k, W, k), fill=g.LINEC, width=2)
g.logo_bug(img, 540, 270, 300)

def title(lines, y0, size=128, hl=-1):
    f = ImageFont.truetype(g.FB, size)
    d2 = ImageDraw.Draw(img)
    for i, t in enumerate(lines):
        y = y0 + int(i * size * 1.22)
        wl = f.getlength(t)
        x = 540 - wl / 2
        if i == hl:
            d2.rounded_rectangle((x - 18, y - size * 0.62, x + wl + 18, y + size * 0.62), radius=20, fill=GOLD)
        d2.text((x, y), t, font=f, fill=CHAR, anchor='lm')

def chip(cx, cy, txt, ang=0, gold=False):
    lay = g.rot(g.pill(txt, 30, OL, GOLD if gold else WHITE), ang)
    g.paste_center(img, lay, cx, cy)

if KEY == 'tt':
    title(['5 PROBLEMAS', 'DE IMPRIMIR', 'NA PRAIA'], 560, 124, hl=2)
    # cena de praia com impressora
    x0, x1, y0, y1 = 90, 990, 1000, 1500
    d.rounded_rectangle((x0, y0, x1, y1), radius=36, fill=SKY, outline=OL, width=6)
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((x0 + 3, y0 + 3, x1 - 3, y1 - 3), radius=34, fill=255)
    scene = Image.new('RGB', (W, H), SKY)
    sd = ImageDraw.Draw(scene)
    sd.rectangle((0, 1290, W, H), fill=SAND)
    for k in range(3):
        pts = [(x, 1250 + k * 34 + 9 * math.sin(x / 38.0 + k * 1.3)) for x in range(0, W + 1, 10)]
        sd.line(pts, fill=SEA if k % 2 == 0 else SEAD, width=8)
    sd.line((0, 1292, W, 1292), fill=OL, width=5)
    # sol
    cx, cy, R = 800, 1130, 64
    for k in range(12):
        a = k * math.pi / 6
        sd.line((cx + (R + 12) * math.cos(a), cy + (R + 12) * math.sin(a), cx + (R + 40) * math.cos(a), cy + (R + 40) * math.sin(a)), fill=GOLD, width=9)
    sd.ellipse((cx - R, cy - R, cx + R, cy + R), fill=GOLD, outline=OL, width=5)
    # guarda-sol
    sd.line((250, 1180, 250, 1440), fill=OL, width=9)
    sd.pieslice((130, 1100, 370, 1280), 180, 360, fill=(214, 90, 90), outline=OL, width=5)
    # impressora
    cxp, yb, s = 600, 1470, 0.92
    sd.rounded_rectangle((cxp - 190 * s, yb - 34 * s, cxp + 190 * s, yb), radius=8, fill=CHAR, outline=OL, width=3)
    for sx in (-1, 1):
        sd.rectangle((cxp + sx * 170 * s - 14 * s, yb - 330 * s, cxp + sx * 170 * s + 14 * s, yb - 34 * s), fill=(176, 180, 188), outline=OL, width=3)
    sd.rounded_rectangle((cxp - 190 * s, yb - 350 * s, cxp + 190 * s, yb - 318 * s), radius=8, fill=CHAR, outline=OL, width=3)
    sd.rectangle((cxp - 160 * s, yb - 230 * s, cxp + 160 * s, yb - 210 * s), fill=GOLD, outline=OL, width=3)
    sd.rounded_rectangle((cxp + 10, yb - 262 * s, cxp + 82, yb - 212 * s), radius=8, fill=CHAR, outline=OL, width=3)
    sd.polygon([(cxp + 28, yb - 212 * s), (cxp + 64, yb - 212 * s), (cxp + 50, yb - 170 * s), (cxp + 42, yb - 170 * s)], fill=GOLD, outline=OL)
    sd.rectangle((cxp - 130 * s, yb - 74 * s, cxp + 130 * s, yb - 50 * s), fill=(206, 200, 190), outline=OL, width=3)
    sd.rectangle((cxp - 60 * s, yb - 130 * s, cxp + 60 * s, yb - 74 * s), fill=GOLD, outline=OL, width=3)
    # gotas de suor
    for k in range(3):
        x, y = 780 + k * 50, 1330 + (k % 2) * 24
        sd.polygon([(x, y - 26), (x - 15, y + 4), (x + 15, y + 4)], fill=(86, 136, 196), outline=OL)
        sd.ellipse((x - 15, y - 10, x + 15, y + 20), fill=(86, 136, 196), outline=OL, width=3)
    img.paste(scene, (0, 0), mask)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0, x1, y1), radius=36, outline=OL, width=6)
    chip(250, 1040, 'UMIDADE', -4)
    chip(560, 1020, 'MARESIA', 3)
    chip(850, 1060, 'AREIA', -3)
    chip(330, 1560, 'CALOR', 3, gold=True)
    chip(700, 1575, 'ENERGIA', -3)
    out = g.D + '/out17/capa_praia.png'
else:
    title(['TREINO NA', 'PRAIA E A', 'ALIANÇA?'], 560, 124, hl=2)
    photo = Image.open(HERE + '/assets/kettlebell_real.jpg').convert('RGB').crop((90, 820, 1390, 1805)).resize((780, 591), Image.LANCZOS)
    pim = photo.convert('RGBA')
    m = Image.new('L', pim.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, pim.width - 1, pim.height - 1), radius=34, fill=255)
    pim.putalpha(m)
    ImageDraw.Draw(pim).rounded_rectangle((0, 0, pim.width - 1, pim.height - 1), radius=34, outline=OL, width=7)
    img.paste(pim, (150, 1010), pim)
    # sol e ondas no canto, tema de praia
    d = ImageDraw.Draw(img)
    cx, cy, R = 290, 1105, 46
    for k in range(12):
        a = k * math.pi / 6
        d.line((cx + (R + 10) * math.cos(a), cy + (R + 10) * math.sin(a), cx + (R + 32) * math.cos(a), cy + (R + 32) * math.sin(a)), fill=GOLD, width=8)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=GOLD, outline=OL, width=5)
    for k in range(2):
        pts = [(x, 1650 + k * 30 + 8 * math.sin(x / 38.0 + k)) for x in range(90, 991, 10)]
        d.line(pts, fill=SEA if k == 0 else SEAD, width=8)
    chip(300, 1560, 'KETTLEBELL PORTA-JOIAS', -3, gold=True)
    chip(760, 1600, 'ABRE COM ROSCA', 3)
    out = g.D + '/out18/capa_kettlebell.png'

img.save(out)
print(out)
