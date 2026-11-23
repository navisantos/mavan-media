"""Capa do vídeo B de 23/11/2026 (brinde útil): python3 -I cover_brinde.py -> out19/capa_brinde.png"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys
sys.path.insert(0, HERE)
import gen4 as g
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
OL, GOLD, CHAR, WHITE = g.OL, g.GOLD, g.CHAR, g.WHITE
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

def photo(name, crop, box, ang=0):
    im = Image.open(HERE + f'/assets/brindes/{name}.jpg').convert('RGB').crop(crop)
    x0, y0, x1, y1 = box
    im = im.resize((x1 - x0, y1 - y0), Image.LANCZOS).convert('RGBA')
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=30, fill=255)
    im.putalpha(m)
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=30, outline=OL, width=7)
    im = im.rotate(ang, expand=True, resample=Image.BICUBIC)
    g.paste_center(img, im, (x0 + x1) // 2, (y0 + y1) // 2)

title(['BRINDE QUE', 'A PESSOA', 'USA'], 560, 124, hl=2)
photo('ratatouille1', (150, 330, 800, 1130), (70, 960, 400, 1450), -4)
photo('pazinha_racao', (0, 100, 640, 1030), (380, 1010, 700, 1500), 3)
photo('marcador_copo_pacco', (200, 190, 800, 810), (690, 960, 1010, 1450), -3)
d = ImageDraw.Draw(img)
def chip(cx, cy, txt, ang=0, gold=False):
    g.paste_center(img, g.pill(txt, 30, OL, GOLD if gold else WHITE).rotate(ang, expand=True, resample=Image.BICUBIC), cx, cy)
chip(240, 1560, 'CHEF', -3, gold=True)
chip(540, 1590, 'PET SHOP', 3)
chip(840, 1560, 'FIM DE ANO', -3, gold=True)
out = g.D + '/out19/capa_brinde.png'
img.save(out)
print(out)
