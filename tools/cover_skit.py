import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, math
sys.path.insert(0, HERE)
import gen4 as g
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
OUT = g.OUT

# background: sunburst + soft gold disc behind Mari
img = g.bg_cu(0.0, 540)
d = ImageDraw.Draw(img)

# value items around her (coins / price tag / sparkles)
items = [('coin', 880, 1090, 56, 0.2), ('coin', 930, 1380, 44, 1.0), ('tag', 215, 1585, 0, 0.7),
         ('spark', 760, 1010, 46, 0.3), ('spark', 190, 1010, 38, 1.1), ('sparkw', 860, 1250, 30, 2.0)]
g.draw_value_items(img, items, 1.6, 0.0)

# big coin with a "no" sign: "NÃO é máquina de dinheiro"
coin = g.coin_layer(84)
g.paste_center(img, coin, 200, 1330)
d = ImageDraw.Draw(img)
cx, cy, r = 200, 1330, 112
d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=g.RED, width=16)
a = math.radians(45)
d.line((cx - r * math.cos(a), cy - r * math.sin(a), cx + r * math.cos(a), cy + r * math.sin(a)), fill=g.RED, width=16)

# Mari: close-up, hand raised toward the headline, eyebrows up
k = 2.2
Y0 = 700
CU_HY = 1260
cx_char, base = 300, 770
hy_char = base - 478
st = g.Stage(W, H - Y0, k, 540 - cx_char * k, (CU_HY - Y0) - hy_char * k)
g.draw_mari(st, cx_char, base, 0.55, 0, 0.9, False, True, True)
small = st.im.resize((W, H - Y0), Image.LANCZOS)
img.paste(small, (0, Y0), small)

# logo (inside the 4:5 grid crop)
g.logo_bug(img, 540, 515, 300)

# headline: auto-fit so the longest line spans ~900px
lines = [[('IMPRESSORA 3D', False)], [('NÃO', True), (' É MÁQUINA', False)], [('DE DINHEIRO', False)]]
def line_text(segs):
    return ''.join(t for t, _ in segs)
size = 130
while True:
    f = ImageFont.truetype(g.FB, size)
    wmax = max(f.getlength(line_text(s)) for s in lines)
    if wmax <= 900 or size < 60:
        break
    size -= 2
f = ImageFont.truetype(g.FB, size)
ys = [700, 700 + int(size * 1.22), 700 + int(size * 2.44)]
d = ImageDraw.Draw(img)
for segs, y in zip(lines, ys):
    wl = f.getlength(line_text(segs))
    x = 540 - wl / 2
    for txt, hl in segs:
        wt = f.getlength(txt)
        if hl:
            d.rounded_rectangle((x - 14, y - size * 0.62, x + wt + 14, y + size * 0.62), radius=18, fill=g.GOLD)
        d.text((x, y), txt, font=f, fill=g.CHAR, anchor='lm')
        x += wt

img.save(OUT + '/capa_mavan_reels.png')

# crop check: full / 3:4 grid / 4:5 / 1:1 (centered)
sheet = Image.new('RGB', (4 * 360 + 30, 640), (120, 120, 120))
crops = [(0, 0, 1080, 1920), (0, 240, 1080, 1680), (0, 285, 1080, 1635), (0, 420, 1080, 1500)]
for i, c in enumerate(crops):
    cr = img.crop(c)
    cr.thumbnail((360, 640))
    sheet.paste(cr, (i * 370, 0))
sheet.save(OUT + '/capa_check.png')
print('size', size)
