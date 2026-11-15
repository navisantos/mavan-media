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
OUT = D + '/out11'
os.makedirs(OUT, exist_ok=True)
AF = D + '/aud11/fin/'

LINES = [
    ('01.wav', 'cliente', 'Brinde de fim de ano pra equipe e pros clientes? Dezembro eu vejo isso.'),
    ('02.wav', 'mari', 'Dezembro é tarde, e brinde bom não é caneca igual a de todo mundo. Olha alguns exemplos.'),
    ('03.wav', 'mari', 'Um: enfeite de Natal com o nome da sua empresa e o ano gravado. O cliente pendura na árvore e lembra de você todo Natal.'),
    ('04.wav', 'cliente', 'Legal. Mas eu queria algo mais pessoal.'),
    ('05.wav', 'mari', 'Dois: a etiqueta de presente com o nome de cada cliente. Depois do Natal, ela vira enfeite.'),
    ('06.wav', 'mari', 'Três: enfeite com espaço pra foto da equipe. Quatro: o kit para pintar, com tinta, pra equipe pintar junto.'),
    ('07.wav', 'cliente', 'E se eu precisar de bastante?'),
    ('08.wav', 'mari', 'Quantidade também leva cerca de uma semana. Quem pede cedo escolhe com calma.'),
    ('09.wav', 'cliente', 'Tá. Deixar pra dezembro foi mesmo o erro.'),
    ('10.wav', 'mari', 'Manda esse vídeo pra quem cuida dos brindes da sua empresa. Ou manda um direct pra Mavan que te ajudamos! Já escolhe o seu.'),
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
TITLES = ['BRINDE DE FIM DE ANO', 'NÃO É CANECA IGUAL', '1 · NOME DA EMPRESA + ANO', 'MAIS PESSOAL?', '2 · ETIQUETA QUE VIRA ENFEITE', '3 · FOTO DA EQUIPE · 4 · KIT', 'E EM QUANTIDADE?', 'CERCA DE 1 SEMANA', 'O ERRO: DEIXAR PRA DEZEMBRO', 'MANDA E ESCOLHE O SEU']
def window(img, i, t):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((SX0 + 10, SY0 + 12, SX1 + 10, SY1 + 12), radius=28, fill=(214, 206, 192))
    rr(d, (SX0, SY0, SX1, SY1), 28, (253, 251, 247), OL, 5)
    d.rounded_rectangle((SX0, SY0, SX1, SY0 + TB), radius=28, fill=CHAR)
    d.rectangle((SX0, SY0 + 30, SX1, SY0 + TB), fill=CHAR)
    d.rectangle((SX0 + 2, SY0 + TB - 1, SX1 - 2, SY0 + TB + 1), fill=CHAR)
    for k, col in enumerate((GOLD, GOLDL, WHITE)):
        d.ellipse((SX0 + 28 + k * 30 - 9, SY0 + 27 - 9, SX0 + 28 + k * 30 + 9, SY0 + 27 + 9), fill=col)
    col = GOLD if i in (0, N - 1) else WHITE
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

def mug(d, cx, cy, w, h, col, ol=OL):
    d.arc((cx + w / 2 - w * 0.18, cy - h * 0.28, cx + w / 2 + w * 0.36, cy + h * 0.22), -90, 90, fill=ol, width=9)
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=int(w * 0.14), fill=col, outline=ol, width=4)
    d.arc((cx - w * 0.3, cy - h * 0.32, cx - w * 0.1, cy - h * 0.1), 200, 275, fill=WHITE, width=4)

def person(d, cx, cy, s=1.0):
    d.rounded_rectangle((cx - 44 * s, cy + 18 * s, cx + 44 * s, cy + 125 * s), radius=int(24 * s), fill=(76, 106, 154), outline=OL, width=4)
    d.ellipse((cx - 32 * s, cy - 50 * s, cx + 32 * s, cy + 14 * s), fill=(246, 208, 178), outline=OL, width=4)

def band(d, cx, cy, txt, w=100, size=28):
    d.rounded_rectangle((cx - w, cy, cx + w, cy + 46), radius=14, fill=CHAR, outline=OL, width=3)
    T(d, cx, cy + 24, txt, size, GOLDL, 'mm')

PALE = (244, 240, 232)

def calendar(d, x0, y0, x1, y1, lab=None):
    d.rounded_rectangle((x0, y0, x1, y1), radius=22, fill=PAPER, outline=OL, width=5)
    d.rounded_rectangle((x0, y0, x1, y0 + 62), radius=22, fill=RED, outline=OL, width=5)
    d.rectangle((x0 + 3, y0 + 36, x1 - 3, y0 + 62), fill=RED)
    for xx in (x0 + 90, x1 - 90):
        d.rounded_rectangle((xx - 8, y0 - 20, xx + 8, y0 + 28), radius=6, fill=GRAY, outline=OL, width=3)
    if lab:
        T(d, (x0 + x1) // 2, y0 + 31, lab, 34, WHITE, 'mm')

def zoom(r, Dd, a=0.82, b=1.0):
    return a + (b - a) * clamp(r / max(0.5, Dd))

def sc_dez(img, d, t, r, Dd):
    s = pop(r, 0.1)
    if s > 0.05:
        calendar(d, 340, Y(45), 740, Y(340), 'DEZEMBRO')
        T(d, 540, Y(205), '?', int(150 * s), GRAY, 'mm')
        T(d, 540, Y(365), 'BRINDE DE FIM DE ANO', 26, GRAY, 'mm') if r > 1.5 else None

def sc_canecas(img, d, t, r, Dd):
    for k in range(4):
        s = pop(r, 0.1 + k * 0.12)
        if s > 0.03:
            mug(d, 205 + k * 177, Y(150), int(105 * s), int(95 * s), (228, 222, 210))
    if r > 1.2:
        u = sm((r - 1.2) / 0.5)
        for k in range(4):
            x = 205 + k * 177
            d.line((x - 28 * u, Y(150) - 28 * u, x + 28 * u, Y(150) + 28 * u), fill=RED, width=9)
            d.line((x + 28 * u, Y(150) - 28 * u, x - 28 * u, Y(150) + 28 * u), fill=RED, width=9)
    if r > 2.0:
        T(d, 540, Y(300), 'IGUAL A TODO MUNDO', 32, GRAY, 'mm')

def sc_ex1(img, d, t, r, Dd):
    z = zoom(r, Dd, 0.75, 1.0) * pop(r, 0.1)
    R = int(150 * z)
    cx, cy = 540, Y(195)
    ornament(d, cx, cy, R, RED)
    d.arc((cx - R * 0.8, cy - R * 0.55, cx + R * 0.8, cy + R * 0.9), 20, 160, fill=WHITE, width=5)
    if pop(r, 0.6) > 0.8:
        band(d, cx, cy - 10, typed('SUA EMPRESA', r, 0.7, 1.9), 150, 30)
        T(d, cx, cy + 62, typed('2026', r, 1.9, 2.5), 34, WHITE, 'mm')
    if r > Dd * 0.62:
        tree(d, 880, Y(150), Y(300), 80)
        s2 = pop(r, Dd * 0.62)
        ornament(d, 880, Y(235), int(14 * s2), RED, ring=False, hl=False)
    foot(d, 'exemplo ilustrativo')

def sc_pers(img, d, t, r, Dd):
    s = pop(r, 0.1)
    person(d, 540, Y(165), s)
    if r > 0.6:
        draw_icon(d, 'heart', 740, Y(110), int(40 * pop(r, 0.6)))

def tag(d, cx, cy, s, txt):
    w, h = 170 * s, 100 * s
    d.polygon([(cx - w / 2 + 30 * s, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2 + 30 * s, cy + h / 2), (cx - w / 2, cy)], fill=PAPER, outline=OL)
    d.ellipse((cx - w / 2 + 22 * s, cy - 9 * s, cx - w / 2 + 40 * s, cy + 9 * s), fill=CREAM, outline=OL, width=3)
    d.line((cx - w / 2 + 31 * s, cy, cx - w / 2 - 50 * s, cy - 50 * s), fill=GOLD, width=5)
    T(d, cx + 14 * s, cy, txt, max(8, int(30 * s)), OL, 'mm')

def sc_ex2(img, d, t, r, Dd):
    s = pop(r, 0.1) * zoom(r, Dd * 0.5, 0.75, 1.0)
    if r < Dd * 0.5:
        tag(d, 540, Y(190), 2.1 * s, typed('MARIA', r, 0.5, 1.4))
        T(d, 540, Y(350), 'ETIQUETA COM O NOME', 28, GRAY, 'mm') if r > 1.6 else None
    else:
        u = pop(r, Dd * 0.5)
        tree(d, 540, Y(60), Y(335), 200)
        d.line((540, Y(150), 540, Y(180)), fill=GOLD, width=5)
        tag(d, 540, Y(215), 0.9 * u + 0.1, 'MARIA')
        T(d, 160, Y(200), 'VIRA', 30, GRAY, 'lm')
        T(d, 160, Y(240), 'ENFEITE', 30, GRAY, 'lm')
    foot(d, 'exemplo ilustrativo')

def sc_ex34(img, d, t, r, Dd):
    if r < Dd * 0.5:
        z = pop(r, 0.1) * zoom(r, Dd * 0.5, 0.78, 1.0)
        R = int(150 * z)
        cx, cy = 540, Y(195)
        ornament(d, cx, cy, R, BLUE)
        fr = int(R * 0.55)
        rr(d, (cx - fr, cy - fr * 0.9, cx + fr, cy + fr * 0.9), 14, PAPER, OL, 4)
        if pop(r, 0.9) > 0.5:
            family(d, cx, cy - 4, 0.85)
        T(d, 540, Y(372), 'ESPAÇO PARA A FOTO DA EQUIPE', 26, GRAY, 'mm') if r > 1.5 else None
    else:
        u = pop(r, Dd * 0.5)
        z = u * zoom(r - Dd * 0.5, Dd * 0.5, 0.78, 1.0)
        ornament(d, 400, Y(180), int(135 * z), PALE)
        for k, c in enumerate((RED, GOLD, GREEN, BLUE)):
            if r > Dd * 0.6 + k * 0.3:
                x = 650 + (k % 2) * 90
                y = Y(210) + (k // 2) * 80 - 30
                d.rounded_rectangle((x - 30, y - 24, x + 30, y + 26), radius=10, fill=WHITE, outline=OL, width=4)
                d.rectangle((x - 30, y - 24, x + 30, y - 4), fill=c)
        brush(d, 800, Y(100), -50, 1.0)
        T(d, 540, Y(372), 'KIT PARA PINTAR, COM TINTA', 26, GRAY, 'mm') if r > Dd * 0.75 else None
    foot(d, 'exemplo ilustrativo')

def brush(d, x, y, ang=-40, s=1.0, col=RED):
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    x1, y1 = x + dx * 120 * s, y + dy * 120 * s
    d.line((x, y, x1, y1), fill=OL, width=int(16 * s))
    d.line((x, y, x1, y1), fill=(196, 150, 96), width=int(9 * s))
    xt, yt = x - dx * 30 * s, y - dy * 30 * s
    d.polygon([(x + dy * 12 * s, y - dx * 12 * s), (x - dy * 12 * s, y + dx * 12 * s), (xt, yt)], fill=col, outline=OL)

def sc_many(img, d, t, r, Dd):
    cols = [RED, BLUE, GOLD, GREEN, (240, 235, 226)]
    k = 0
    for row in range(2):
        for col in range(5):
            s = pop(r, 0.05 + k * 0.05)
            if s > 0.03:
                ornament(d, 170 + col * 175, Y(120 + row * 130), int(48 * s), cols[(col + row) % 5], ring=False, hl=False)
            k += 1
    if r > 0.9:
        T(d, 540, Y(350), 'EM QUANTIDADE', 32, GRAY, 'mm')

def sc_week(img, d, t, r, Dd):
    calendar(d, 200, Y(45), 880, Y(335))
    for k in range(7):
        x = 245 + k * 88
        u = clamp((r - Dd * (0.15 + 0.08 * k)) / 0.25)
        d.rounded_rectangle((x, Y(140), x + 70, Y(215)), radius=12, fill=tuple(int(255 + (c - 255) * u) for c in GOLD), outline=OL, width=3)
        T(d, x + 35, Y(178), str(k + 1), 32, OL, 'mm')
    if r > Dd * 0.2:
        T(d, 540, Y(270), 'CERCA DE 1 SEMANA', 36, OL, 'mm')
    if r > Dd * 0.7:
        s2 = pop(r, Dd * 0.7)
        T(d, 540, Y(372), 'PEÇA CEDO', int(30 * s2), GRAY, 'mm')

def sc_erro(img, d, t, r, Dd):
    s = pop(r, 0.1)
    if s > 0.05:
        calendar(d, 340, Y(45), 740, Y(340), 'DEZEMBRO')
    if r > 0.8:
        u = sm((r - 0.8) / 0.4)
        d.line((380, Y(110), 380 + 320 * u, Y(110) + 200 * u), fill=RED, width=14)
        d.line((700, Y(110), 700 - 320 * u, Y(110) + 200 * u), fill=RED, width=14)

def sc_send(img, d, t, r, Dd):
    tree(d, 540, Y(70), Y(335), 200)
    spots = [(480, Y(190), RED), (610, Y(235), BLUE), (470, Y(290), GOLD), (625, Y(305), (240, 235, 226))]
    for k, (x, y, c) in enumerate(spots):
        s = pop(r, 0.1 + k * 0.15)
        if s > 0.02:
            ornament(d, x, y, int(26 * s), c, ring=False, hl=False)
    T(d, 120, Y(190), 'ESCOLHE', 30, GRAY, 'lm')
    T(d, 120, Y(230), 'O SEU', 30, GRAY, 'lm')
    draw_icon(d, 'heart', 840, Y(170), int(36 * pop(r, 0.6)))

SCENES = [sc_dez, sc_canecas, sc_ex1, sc_pers, sc_ex2, sc_ex34, sc_many, sc_week, sc_erro, sc_send]

# ---------------------------------------------------------------- bubbles
BS, BLH, BPAD, BMAXW = 34, 46, 26, 860
EMPH = {'dezembro', 'manda', 'semana', 'brindes', 'ano', 'nome', 'cedo', 'kit', 'caneca', 'direct', 'tinta', 'foto', 'etiqueta'}
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
    if t < P[3]:
        return 'smug'
    if t < P[8]:
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
              (t % 2.6) < 0.12, spk == 'mari', i in (2, 4, 5))
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
            paste_pop(img, pill('MANDA UM DIRECT PRA MAVAN', 34, WHITE, CHAR, 'send'), 540, 960, (t - t_end) / 0.28)
        else:
            paste_pop(img, pill('MANDA PRA QUEM CUIDA DOS BRINDES', 28, WHITE, CHAR, 'send'), 540, 960, (t - sw) / 0.28)
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
    moments = [P[i] + AUD[i]['d'] * f for i in range(N) for f in (0.9,)] + [P[3] + AUD[3]['d'] * 0.5, P[5] + AUD[5]['d'] * 0.5, CEND - 0.5, CEND + 0.9]
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
    final = f'{OUT}/mavan_brindes.mp4'
    cmd += ['-filter_complex', ';'.join(fc), '-map', f'{N}:v', '-map', '[aout]',
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', f'{TOTAL:.3f}', final + '.tmp.mp4']
    subprocess.check_call(cmd)
    os.rename(final + '.tmp.mp4', final)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':
        preview()
    elif len(sys.argv) > 1 and sys.argv[1] == 'render':
        render()
