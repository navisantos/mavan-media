import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, math
sys.path.insert(0, HERE)
import gen4 as g
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
OUT = HERE + '/out6'
img = g.bg_cu(0.0, 540)
d = ImageDraw.Draw(img)
items = [('spark', 880, 1060, 50, 0.2), ('spark', 190, 1040, 40, 1.1), ('sparkw', 900, 1500, 32, 2.0), ('spark', 150, 1480, 36, 0.7)]
g.draw_value_items(img, items, 1.6, 0.0)

# Mari close-up
k, Y0, CU_HY = 2.2, 700, 1260
cx_char, base = 300, 770
hy_char = base - 478
st = g.Stage(W, H - Y0, k, 540 - cx_char * k, (CU_HY - Y0) - hy_char * k)
g.draw_mari(st, cx_char, base, 0.55, 0, 0.9, False, True, True)
small = st.im.resize((W, H - Y0), Image.LANCZOS)
img.paste(small, (0, Y0), small)

# setting chips around her (settings the manual hides)
chips = [('1 · NOME + FOTO', 'pencil', 235, 1075, 4), ('2 · ANO GRAVADO', None, 250, 1250, -3),
         ('3 · ETIQUETA', None, 810, 1190, -4), ('4 · KIT PINTURA', None, 790, 1330, 3)]
for txt, icon, cx, cy, ang in chips:
    lay = g.rot(g.pill(txt, 30, g.OL, g.GOLD if txt.startswith('1') else g.WHITE), ang)
    g.paste_center(img, lay, cx, cy)


# ---- Christmas theme: hanging ornaments + Santa hat
RED_, GREEN_, BLUE_ = (214, 64, 64), (72, 150, 88), (86, 136, 196)
def orn(d, cx, cy, r, col, top):
    d.line((cx, top, cx, cy - r - 8), fill=g.OL, width=4)
    d.rounded_rectangle((cx - r * 0.3, cy - r - 12, cx + r * 0.3, cy - r + 4), radius=4, fill=g.GOLD, outline=g.OL, width=3)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=g.OL, width=4)
    d.arc((cx - r * 0.72, cy - r * 0.72, cx + r * 0.25, cy + r * 0.25), 200, 275, fill=g.WHITE, width=5)
    d.arc((cx - r, cy - r * 0.2, cx + r, cy + r * 0.2), 0, 180, fill=g.WHITE, width=4)
d = ImageDraw.Draw(img)
for cx, cy, r, col, top in [(110, 250, 52, RED_, 0), (270, 170, 40, g.GOLD, 0), (540, 120, 34, BLUE_, 0),
                            (810, 190, 44, GREEN_, 0), (970, 280, 56, RED_, 0), (400, 300, 30, g.WHITE, 0), (690, 330, 36, g.GOLD, 0)]:
    orn(d, cx, cy, r, col, top)
# Santa hat on Mari (head ~ x390-690, hair top ~ y1095)
hat = Image.new('RGBA', (W, H), (0, 0, 0, 0))
hd = ImageDraw.Draw(hat)
cone = [(400, 1105), (445, 1040), (540, 998), (640, 985), (735, 1000), (775, 1040), (700, 1050), (690, 1105)]
hd.polygon(cone, fill=RED_, outline=g.OL)
hd.line(cone + [cone[0]], fill=g.OL, width=5, joint='curve')
hd.rounded_rectangle((383, 1078, 707, 1140), radius=30, fill=g.WHITE, outline=g.OL, width=5)
hd.ellipse((745, 1002, 821, 1078), fill=g.WHITE, outline=g.OL, width=5)
img.paste(hat, (0, 0), hat)

g.logo_bug(img, 540, 515, 300)

lines = [[('ENFEITE DE NATAL', False)], [('COM A FOTO DA', False)], [('SUA', True), (' FAMÍLIA', False)]]
def lt(segs): return ''.join(t for t, _ in segs)
size = 130
while True:
    f = ImageFont.truetype(g.FB, size)
    if max(f.getlength(lt(s)) for s in lines) <= 900 or size < 60:
        break
    size -= 2
f = ImageFont.truetype(g.FB, size)
ys = [660, 660 + int(size * 1.22), 660 + int(size * 2.44)]
d = ImageDraw.Draw(img)
for segs, y in zip(lines, ys):
    wl = f.getlength(lt(segs))
    x = 540 - wl / 2
    for txt, hl in segs:
        wt = f.getlength(txt)
        if hl:
            d.rounded_rectangle((x - 14, y - size * 0.62, x + wt + 14, y + size * 0.62), radius=18, fill=g.GOLD)
        d.text((x, y), txt, font=f, fill=g.CHAR, anchor='lm')
        x += wt
img.save(OUT + '/capa_natal_v2.png')
sheet = Image.new('RGB', (4 * 360 + 30, 640), (120, 120, 120))
for i, c in enumerate([(0, 0, 1080, 1920), (0, 240, 1080, 1680), (0, 285, 1080, 1635), (0, 420, 1080, 1500)]):
    cr = img.crop(c); cr.thumbnail((360, 640)); sheet.paste(cr, (i * 370, 0))
sheet.save(OUT + '/capa_check.png')
print('size', size)
