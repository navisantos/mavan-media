import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, math
sys.path.insert(0, HERE)
import gen4 as g
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
OUT = HERE + '/out13'
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
chips = [('FÁCIL', None, 195, 1240, -3), ('RESISTENTE', 'pencil', 860, 1215, 4),
         ('FLEXÍVEL', None, 830, 1350, -3)]
for txt, icon, cx, cy, ang in chips:
    lay = g.rot(g.pill(txt, 26, g.OL, g.GOLD if txt.startswith('RESIST') else g.WHITE), ang)
    g.paste_center(img, lay, cx, cy)


# ---- filament theme: three spools (PLA, PETG, TPU)
d = ImageDraw.Draw(img)
for cx, col, lab in [(240, (214, 64, 64), 'PLA'), (540, (86, 136, 196), 'PETG'), (840, (72, 150, 88), 'TPU')]:
    R, cy = 92, 170
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=col, outline=g.OL, width=6)
    d.ellipse((cx - R * 0.72, cy - R * 0.72, cx + R * 0.72, cy + R * 0.72), outline=g.OL, width=4)
    d.ellipse((cx - R * 0.3, cy - R * 0.3, cx + R * 0.3, cy + R * 0.3), fill=g.CREAM, outline=g.OL, width=5)
    d.arc((cx - R * 0.88, cy - R * 0.88, cx + R * 0.2, cy + R * 0.2), 200, 270, fill=g.WHITE, width=6)
    d.rounded_rectangle((cx - 78, cy + R + 14, cx + 78, cy + R + 62), radius=16, fill=g.CHAR, outline=g.OL, width=4)
    d.text((cx, cy + R + 38), lab, font=ImageFont.truetype(g.FB, 32), fill=g.GOLDL, anchor='mm')

g.logo_bug(img, 540, 515, 300)

lines = [[('PLA, PETG', False)], [('OU TPU?', False)], [('QUAL USAR', True)]]
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
img.save(OUT + '/capa_filamentos.png')
sheet = Image.new('RGB', (4 * 360 + 30, 640), (120, 120, 120))
for i, c in enumerate([(0, 0, 1080, 1920), (0, 240, 1080, 1680), (0, 285, 1080, 1635), (0, 420, 1080, 1500)]):
    cr = img.crop(c); cr.thumbnail((360, 640)); sheet.paste(cr, (i * 370, 0))
sheet.save(OUT + '/capa_check.png')
print('size', size)
