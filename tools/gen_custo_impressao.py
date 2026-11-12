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
OUT = D + '/out7'
os.makedirs(OUT, exist_ok=True)
AF = D + '/aud7/fin/'

LINES = [
    ('01.wav', 'cliente', 'Isso é só um pedaço de plástico. Por que cobra tanto?'),
    ('02.wav', 'mari', 'Beleza, vamos fazer a conta. Um enfeite de 50 gramas. O quilo do filamento custa 100 reais: são 5 reais.'),
    ('03.wav', 'mari', 'Energia: 3 horas de impressão, uns 30 centavos.'),
    ('04.wav', 'mari', 'Só que 1 em cada 5 impressões falha. O que deu errado vai pro lixo, e o custo sobe pra uns 6 reais e 60.'),
    ('05.wav', 'mari', 'E isso é só o plástico. Ainda tem o projeto, a personalização, a pintura, a embalagem e o meu tempo.'),
    ('06.wav', 'cliente', 'Tá… então o plástico é a parte barata.'),
    ('07.wav', 'mari', 'Comenta “EU” se você também achava que era só plástico, e manda pra quem pede desconto.'),
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

TITLES = ['SÓ UM PEDAÇO DE PLÁSTICO?', '1 · FILAMENTO', '2 · ENERGIA', '3 · FALHAS (1 EM CADA 5)',
          'E O RESTO?', 'O PLÁSTICO É A PARTE BARATA', 'COMENTA “EU”']

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

# ---------------------------------------------------------------- custo scenes
def spool(d, cx, cy, R, col=GREEN):
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=col, outline=OL, width=5)
    d.ellipse((cx - R * 0.62, cy - R * 0.62, cx + R * 0.62, cy + R * 0.62), outline=OL, width=3)
    d.ellipse((cx - R * 0.3, cy - R * 0.3, cx + R * 0.3, cy + R * 0.3), fill=CREAM, outline=OL, width=4)
    d.line((cx + R * 0.7, cy + R * 0.7, cx + R * 1.2, cy + R * 0.95), fill=col, width=6)

def bolt(d, cx, cy, s, col=GOLD):
    pts = [(0, -1), (-0.55, 0.1), (-0.05, 0.1), (-0.3, 1), (0.6, -0.2), (0.05, -0.2), (0.3, -1)]
    d.polygon([(cx + x * s, cy + y * s) for x, y in pts], fill=col, outline=OL)

def sc_plastic(img, d, t, r, Dd):
    s = pop(r, 0.1)
    spool(d, 330, Y(205), int(110 * s))
    if r > 0.5:
        s2 = pop(r, 0.5)
        ornament(d, 700, Y(215), int(88 * s2), (236, 232, 224), hl=False)
    if r > Dd * 0.45:
        for k, (x, y) in enumerate([(540, Y(110)), (580, Y(70)), (500, Y(60))]):
            T(d, x + (k - 1) * 40, y - 5, '?', 56, RED, 'mm')
    T(d, 540, Y(365), 'SÓ PLÁSTICO?', 38, GRAY, 'mm')

def sc_fil(img, d, t, r, Dd):
    s = pop(r, 0.1)
    spool(d, 215, Y(190), int(95 * s))
    T(d, 215, Y(325), '50 g', 38, OL, 'mm') if r > 0.5 else None
    if r > Dd * 0.28:
        T(d, 540, Y(140), '×', 56, GRAY, 'mm')
        d.rounded_rectangle((590, Y(95), 910, Y(185)), radius=16, fill=PAPER, outline=OL, width=4)
        T(d, 750, Y(140), 'R$ 100 / kg', 38, OL, 'mm')
    if r > Dd * 0.6:
        u = pop(r, Dd * 0.6)
        T(d, 640, Y(290), '= R$ 5,00', int(78 * u), RED, 'mm')

def sc_energy(img, d, t, r, Dd):
    s = pop(r, 0.1)
    bolt(d, 230, Y(190), int(110 * s))
    if r > Dd * 0.2:
        d.rounded_rectangle((400, Y(95), 910, Y(185)), radius=16, fill=PAPER, outline=OL, width=4)
        T(d, 655, Y(140), '3 h de impressão', 38, OL, 'mm')
    if r > Dd * 0.55:
        u = pop(r, Dd * 0.55)
        T(d, 655, Y(290), '≈ R$ 0,30', int(78 * u), RED, 'mm')

def sc_fail(img, d, t, r, Dd):
    for k in range(5):
        x = 170 + k * 175
        s = pop(r, 0.05 + k * 0.1)
        ornament(d, x, Y(120), int(46 * s), GOLD if k < 4 else (205, 200, 192), ring=False, hl=False)
    if r > Dd * 0.4:
        u = sm((r - Dd * 0.4) / 0.3)
        x = 170 + 4 * 175
        d.line((x - 45, Y(75), x - 45 + 90 * u, Y(75) + 90 * u), fill=RED, width=10)
        d.line((x + 45, Y(75), x + 45 - 90 * u, Y(75) + 90 * u), fill=RED, width=10)
        T(d, x, Y(210), 'FALHOU', 26, RED, 'mm')
    T(d, 360, Y(210), '4 deram certo', 26, GRAY, 'mm') if r > Dd * 0.3 else None
    v = 5.30 + 1.30 * clamp((r - Dd * 0.55) / (Dd * 0.3))
    if r > Dd * 0.2:
        T(d, 540, Y(300), 'R$ ' + ('%.2f' % v).replace('.', ','), 86, RED if v > 6.5 else OL, 'mm')
    T(d, 540, Y(358), 'por peça boa', 26, GRAY, 'mm')

def sc_rest(img, d, t, r, Dd):
    items = ['PROJETO', 'PERSONALIZAÇÃO', 'PINTURA', 'EMBALAGEM', 'MEU TEMPO']
    for k, it in enumerate(items):
        s = pop(r, 0.15 + k * Dd * 0.14)
        if s < 0.05:
            continue
        w = 360
        x = 200 if k % 2 == 0 else 560
        y = Y(40 + (k // 2) * 105) if k < 4 else Y(250)
        if k == 4:
            x = 380
        d.rounded_rectangle((x, y, x + w * s, y + 80 * s), radius=18, fill=PAPER, outline=OL, width=4)
        if s > 0.8:
            T(d, x + w / 2, y + 40, it, 28, OL, 'mm')
    if r > Dd * 0.8:
        T(d, 540, Y(352), 'E NADA DISSO ENTROU NA CONTA', 28, RED, 'mm')

def sc_cheap(img, d, t, r, Dd):
    u = sm(r / 0.6)
    base = Y(350)
    h1 = 50 * u
    d.rectangle((250, base - h1, 450, base), fill=GREEN, outline=OL, width=4)
    h2 = 280 * clamp((r - 0.4) / 0.7)
    d.rectangle((590, base - h2, 790, base), fill=GOLD, outline=OL, width=4)
    T(d, 350, base + 25, 'PLÁSTICO', 28, OL, 'mm')
    T(d, 690, base + 25, 'O RESTO', 28, OL, 'mm')
    if r > 0.8:
        T(d, 350, base - h1 - 28, 'R$ 6,60', 34, OL, 'mm')
    if r > 1.3:
        T(d, 690, base - h2 + 120, '?', 90, OL, 'mm')

def sc_eu(img, d, t, r, Dd):
    s = pop(r, 0.1)
    R = int(110 * s)
    d.ellipse((540 - R, Y(170) - R, 540 + R, Y(170) + R), fill=GOLD, outline=OL, width=6)
    if R > 60:
        T(d, 540, Y(170), 'EU', int(R * 0.9), OL, 'mm')
    if r > Dd * 0.55:
        T(d, 540, Y(335), 'MANDA PRA QUEM PEDE DESCONTO', 28, GRAY, 'mm')

SCENES = [sc_plastic, sc_fil, sc_energy, sc_fail, sc_rest, sc_cheap, sc_eu]

# ---------------------------------------------------------------- bubbles
BS, BLH, BPAD, BMAXW = 36, 48, 26, 860
EMPH = {'plástico', 'conta', '50', '100', '5', '30', '1', '60', 'falha', 'energia', 'projeto', 'personalização', 'pintura', 'embalagem', 'tempo', 'barata', 'eu', 'desconto', 'filamento'}
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
    if t < P[5]:
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
              (t % 2.6) < 0.12, spk == 'mari', i in (1, 2, 3, 4))
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
            paste_pop(img, pill('COMENTA “EU”', 54, WHITE, CHAR), 540, 960, (t - t_end) / 0.28)
        else:
            paste_pop(img, pill('MANDA PRA QUEM PEDE DESCONTO', 34, WHITE, CHAR, 'send'), 540, 960, (t - sw) / 0.28)
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
    moments = [P[i] + AUD[i]['d'] * 0.9 for i in range(7)] + [P[1] + AUD[1]['d'] * 0.5, P[3] + AUD[3]['d'] * 0.4, CEND - 0.5, CEND + 0.9]
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
    final = f'{OUT}/mavan_custo_impressao.mp4'
    cmd += ['-filter_complex', ';'.join(fc), '-map', f'{N}:v', '-map', '[aout]',
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', f'{TOTAL:.3f}', final + '.tmp.mp4']
    subprocess.check_call(cmd)
    os.rename(final + '.tmp.mp4', final)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':
        preview()
    elif len(sys.argv) > 1 and sys.argv[1] == 'render':
        render()
