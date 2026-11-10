import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
sys.path.insert(0, HERE)
import gen4 as g
from gen4 import (W, H, FPS, CREAM, CHAR, OL, GOLD, GOLDL, WARM, LINEC, GRAY, RED, WHITE, FB, FM,
                  Stage, draw_mari, draw_cliente, pill, tl, font, eob, paste_pop, paste_center, put, rot,
                  draw_icon, logo_w, logo_bug)

D = g.D
OUT = D + '/out6'
os.makedirs(OUT, exist_ok=True)
AF = D + '/aud6/fin/'

LINES = [
    ('01.wav', 'cliente', 'Enfeite de Natal? Compro uma bola vermelha no mercado. Todo mundo tem.'),
    ('02.wav', 'mari', 'Bah! A Mavan 3D pode imprimir o seu enfeite personalizado! Quer exemplos? Então toma!'),
    ('03.wav', 'mari', '1) Enfeite com o nome da sua marca e um espaço para a foto da família.'),
    ('04.wav', 'mari', '2) Enfeite com o ano gravado, para a família montar uma coleção.'),
    ('05.wav', 'mari', '3) Etiqueta de presente que vira enfeite depois do Natal.'),
    ('06.wav', 'mari', '4) Kit para pintar em casa. Cada um faz o seu.'),
    ('07.wav', 'cliente', 'Tá… então a bola do mercado perdeu.'),
    ('08.wav', 'mari', 'Comenta o número da sua favorita e manda pra quem monta a árvore.'),
]
LEAD, GAP, HOLD, ENDCARD = 0.25, 0.30, 1.9, 1.2

AUD = []
for fn, spk, txt in LINES:
    s, e, env = g.analyse(AF + fn)
    AUD.append(dict(file=AF + fn, spk=spk, txt=txt, s=s, e=e, d=e - s, env=env))
P = []
tcur = LEAD
for a in AUD:
    P.append(tcur)
    tcur += a['d'] + GAP
CEND = P[-1] + AUD[-1]['d'] + HOLD
TOTAL = CEND + ENDCARD
N = len(AUD)

# ---------------------------------------------------------------- small helpers
def sm(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def lerp(a, b, u):
    return a + (b - a) * u

def T(d, x, y, txt, size, fill=OL, anchor='lm', fp=None):
    d.text((x, y), txt, font=font(fp or FB, size), fill=fill, anchor=anchor)

def rr(d, box, r, fill, ol=OL, w=4):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=ol, width=w)

def path(t, keys):
    if t <= keys[0][0]:
        return keys[0][1], keys[0][2]
    for (t0, x0, y0), (t1, x1, y1) in zip(keys, keys[1:]):
        if t <= t1:
            u = sm((t - t0) / (t1 - t0))
            return lerp(x0, x1, u), lerp(y0, y1, u)
    return keys[-1][1], keys[-1][2]

def cursor(img, x, y, click=-1.0):
    d = ImageDraw.Draw(img)
    if 0 <= click < 1:
        r = 12 + 44 * click
        d.ellipse((x - r, y - r, x + r, y + r), outline=GOLD, width=6)
    pts = [(0, 0), (0, 36), (10, 27), (17, 42), (25, 38), (18, 24), (30, 24)]
    pp = [(x + a, y + b) for a, b in pts]
    d.polygon(pp, fill=WHITE)
    d.line(pp + [pp[0]], fill=OL, width=3, joint='curve')

def typed(txt, r, t0, t1):
    u = (r - t0) / max(0.01, (t1 - t0))
    return txt[:int(len(txt) * max(0.0, min(1.0, u)) + 0.0001)]

def lock(d, x, y, col=GRAY):
    d.rounded_rectangle((x, y + 10, x + 22, y + 32), radius=4, fill=col)
    d.arc((x + 3, y - 2, x + 19, y + 22), 180, 360, fill=col, width=4)

def check(d, x, y, s=1.0, col=OL):
    d.line([(x - 9 * s, y), (x - 2 * s, y + 8 * s), (x + 11 * s, y - 9 * s)], fill=col, width=6, joint='curve')

# ---------------------------------------------------------------- window geometry
SX0, SX1 = 70, 1010
SY0, SY1 = 355, 805
TB = 54
CY0 = SY0 + TB   # content origin (y = 0 here)
BED_REL = 350

TITLES = ['ENFEITE DO MERCADO', 'ENFEITES MAVAN 3D', '1 · NOME DA MARCA + FOTO', '2 · ANO GRAVADO',
          '3 · ETIQUETA QUE VIRA ENFEITE', '4 · KIT PINTE EM CASA', 'A BOLA DO MERCADO PERDEU', 'QUAL É A SUA FAVORITA?']

def window(img, i, t):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((SX0 + 10, SY0 + 12, SX1 + 10, SY1 + 12), radius=28, fill=(214, 206, 192))
    rr(d, (SX0, SY0, SX1, SY1), 28, (253, 251, 247), OL, 5)
    d.rounded_rectangle((SX0, SY0, SX1, SY0 + TB), radius=28, fill=CHAR)
    d.rectangle((SX0, SY0 + 30, SX1, SY0 + TB), fill=CHAR)
    d.rectangle((SX0 + 2, SY0 + TB - 1, SX1 - 2, SY0 + TB + 1), fill=CHAR)
    for k, col in enumerate((GOLD, GOLDL, WHITE)):
        d.ellipse((SX0 + 28 + k * 30 - 9, SY0 + 27 - 9, SX0 + 28 + k * 30 + 9, SY0 + 27 + 9), fill=col)
    col = GOLD if i in (0, 7) else WHITE
    size = 28 if len(TITLES[i]) < 28 else 25
    T(d, 560, SY0 + 28, TITLES[i], size, col, 'mm')
    return d

def foot(d, txt='valores ilustrativos'):
    T(d, SX1 - 22, SY1 - 16, txt, 17, GRAY, 'rm', FM)

def Y(v):
    return CY0 + v

# ---------------------------------------------------------------- Natal scenes (y relative to CY0)
GREEN, GREEND, BLUE, BROWN = (72, 150, 88), (52, 118, 66), (86, 136, 196), (140, 100, 70)
PAPER = (250, 246, 238)

def clamp(x):
    return max(0.0, min(1.0, x))

def pop(r, start, dur=0.3):
    return eob(clamp((r - start) / dur))

def ornament(d, cx, cy, r, col, ring=True, ol=OL, hl=True):
    if r < 3:
        return
    if ring:
        d.ellipse((cx - 9, cy - r - 30, cx + 9, cy - r - 10), outline=ol, width=4)
    d.rounded_rectangle((cx - r * 0.3, cy - r - 12, cx + r * 0.3, cy - r + 6), radius=4, fill=GOLD, outline=ol, width=3)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=ol, width=4)
    if hl:
        d.arc((cx - r * 0.72, cy - r * 0.72, cx + r * 0.25, cy + r * 0.25), 200, 275, fill=WHITE, width=max(3, int(r * 0.07)))

def num(d, x, y, n, size=30, col=WHITE):
    T(d, x, y, str(n), size, col, 'mm')

def star(d, cx, cy, R, fill=GOLD):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr_ = R if k % 2 == 0 else R * 0.45
        pts.append((cx + rr_ * math.cos(a), cy + rr_ * math.sin(a)))
    d.polygon(pts, fill=fill, outline=OL)

def tree(d, cx, top, base, wmax, ornaments=()):
    levels = [(0.55, 0.0, 0.42), (0.78, 0.25, 0.7), (1.0, 0.5, 1.0)]
    h = base - top
    for w, a, b in levels:
        d.polygon([(cx, top + h * a), (cx - wmax * w, top + h * b), (cx + wmax * w, top + h * b)], fill=GREEN, outline=OL)
    d.rectangle((cx - wmax * 0.12, base, cx + wmax * 0.12, base + h * 0.12), fill=BROWN, outline=OL, width=3)
    star(d, cx, top - 2, wmax * 0.2)

def family(d, cx, cy, s=1.0):
    cols = [(124, 56, 66), (76, 106, 154), (236, 176, 62)]
    spec = [(-38, 0, 15, 40), (36, 0, 15, 40), (0, 18, 11, 28)]
    for (dx, dy, hr, bh), c in zip(spec, cols):
        x, y = cx + dx * s, cy + dy * s
        d.rounded_rectangle((x - hr * 1.7 * s, y + hr * 0.9 * s, x + hr * 1.7 * s, y + (hr + bh) * s), radius=int(10 * s), fill=c, outline=OL, width=3)
        d.ellipse((x - hr * s, y - hr * s, x + hr * s, y + hr * s), fill=(246, 208, 178), outline=OL, width=3)

def arrow(d, x0, y0, x1, y1, col=OL, w=5):
    d.line((x0, y0, x1, y1), fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0)
    for s in (-0.5, 0.5):
        d.line((x1, y1, x1 - 20 * math.cos(a + s), y1 - 20 * math.sin(a + s)), fill=col, width=w)

def sc_hook(img, d, t, r, Dd):
    for k in range(9):
        s = pop(r, 0.05 + k * 0.05)
        ornament(d, 130 + k * 100, Y(55), int(24 * s), RED, ring=False)
    s = pop(r, 0.25)
    ornament(d, 540, Y(215), int(98 * s), RED)
    if r > 0.9:
        s2 = pop(r, 0.9)
        x0, y0 = 690, Y(170)
        d.rounded_rectangle((x0, y0, x0 + 150 * s2, y0 + 70 * s2), radius=10, fill=PAPER, outline=OL, width=4)
        if s2 > 0.8:
            T(d, x0 + 75, y0 + 36, 'R$ 5', 36, RED, 'mm')
    if r > Dd * 0.55:
        T(d, 540, Y(355), 'TODO MUNDO TEM', 36, GRAY, 'mm')

def sc_tree(img, d, t, r, Dd):
    tree(d, 540, Y(70), Y(335), 210)
    spots = [(470, Y(185), RED, 1), (615, Y(235), BLUE, 2), (455, Y(290), GOLD, 3), (625, Y(315), (240, 235, 226), 4)]
    for k, (x, y, c, n) in enumerate(spots):
        s = pop(r, Dd * 0.38 + k * Dd * 0.13)
        if s > 0.02:
            ornament(d, x, y, int(26 * s), c, ring=False, hl=False)
            if s > 0.7:
                num(d, x, y, n, 26, OL if n == 4 else WHITE)
    T(d, 130, Y(210), 'SEU NOME', 30, GRAY, 'lm')
    T(d, 130, Y(250), 'SUA FOTO', 30, GRAY, 'lm')
    T(d, 130, Y(290), 'SEU ANO', 30, GRAY, 'lm')

def sc_brand(img, d, t, r, Dd):
    cx, cy, R = 540, Y(205), 135
    s = pop(r, 0.1)
    ornament(d, cx, cy, int(R * s), GOLD)
    if r > Dd * 0.3:
        s2 = pop(r, Dd * 0.3)
        w, h = 88 * s2, 74 * s2
        d.ellipse((cx - w, cy - 95 * s2, cx + w, cy + 35 * s2 + 0), fill=PAPER, outline=OL, width=4)
        if s2 > 0.8:
            family(d, cx, cy - 55, 0.95)
        T(d, 170, Y(115), 'FOTO DA', 28, GRAY, 'lm')
        T(d, 170, Y(150), 'FAMÍLIA', 28, GRAY, 'lm')
        arrow(d, 340, Y(130), cx - 100, Y(130))
    if r > Dd * 0.55:
        d.rounded_rectangle((cx - 100, cy + 55, cx + 100, cy + 102), radius=14, fill=CHAR, outline=OL, width=3)
        txt = typed('SUA MARCA', r, Dd * 0.55, Dd * 0.8)
        T(d, cx, cy + 79, txt, 28, GOLDL, 'mm')
        if r > Dd * 0.8:
            T(d, 930, Y(352), 'NOME DA MARCA', 28, GRAY, 'rm')
            arrow(d, 800, Y(335), cx + 108, cy + 98)

def sc_year(img, d, t, r, Dd):
    xs = [185, 395, 605, 815]
    yrs = ['2024', '2025', '2026', '2027']
    for k, (x, yr) in enumerate(zip(xs, yrs)):
        s = pop(r, 0.1 + k * Dd * 0.16)
        rad = int(66 * s)
        if rad < 3:
            continue
        y = Y(185)
        if k == 2:
            d.ellipse((x - rad - 14, y - rad - 14, x + rad + 14, y + rad + 14), fill=GOLDL)
            ornament(d, x, y, rad, RED)
        elif k == 3:
            for a in range(0, 360, 30):
                d.arc((x - rad, y - rad, x + rad, y + rad), a, a + 16, fill=GRAY, width=4)
            T(d, x, y, '?', 54, GRAY, 'mm')
        else:
            ornament(d, x, y, rad, (232, 226, 214), ol=GRAY, hl=False)
        if s > 0.7:
            T(d, x, Y(300), yr, 34, OL if k == 2 else GRAY, 'mm')
            if k < 3:
                T(d, x, y + 2, yr[2:], 40, WHITE if k == 2 else GRAY, 'mm')
    if r > Dd * 0.75:
        T(d, 540, Y(365), 'COLEÇÃO DA FAMÍLIA', 32, OL, 'mm')

def tag_shape(d, x, y, w, h, hole=True):
    pts = [(x, y), (x + w - h * 0.22, y), (x + w, y + h * 0.22), (x + w, y + h), (x, y + h)]
    d.polygon(pts, fill=WHITE, outline=OL)
    d.line(pts + [pts[0]], fill=OL, width=4)
    if hole:
        d.ellipse((x + w * 0.5 - 9, y + 14, x + w * 0.5 + 9, y + 32), fill=CREAM, outline=OL, width=3)

def sc_tag(img, d, t, r, Dd):
    s = pop(r, 0.1)
    if s > 0.02:
        x, y, w, h = 150, Y(70), 190 * s, 250 * s
        d.line((x + w * 0.5, y + 23 * s, x + w * 0.5 - 40, y - 40), fill=RED, width=4)
        tag_shape(d, x, y, w, h)
        if s > 0.8:
            T(d, x + w / 2, y + 100, 'PARA: VOVÓ', 24, OL, 'mm')
            T(d, x + w / 2, y + 145, 'DE: JOÃO', 24, GRAY, 'mm')
            draw_icon(d, 'heart', x + w / 2, y + 200, 22) if False else None
    if r > Dd * 0.42:
        s2 = pop(r, Dd * 0.42)
        arrow(d, 400, Y(190), 400 + 150 * s2, Y(190))
        T(d, 475, Y(150), 'DEPOIS DO NATAL', 24, GRAY, 'mm')
    if r > Dd * 0.55:
        s3 = pop(r, Dd * 0.55)
        tree(d, 790, Y(60), Y(300), 140)
        t2 = int(46 * s3)
        d.line((770, Y(150), 770, Y(150) + 28 * s3), fill=RED, width=3)
        tag_shape(d, 748, Y(178), 46 * s3, 62 * s3, hole=False)
        if s3 > 0.8:
            T(d, 790, Y(350), 'VIROU ENFEITE', 30, OL, 'mm')

def sc_kit(img, d, t, r, Dd):
    cols = [RED, BLUE, GREEN]
    for k in range(3):
        x = 230 + k * 310
        s = pop(r, 0.1 + k * 0.12)
        rad = int(72 * s)
        u = clamp((r - Dd * (0.3 + 0.18 * k)) / (Dd * 0.2))
        base = tuple(int(255 + (c - 255) * u) for c in cols[k])
        ornament(d, x, Y(150), rad, base)
        if u > 0.6 and rad > 40:
            for a in range(4):
                ang = a * 1.57 + 0.5
                d.ellipse((x + 38 * math.cos(ang) - 7, Y(150) + 38 * math.sin(ang) - 7, x + 38 * math.cos(ang) + 7, Y(150) + 38 * math.sin(ang) + 7), fill=WHITE)
    for k, c in enumerate(cols):
        x = 400 + k * 90
        d.rounded_rectangle((x - 26, Y(285), x + 26, Y(325)), radius=10, fill=c, outline=OL, width=3)
        d.rectangle((x - 18, Y(275), x + 18, Y(287)), fill=WHITE, outline=OL, width=3)
    d.line((820, Y(325), 900, Y(255)), fill=BROWN, width=10)
    d.polygon([(900, Y(255)), (925, Y(230)), (938, Y(243)), (912, Y(269))], fill=GOLD, outline=OL)
    if r > Dd * 0.7:
        T(d, 540, Y(362), 'CADA UM FAZ O SEU', 28, GRAY, 'mm')

def sc_lose(img, d, t, r, Dd):
    xs = [215, 405, 595, 785]
    cs = [GOLD, (240, 235, 226), RED, BLUE]
    for k in range(4):
        s = pop(r, 0.05 + k * 0.08)
        ornament(d, xs[k], Y(110), int(46 * s), cs[k], ring=False, hl=False)
        if s > 0.7:
            num(d, xs[k], Y(110), k + 1, 28, OL if k == 1 else WHITE)
    sh = 1.0 - 0.45 * sm((r - Dd * 0.35) / 0.5)
    ornament(d, 540, Y(285), int(70 * sh), RED, ring=False)
    if r > Dd * 0.3:
        u = sm((r - Dd * 0.3) / 0.25)
        d.line((470, Y(215), 470 + 140 * u, Y(215) + 140 * u), fill=OL, width=10)
        d.line((610, Y(215), 610 - 140 * u, Y(215) + 140 * u), fill=OL, width=10)
    T(d, 540, Y(375), 'R$ 5 · TODO MUNDO TEM', 26, GRAY, 'mm')

def sc_cta(img, d, t, r, Dd):
    labels = ['FOTO + MARCA', 'ANO GRAVADO', 'ETIQUETA', 'KIT PINTURA']
    cs = [GOLD, RED, (240, 235, 226), BLUE]
    for k in range(4):
        x0 = 120 + (k % 2) * 430
        y = Y(105 + (k // 2) * 175)
        s = pop(r, 0.05 + k * 0.1)
        ornament(d, x0 + 50, y, int(48 * s), cs[k], ring=False)
        if s > 0.7:
            num(d, x0 + 50, y, k + 1, 30, OL if k == 2 else WHITE)
            T(d, x0 + 122, y, labels[k], 28, OL, 'lm')
    T(d, 540, Y(375), 'COMENTA O NÚMERO', 30, GRAY, 'mm')

SCENES = [sc_hook, sc_tree, sc_brand, sc_year, sc_tag, sc_kit, sc_lose, sc_cta]

# ---------------------------------------------------------------- bubbles
BS, BLH, BPAD, BMAXW = 36, 48, 26, 860
EMPH = {'1', '2', '3', '4', 'nome', 'marca', 'foto', 'ano', 'gravado', 'etiqueta', 'kit', 'pintar', 'mavan', '3d', 'personalizado', 'favorita', 'número', 'coleção'}
_bub = {}

def emph(w):
    return ''.join(c for c in w.lower() if c.isalnum() or c == '%') in EMPH

def make_bubble(i, tipx):
    key = (i, tipx)
    if key in _bub:
        return _bub[key]
    a = AUD[i]
    lines = g.wrap(a['txt'], BS, BMAXW - 2 * BPAD)
    f = font(FB, BS)
    wmax = max(f.getlength(' '.join(l)) for l in lines)
    w = int(wmax + 2 * BPAD)
    h = int(len(lines) * BLH + 2 * BPAD - 6)
    x0 = tipx - w * 0.3 if tipx < 540 else tipx - w * 0.7
    x0 = max(36, min(930 - w, x0))
    tx = int(min(max(tipx - x0, 60), w - 60))
    col = WHITE if a['spk'] == 'mari' else (240, 235, 226)
    pad = 12
    im = Image.new('RGBA', (w + 2 * pad, h + 60 + pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((pad, pad, pad + w, pad + h), radius=32, fill=col, outline=OL, width=6)
    d.polygon([(pad + tx - 20, pad + h - 3), (pad + tx + 20, pad + h - 3), (pad + tx, pad + h + 38)], fill=col, outline=OL)
    d.rectangle((pad + tx - 16, pad + h - 6, pad + tx + 16, pad + h - 1), fill=col)
    _bub[key] = dict(im=im, lines=lines, w=w, h=h, tx=tx, pad=pad)
    return _bub[key]

def draw_bubble(img, i, t, tipx, tipy, limit):
    a = AUD[i]
    b = make_bubble(i, tipx)
    st = P[i] - 0.05
    end = min(P[i] + a['d'] + 0.3, limit)
    if t < st or t > end + 0.12:
        return
    alpha = 1.0 - max(0.0, (t - end) / 0.12)
    im = b['im'].copy()
    d = ImageDraw.Draw(im)
    total = sum(len(l) for l in b['lines'])
    prog = (t - P[i]) / max(0.2, a['d'] * 0.92)
    nvis = int(math.ceil(max(0.0, min(1.0, prog)) * total))
    f = font(FB, BS)
    k = 0
    for li, line in enumerate(b['lines']):
        x = b['pad'] + BPAD
        y = b['pad'] + BPAD - 3 + li * BLH + BLH // 2
        for wd in line:
            if k < nvis:
                if emph(wd):
                    wl = f.getlength(wd)
                    d.rounded_rectangle((x - 6, y - 26, x + wl + 4, y + 26), radius=10, fill=GOLDL)
                d.text((x, y), wd, font=f, fill=OL, anchor='lm')
            x += f.getlength(wd + ' ')
            k += 1
    tipx_l = b['pad'] + b['tx']
    tipy_l = b['pad'] + b['h'] + 38
    pp = min(1.0, (t - st) / 0.22)
    if pp <= 0:
        return
    s = 0.55 + 0.45 * eob(pp)
    lw, lh = max(1, int(im.width * s)), max(1, int(im.height * s))
    l2 = im.resize((lw, lh), Image.LANCZOS) if abs(s - 1) > 0.01 else im
    l2 = l2.copy()
    l2.putalpha(l2.getchannel('A').point(lambda v: int(v * min(1.0, pp * 3) * alpha)))
    img.paste(l2, (int(tipx - tipx_l * s), int(tipy - tipy_l * s)), l2)

# ---------------------------------------------------------------- audio-driven state
def active_line(t):
    for i, a in enumerate(AUD):
        if P[i] <= t < P[i] + a['d']:
            return i
    return None

def env_at(i, t):
    env = AUD[i]['env']
    k = max(1, min(len(env) - 2, int((t - P[i]) * FPS)))
    return float(np.mean(env[k - 1:k + 2]))

def lvl_of(e):
    return 0 if e < 0.15 else 1 if e < 0.4 else 2 if e < 0.75 else 3

def cliente_mood(t):
    if t < P[1] + 0.8:
        return 'smug'
    if t < P[6]:
        return 'worry'
    return 'deflated'

def scene_index(t):
    k = 0
    for i in range(N):
        if t >= P[i] - 0.05:
            k = i
    return k

# ---------------------------------------------------------------- frame
FLOOR = 1560
KC = 0.85
MARI_SX, CLI_SX = 250, 830
BASE_C = 1000
STAGE_Y0 = 1000
_bg = None

def bg(t):
    img = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(img)
    for k in range(0, FLOOR, 54):
        y = (k - t * 30) % FLOOR
        d.line((0, y, W, y), fill=LINEC, width=2)
    d.rectangle((0, FLOOR, W, H), fill=WARM)
    for i in range(0, 8):
        y = FLOOR + 14 + i * 46
        d.line((0, y, W, y), fill=(214, 206, 192), width=3)
    d.rectangle((0, FLOOR - 5, W, FLOOR), fill=CHAR)
    return img

def scene_end(t):
    img = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(img)
    for k in range(0, H + 54, 54):
        y = (k - t * 30) % H
        d.line((0, y, W, y), fill=LINEC, width=2)
    p = min(1.0, (t - CEND) / 0.5)
    lg = logo_w(800)
    s = 0.85 + 0.15 * eob(p)
    lay = lg.resize((int(lg.width * s), int(lg.height * s)), Image.LANCZOS)
    paste_center(img, lay, 540, 860, alpha=min(1.0, p * 2))
    put(img, '@mavan.3d', 54, OL, 540, 1180, t, CEND + 0.6, FM)
    return img

def frame(t):
    if t >= CEND:
        img = scene_end(t)
        a = max(0.0, 1 - abs(t - CEND) / 0.08) * 0.9
        return Image.blend(img, Image.new('RGB', (W, H), CREAM), a) if a > 0.01 else img
    img = bg(t)
    i = scene_index(t)
    d = window(img, i, t)
    r = t - P[i]
    Dd = AUD[i]['d']
    SCENES[i](img, d, t, r, Dd)
    # characters
    ai = active_line(t)
    spk = AUD[ai]['spk'] if ai is not None else None
    e = env_at(ai, t) if ai is not None else 0.0
    lvl = lvl_of(e) if ai is not None else 0
    st = Stage(W, H - STAGE_Y0, KC, 0, (FLOOR - STAGE_Y0) - BASE_C * KC)
    draw_mari(st, MARI_SX / KC, BASE_C, t, lvl if spk == 'mari' else 0, e if spk == 'mari' else 0.0,
              (t % 2.6) < 0.12, spk == 'mari', i in (2, 3, 4, 5))
    draw_cliente(st, CLI_SX / KC, BASE_C, t, lvl if spk == 'cliente' else 0, e if spk == 'cliente' else 0.0,
                 ((t + 1.1) % 3.1) < 0.12, spk == 'cliente', cliente_mood(t))
    small = st.im.resize((W, H - STAGE_Y0), Image.LANCZOS)
    img.paste(small, (0, STAGE_Y0), small)
    logo_bug(img, 540, 285, 230)
    # bubble
    tip_y = FLOOR - 478 * KC - 66 * KC - 22
    for j in range(N):
        tipx = MARI_SX if AUD[j]['spk'] == 'mari' else CLI_SX
        lim = P[j + 1] - 0.05 if j + 1 < N else CEND
        draw_bubble(img, j, t, tipx, tip_y, lim)
    # CTA after the last line
    t_end = P[-1] + AUD[-1]['d'] + 0.15
    if t >= t_end:
        sw = t_end + 1.0
        if t < sw:
            paste_pop(img, pill('COMENTA O NÚMERO', 50, WHITE, CHAR), 540, 960, (t - t_end) / 0.28)
        else:
            paste_pop(img, pill('MANDA PRA QUEM MONTA A ÁRVORE', 34, WHITE, CHAR, 'send'), 540, 960, (t - sw) / 0.28)
    # quick cream flash over the window at every step change
    for j in range(1, N):
        c = P[j] - 0.05
        a = max(0.0, 1 - abs(t - c) / 0.08) * 0.9
        if a > 0.01:
            box = (SX0 - 6, SY0 - 6, SX1 + 16, SY1 + 18)
            reg = img.crop(box)
            reg = Image.blend(reg, Image.new('RGB', reg.size, CREAM), a)
            img.paste(reg, box[:2])
    return img

# ---------------------------------------------------------------- run
def preview():
    moments = [P[i] + AUD[i]['d'] * f for i in range(8) for f in (0.9,)] + [P[2] + AUD[2]['d'] * 0.5, P[4] + AUD[4]['d'] * 0.9, P[5] + AUD[5]['d'] * 0.95, CEND - 0.5, CEND + 0.9]
    n = len(moments)
    cols = 5
    rows = (n + cols - 1) // cols
    sheet = Image.new('RGB', (360 * cols, 640 * rows))
    for k, t in enumerate(moments):
        im = frame(t)
        im.save(f'{OUT}/prev{k + 1:02d}.png')
        sheet.paste(im.resize((360, 640), Image.LANCZOS), (360 * (k % cols), 640 * (k // cols)))
    sheet.save(f'{OUT}/sheet.png')
    print('P', [round(float(x), 2) for x in P], 'CEND', round(float(CEND), 2), 'TOTAL', round(float(TOTAL), 2))

def render():
    tmp = f'{OUT}/video.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '18',
                          '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    n = int(round(TOTAL * FPS))
    for k in range(n):
        p.stdin.write(frame(k / FPS).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        sys.exit('ffmpeg video failed')
    os.rename(tmp, f'{OUT}/video.mp4')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error']
    for a in AUD:
        cmd += ['-i', a['file']]
    cmd += ['-i', f'{OUT}/video.mp4']
    fc = []
    for k, a in enumerate(AUD):
        ms = int(P[k] * 1000)
        fc.append(f"[{k}:a]atrim=start={a['s']:.3f}:end={a['e']:.3f},asetpts=PTS-STARTPTS,"
                  f"aformat=sample_rates=44100:channel_layouts=mono,adelay={ms}:all=1[a{k}]")
    mix = ''.join(f'[a{k}]' for k in range(N))
    fc.append(f"{mix}amix=inputs={N}:normalize=0:duration=longest,apad,atrim=0:{TOTAL:.3f},"
              f"loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
    final = f'{OUT}/mavan_natal_enfeites.mp4'
    cmd += ['-filter_complex', ';'.join(fc), '-map', f'{N}:v', '-map', '[aout]',
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', f'{TOTAL:.3f}', final + '.tmp.mp4']
    subprocess.check_call(cmd)
    os.rename(final + '.tmp.mp4', final)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':
        preview()
    elif len(sys.argv) > 1 and sys.argv[1] == 'render':
        render()
