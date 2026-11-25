"""Capa do vídeo B de 25/11/2026 (Mila): python3 -I cover_mila.py -> out21/capa_mila.png
Foto: Mila_close_com_plaquinha.png (imagem gerada por IA, enviada pelo Ivan)."""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys
sys.path.insert(0, HERE)
import gen4 as g
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
OL, GOLD, WHITE, GRAY = g.OL, g.GOLD, g.WHITE, g.GRAY
img = Image.open(HERE + '/assets/mila/mila_close.png').convert('RGB').resize((W, H), Image.LANCZOS)
d = ImageDraw.Draw(img, 'RGBA')
# faixa escura suave embaixo para o texto
for k in range(520):
    a = int(170 * (k / 520) ** 1.4)
    d.line((0, H - 520 + k, W, H - 520 + k), fill=(20, 18, 24, a))
d.rounded_rectangle((36, 40, 346, 176), radius=28, fill=(250, 247, 240, 232))
g.logo_bug(img, 191, 106, 230)
f = ImageFont.truetype(g.FB, 90)
y0 = 1500
for i, t in enumerate(['SEU PET TEM NOME.', 'A PLAQUINHA TEM?']):
    y = y0 + i * 118
    wl = f.getlength(t)
    x = 540 - wl / 2
    if i == 1:
        d.rounded_rectangle((x - 20, y - 62, x + wl + 20, y + 62), radius=24, fill=GOLD)
        d.text((x, y), t, font=f, fill=OL, anchor='lm')
    else:
        d.text((x, y), t, font=f, fill=WHITE, anchor='lm', stroke_width=8, stroke_fill=OL)
g.paste_center(img, g.pill('ILUSTRAÇÃO GERADA POR IA', 26, GRAY, WHITE), 540, 1830)
out = g.D + '/out21/capa_mila.png'
img.save(out)
print(out)
