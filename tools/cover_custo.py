import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, math
sys.path.insert(0, HERE)
import gen4 as g
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
OUT = '/tmp/claude-0/-home-claude/06e0c612-1d53-5ee2-85ec-a21396d1799c/scratchpad/out7'
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
chips = [('FILAMENTO R$ 5', 'pencil', 235, 1075, 4), ('ENERGIA R$ 0,30', None, 225, 1250, -3),
         ('FALHA 20%', None, 860, 1150, -4), ('TOTAL ≈ R$ 6,60', None, 835, 1440, 3)]
for txt, icon, cx, cy, ang in chips:
    lay = g.rot(g.pill(txt, 30, g.OL, g.GOLD if txt.startswith('1') else g.WHITE), ang)
    g.paste_center(img, lay, cx, cy)


# ---- tema: custo (moedas e carretel)
d = ImageDraw.Draw(img)
def coin(d, cx, cy, r, top):
    d.line((cx, top, cx, cy - r), fill=g.OL, width=4)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=g.GOLD, outline=g.OL, width=4)
    d.ellipse((cx - r * 0.72, cy - r * 0.72, cx + r * 0.72, cy + r * 0.72), outline=g.OL, width=3)
    d.text((cx, cy + 2), 'R$', font=g.font(g.FB, int(r * 0.7)), fill=g.OL, anchor='mm')
for cx, cy, r in [(110, 250, 52), (270, 170, 40), (540, 120, 34), (810, 190, 44), (970, 280, 56), (400, 300, 30), (690, 330, 36)]:
    coin(d, cx, cy, r, 0)
g.logo_bug(img, 540, 515, 300)

lines = [[('QUANTO CUSTA', False)], [('IMPRIMIR UMA', False)], [('PEÇA', True), (' DE VERDADE?', False)]]
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
img.save(OUT + '/capa_custo.png')
sheet = Image.new('RGB', (4 * 360 + 30, 640), (120, 120, 120))
for i, c in enumerate([(0, 0, 1080, 1920), (0, 240, 1080, 1680), (0, 285, 1080, 1635), (0, 420, 1080, 1500)]):
    cr = img.crop(c); cr.thumbnail((360, 640)); sheet.paste(cr, (i * 370, 0))
sheet.save(OUT + '/capa_check.png')
print('size', size)
