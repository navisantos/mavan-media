import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, math
sys.path.insert(0, HERE)
import gen4 as g
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
OUT = HERE + '/out16'
_os.makedirs(OUT, exist_ok=True)
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
chips = [('MENOS FILAMENTO', None, 205, 1240, -3), ('SAI MAIS FÁCIL', None, 855, 1215, 4),
         ('MENOS COLUNA', None, 830, 1350, -3)]
for txt, icon, cx, cy, ang in chips:
    lay = g.rot(g.pill(txt, 26, g.OL, g.GOLD if txt.startswith('SAI') else g.WHITE), ang)
    g.paste_center(img, lay, cx, cy)


# ---- support theme: common (columns) vs tree support
d = ImageDraw.Draw(img)
RED_, SUP, GRN = (214, 64, 64), (226, 176, 74), (72, 150, 88)
def part(x0, x1):
    d.rounded_rectangle((x0, 120, x1, 175), radius=12, fill=RED_, outline=g.OL, width=5)
    for lx in (x0, x1 - 46):
        d.rectangle((lx, 175, lx + 46, 290), fill=RED_, outline=g.OL, width=4)
    d.line((x0 - 30, 290, x1 + 30, 290), fill=g.OL, width=6)
part(100, 440)
n = 6
for k in range(n):
    x = 100 + 70 + k * (340 - 140) / (n - 1)
    d.rectangle((x - 6, 175, x + 6, 290), fill=SUP, outline=g.OL, width=2)
part(640, 980)
cxm = 810
d.line((cxm, 290, cxm, 232), fill=g.OL, width=18); d.line((cxm, 290, cxm, 232), fill=SUP, width=10)
for tx in (-110, 0, 110):
    d.line((cxm, 232, cxm + tx, 175), fill=g.OL, width=16); d.line((cxm, 232, cxm + tx, 175), fill=SUP, width=8)
for cx, lab in [(270, 'COMUM'), (810, 'ÁRVORE')]:
    d.rounded_rectangle((cx - 110, 312, cx + 110, 360), radius=16, fill=g.CHAR, outline=g.OL, width=4)
    d.text((cx, 337), lab, font=ImageFont.truetype(g.FB, 32), fill=g.GOLDL, anchor='mm')
d.text((540, 235), 'x', font=ImageFont.truetype(g.FB, 70), fill=g.OL, anchor='mm')

g.logo_bug(img, 540, 515, 300)

lines = [[('SUPORTE', False)], [('COMUM OU', False)], [('ÁRVORE?', True)]]
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
img.save(OUT + '/capa_suporte.png')
sheet = Image.new('RGB', (4 * 360 + 30, 640), (120, 120, 120))
for i, c in enumerate([(0, 0, 1080, 1920), (0, 240, 1080, 1680), (0, 285, 1080, 1635), (0, 420, 1080, 1500)]):
    cr = img.crop(c); cr.thumbnail((360, 640)); sheet.paste(cr, (i * 370, 0))
sheet.save(OUT + '/capa_check.png')
print('size', size)
