import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, math
sys.path.insert(0, HERE)
import gen4 as g
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
OUT = HERE + '/out9'
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
chips = [('5 CAUSAS', None, 195, 1240, -3), ('1ª CAMADA', 'pencil', 880, 1215, 4),
         ('SALVA ESSE VÍDEO', None, 830, 1350, -3)]
for txt, icon, cx, cy, ang in chips:
    lay = g.rot(g.pill(txt, 26, g.OL, g.GOLD if txt.startswith('1ª') else g.WHITE), ang)
    g.paste_center(img, lay, cx, cy)


# ---- printer theme: nozzle over a bed with a piece peeling off
GOLD_, OLc = g.GOLD, g.OL
d = ImageDraw.Draw(img)
bx0, bx1, by = 80, 1000, 330
d.polygon([(bx0, by), (bx1, by), (bx1, by + 30), (bx0, by + 30)], fill=(206, 200, 190), outline=OLc)
d.polygon([(300, by), (760, by - 44), (760, by - 150), (300, by - 112)], fill=GOLD_, outline=OLc)
for yy in (-40, -76):
    d.line((300, by + yy * 0.9, 760, by + yy * 0.9 - 40 * 0.96), fill=g.GOLDL, width=4)
d.rounded_rectangle((470, 40, 610, 150), radius=14, fill=g.CHAR, outline=OLc, width=4)
d.polygon([(490, 150), (590, 150), (550, 215), (530, 215)], fill=GOLD_, outline=OLc)
pts = [(560 + 130 * f / 30 + 22 * math.sin(f * 0.8), 218 + 100 * (f / 30) ** 2 + 14 * math.cos(f * 1.3)) for f in range(31)]
d.line(pts, fill=GOLD_, width=9, joint='curve')

g.logo_bug(img, 540, 515, 300)

lines = [[('A PEÇA DESCOLOU?', False)], [('QUASE NUNCA É A', False)], [('IMPRESSORA', True)]]
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
img.save(OUT + '/capa_primeira_camada.png')
sheet = Image.new('RGB', (4 * 360 + 30, 640), (120, 120, 120))
for i, c in enumerate([(0, 0, 1080, 1920), (0, 240, 1080, 1680), (0, 285, 1080, 1635), (0, 420, 1080, 1500)]):
    cr = img.crop(c); cr.thumbnail((360, 640)); sheet.paste(cr, (i * 370, 0))
sheet.save(OUT + '/capa_check.png')
print('size', size)
