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
OUT = D + '/out16'
os.makedirs(OUT, exist_ok=True)
AF = D + '/aud16/fin/'

LINES = [
    ('01.wav', 'cliente', 'Suporte é tudo igual. Ligo o automático e deixo imprimir.'),
    ('02.wav', 'mari', 'Igual nada. O suporte comum enche a peça de coluna, e tudo isso vira lixo no final.'),
    ('03.wav', 'cliente', 'Mas é só um pouquinho de filamento.'),
    ('04.wav', 'mari', 'Em peça grande não é pouquinho. E ainda deixa marca onde encosta, então o acabamento sofre.'),
    ('05.wav', 'cliente', 'E tem outro jeito?'),
    ('06.wav', 'mari', 'Tem. O suporte em árvore. Em vez de uma parede cheia, ele faz galhos que só tocam onde precisa.'),
    ('07.wav', 'mari', 'Gasta menos filamento e sai mais fácil de tirar.'),
    ('08.wav', 'cliente', 'Então é só ligar e pronto?'),
    ('09.wav', 'mari', 'Quase. Em peça com muito detalhe ou base pequena, vale conferir no preview antes de fatiar.'),
    ('10.wav', 'cliente', 'Tá. Vou testar na minha próxima peça.'),
    ('11.wav', 'mari', 'Testa e me conta nos comentários: qual peça sua gasta mais suporte? E marca quem usa suporte comum em tudo.'),
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
TITLES = ['SUPORTE É TUDO IGUAL?', 'SUPORTE COMUM: MUITA COLUNA', 'É SÓ UM POUQUINHO?', 'PEÇA GRANDE E ACABAMENTO', 'TEM OUTRO JEITO?', 'SUPORTE EM ÁRVORE', 'GASTA MENOS · SAI FÁCIL', 'É SÓ LIGAR?', 'CONFERE NO PREVIEW', 'TESTAR NA PRÓXIMA PEÇA', 'COMENTA E MARCA']
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

def bed(d, x0, x1, yb, col=(206, 200, 190)):
    d.polygon([(x0, yb), (x1, yb), (x1, yb + 24), (x0, yb + 24)], fill=col, outline=OL)

def nozzle(d, x, y, s=1.0):
    d.rounded_rectangle((x - 40 * s, y - 120 * s, x + 40 * s, y - 56 * s), radius=int(10 * s), fill=CHAR, outline=OL, width=3)
    d.polygon([(x - 28 * s, y - 56 * s), (x + 28 * s, y - 56 * s), (x + 6 * s, y), (x - 6 * s, y)], fill=GOLD, outline=OL)

def slab(d, yb, lift, x0=300, x1=780, h=60):
    d.polygon([(x0, yb), (x1, yb), (x1, yb - h), (x0 + 0, yb - h - lift)], fill=GOLD, outline=OL) if False else None
    d.polygon([(x0, yb - lift), (x0 + 60, yb - lift - h), (x1, yb - h), (x1, yb)], fill=GOLD, outline=OL)
    d.line((x0, yb - lift, x0 + 40, yb), fill=OL, width=3)

def magnifier(d, cx, cy, R):
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=RED, width=7)
    d.line((cx + R * 0.7, cy + R * 0.7, cx + R * 1.5, cy + R * 1.5), fill=RED, width=10)

def sc_pasta(img, d, t, r, Dd):
    yb = Y(300)
    bed(d, 150, 930, yb)
    nozzle(d, 540, Y(135))
    n = int(120 * clamp(r / 2.5))
    pts = []
    for k in range(n):
        a = k * 0.5
        pts.append((540 + (60 + k * 1.6) * math.cos(a) * 1.8 * 0.55 + 90 * math.sin(k * 0.13), yb - 10 - (k % 40) * 3.4 - 10 * math.sin(a)))
    if len(pts) > 1:
        d.line(pts, fill=GOLD, width=7, joint='curve')
    if r > 2.2:
        T(d, 540, Y(372), 'ACORDEI COM MACARRÃO DE FILAMENTO', 24, RED, 'mm')

def sc_three(img, d, t, r, Dd):
    if r > 0.3:
        T(d, 540, Y(55), 'FALHAS AVISAM CEDO', 30, GRAY, 'mm')
    for k in range(3):
        s = pop(r, 2.0 + k * 0.7)
        if s > 0.03:
            R = int(62 * s)
            x = 250 + k * 290
            d.ellipse((x - R, Y(205) - R, x + R, Y(205) + R), fill=GOLD, outline=OL, width=5)
            if s > 0.7:
                num(d, x, Y(207), k + 1, 54, OL)
    if r > 4.2:
        T(d, 540, Y(340), 'NOS PRIMEIROS MINUTOS', 32, OL, 'mm')

def sc_corner(img, d, t, r, Dd):
    yb = Y(300)
    bed(d, 150, 930, yb)
    lift = 22 * sm(r / 1.5)
    slab(d, yb, lift)
    nozzle(d, 560, Y(150))
    if r > 0.9:
        s = pop(r, 0.9)
        magnifier(d, 300, yb - 14, int(60 * s))
    if r > Dd * 0.55:
        T(d, 540, Y(372), 'A PONTA JÁ SOLTA DA MESA', 28, RED, 'mm')

def sc_small(img, d, t, r, Dd):
    yb = Y(300)
    bed(d, 150, 930, yb)
    slab(d, yb, 22)
    nozzle(d, 560, Y(150))
    s = pop(r, 0.2)
    magnifier(d, 300, yb - 14, 60)
    T(d, 760, Y(90), '?', max(1, int(110 * s)), GRAY, 'mm')

def sc_lines(img, d, t, r, Dd):
    yb = Y(300)
    if r < Dd * 0.38:
        bed(d, 150, 930, yb)
        lift = 22 + 70 * sm(r / 1.8)
        slab(d, yb, lift)
        nozzle(d, 560, Y(150))
        T(d, 540, Y(372), 'UM CANTINHO VIRA PEÇA SOLTA', 28, RED, 'mm')
    else:
        u = pop(r, Dd * 0.38)
        rr(d, (200, Y(60), 880, Y(320)), 18, PAPER, OL, 4)
        for k in range(7):
            y = Y(90 + k * 32)
            if k in (2, 4):
                d.line((230, y, 420, y), fill=GOLD, width=14)
                d.line((560, y, 850, y), fill=GOLD, width=14)
                d.rectangle((420, y - 12, 560, y + 12), fill=(255, 235, 235))
                if u > 0.8:
                    T(d, 490, y, '?', 24, RED, 'mm')
            elif k == 5:
                d.line((230, y, 850, y), fill=GOLD, width=5)
            else:
                d.line((230, y, 850, y), fill=GOLD, width=14)
        T(d, 540, Y(360), 'ESPAÇO ENTRE AS LINHAS · FIO FINO', 26, RED, 'mm') if r > Dd * 0.55 else None

def sc_drag(img, d, t, r, Dd):
    yb = Y(300)
    bed(d, 150, 930, yb)
    nozzle(d, 560, Y(175))
    u = clamp(r / 2.0)
    d.ellipse((560 - 34 * u, Y(175) - 8, 560 + 34 * u, Y(175) + 40 * u), fill=GOLD, outline=OL, width=3)
    pts = [(560 - 20 + k * 9 + 24 * math.sin(k * 0.9 + r * 3), Y(175) + 40 + 28 * (k % 5) * 0.3 + k * 2.5) for k in range(22)]
    d.line(pts, fill=GOLD, width=8, joint='curve')
    T(d, 760, Y(110), 'BOLINHA', 28, RED, 'lm') if r > 1.5 else None
    T(d, 540, Y(372), 'ELE NÃO ESTÁ GRUDANDO', 28, GRAY, 'mm') if r > Dd * 0.7 else None

def sc_what(img, d, t, r, Dd):
    s = pop(r, 0.1)
    yb = Y(300)
    bed(d, 250, 830, yb)
    nozzle(d, 540, Y(190), 0.9)
    T(d, 720, Y(170), '?', max(1, int(120 * s)), GRAY, 'mm')

def sc_steps(img, d, t, r, Dd):
    labs = ['PARA', 'LIMPA', 'AJUSTA', 'RECOMEÇA']
    for k, lab in enumerate(labs):
        s = pop(r, 0.1 + k * (Dd * 0.2), 0.3)
        if s > 0.03:
            x = 190 + k * 233
            R = int(70 * s)
            d.ellipse((x - R, Y(170) - R, x + R, Y(170) + R), fill=GOLD, outline=OL, width=5)
            if s > 0.8:
                if k == 0:
                    d.rectangle((x - 26, Y(170) - 28, x - 8, Y(170) + 28), fill=OL)
                    d.rectangle((x + 8, Y(170) - 28, x + 26, Y(170) + 28), fill=OL)
                elif k == 1:
                    d.rounded_rectangle((x - 34, Y(170) - 22, x + 34, Y(170) + 22), radius=10, fill=WHITE, outline=OL, width=4)
                elif k == 2:
                    d.ellipse((x - 26, Y(170) - 26, x + 26, Y(170) + 26), outline=OL, width=8)
                    d.ellipse((x - 8, Y(170) - 8, x + 8, Y(170) + 8), fill=OL)
                else:
                    d.arc((x - 30, Y(170) - 30, x + 30, Y(170) + 30), 40, 330, fill=OL, width=8)
                    d.polygon([(x + 24, Y(170) - 30), (x + 40, Y(170) - 6), (x + 14, Y(170) - 8)], fill=OL)
                T(d, x, Y(285), lab, 28, OL, 'mm')
    if r > Dd * 0.82:
        T(d, 540, Y(360), 'VOCÊ PERDE MINUTOS, NÃO A NOITE', 28, GRAY, 'mm')

def sc_eye(img, d, t, r, Dd):
    s = pop(r, 0.1)
    cx, cy = 540, Y(180)
    d.ellipse((cx - 150 * s, cy - 80 * s, cx + 150 * s, cy + 80 * s), fill=WHITE, outline=OL, width=6)
    d.ellipse((cx - 55 * s, cy - 55 * s, cx + 55 * s, cy + 55 * s), fill=GOLD, outline=OL, width=5)
    d.ellipse((cx - 22 * s, cy - 22 * s, cx + 22 * s, cy + 22 * s), fill=OL)
    if r > 0.8:
        T(d, 540, Y(340), 'OS PRIMEIROS MINUTOS', 30, GRAY, 'mm')

def sc_cta(img, d, t, r, Dd):
    s = pop(r, 0.1)
    d.rounded_rectangle((300, Y(40), 780, Y(80)), radius=12, fill=CHAR, outline=OL, width=4)
    nozzle(d, 540, Y(200), 0.9)
    bed(d, 280, 800, Y(290))
    d.rounded_rectangle((420, Y(250), 660, Y(290)), radius=8, fill=GOLD, outline=OL, width=4)
    R = int(60 * s)
    d.ellipse((830 - R, Y(90) - R, 830 + R, Y(90) + R), fill=(72, 150, 88), outline=OL, width=5)
    if s > 0.8:
        check(d, 830, Y(92), 2.2, WHITE)
    T(d, 540, Y(360), 'DÚVIDA? MANDA PRA GENTE', 30, GRAY, 'mm')

def spool(d, cx, cy, R, col, lab=None):
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=col, outline=OL, width=5)
    d.ellipse((cx - R * 0.72, cy - R * 0.72, cx + R * 0.72, cy + R * 0.72), outline=OL, width=3)
    d.ellipse((cx - R * 0.3, cy - R * 0.3, cx + R * 0.3, cy + R * 0.3), fill=CREAM, outline=OL, width=4)
    d.arc((cx - R * 0.88, cy - R * 0.88, cx + R * 0.2, cy + R * 0.2), 200, 270, fill=WHITE, width=max(3, int(R * 0.06)))
    if lab:
        band(d, cx, cy + R + 12, lab, max(60, int(R * 0.75)), 30)

def chip(d, cx, cy, txt, w=260, size=26):
    d.rounded_rectangle((cx - w // 2, cy - 28, cx + w // 2, cy + 28), radius=18, fill=WHITE, outline=OL, width=4)
    T(d, cx, cy, txt, max(8, size), OL, 'mm')

def sun(d, cx, cy, R):
    for k in range(8):
        a_ = k * math.pi / 4
        d.line((cx + R * 1.35 * math.cos(a_), cy + R * 1.35 * math.sin(a_), cx + R * 1.8 * math.cos(a_), cy + R * 1.8 * math.sin(a_)), fill=GOLD, width=7)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=GOLD, outline=OL, width=4)

def car(d, cx, cy, s=1.0):
    s = max(0.05, s)
    d.polygon([(cx - 70 * s, cy - 30 * s), (cx - 40 * s, cy - 70 * s), (cx + 45 * s, cy - 70 * s), (cx + 80 * s, cy - 30 * s)], fill=BLUE, outline=OL)
    d.rounded_rectangle((cx - 120 * s, cy - 30 * s, cx + 120 * s, cy + 25 * s), radius=int(14 * s), fill=BLUE, outline=OL, width=4)
    for dx in (-70, 70):
        d.ellipse((cx + dx * s - 24 * s, cy + 5 * s, cx + dx * s + 24 * s, cy + 53 * s), fill=CHAR, outline=OL, width=4)

def sc_pla_all(img, d, t, r, Dd):
    s = pop(r, 0.1)
    spool(d, 300, Y(160), max(4, int(100 * s)), RED, 'PLA' if s > 0.8 else None)
    for k, txt in enumerate(('PEÇA DE CARRO', 'DE COZINHA', 'CAPINHA')):
        u = min(1.0, pop(r, 1.4 + k * 0.9))
        if u > 0.05:
            chip(d, 745, Y(80 + k * 90), txt, int(320 * u), int(26 * u))
    if r > Dd * 0.85:
        T(d, 540, Y(372), 'PLA PRA TUDO?', 30, GRAY, 'mm')

def sc_three_f(img, d, t, r, Dd):
    if r > 0.3:
        T(d, 540, Y(50), 'CADA UM NO SEU TRABALHO', 28, GRAY, 'mm')
    for k, (lab, col) in enumerate((('PLA', RED), ('PETG', BLUE), ('TPU', GREEN))):
        s = pop(r, Dd * (0.4 + 0.2 * k))
        if s > 0.03:
            spool(d, 210 + k * 330, Y(185), max(4, int(85 * s)), col, lab if s > 0.8 else None)

def sc_pla(img, d, t, r, Dd):
    if r < Dd * 0.6:
        spool(d, 260, Y(165), 100, RED, 'PLA')
        for k, (txt, st) in enumerate((('FÁCIL DE IMPRIMIR', 0.5), ('DECORAÇÃO', 2.9), ('TESTE', 3.9))):
            u = min(1.0, pop(r, st))
            if u > 0.05:
                chip(d, 715, Y(75 + k * 95), txt, int(330 * u), int(26 * u))
    else:
        u = pop(r, Dd * 0.6)
        sun(d, 800, Y(100), max(4, int(48 * u)))
        car(d, 400, Y(235), 1.5 * u)
        if r < Dd * 0.82:
            T(d, 540, Y(372), 'AMOLECE COM CALOR', 30, RED, 'mm')
        else:
            T(d, 540, Y(372), 'NÃO DEIXA NO CARRO, NO SOL', 28, RED, 'mm')

def sc_bent(img, d, t, r, Dd):
    sun(d, 850, Y(70), 36)
    bend = 80 * sm(r / 1.4)
    pts = [(220 + k * 32, Y(210) + bend * math.sin(math.pi * k / 20)) for k in range(21)]
    d.line(pts, fill=OL, width=46, joint='curve')
    d.line(pts, fill=RED, width=34, joint='curve')
    if r > 1.2:
        T(d, 540, Y(350), 'A PEÇA ENTORTOU', 30, RED, 'mm')

def sc_petg(img, d, t, r, Dd):
    spool(d, 170, Y(140), 78, BLUE, 'PETG')
    T(d, 640, Y(40), 'AGUENTA CALOR', 26, GRAY, 'mm')
    u1 = sm((r - 1.0) / 1.6)
    u2 = sm((r - 3.0) / 2.2)
    for k, (lab, col, ln, u) in enumerate((('PLA', RED, 200, u1), ('PETG', BLUE, 460, u2))):
        y = Y(120 + k * 80)
        T(d, 385, y, lab, 28, OL, 'rm')
        d.rounded_rectangle((400, y - 26, 400 + max(6, ln * u), y + 26), radius=12, fill=col, outline=OL, width=4)
    if r > Dd * 0.45:
        T(d, 640, Y(300), 'MAIS RESISTENTE', 32, OL, 'mm')
    foot(d, 'comparação ilustrativa')

def sc_tpu(img, d, t, r, Dd):
    spool(d, 170, Y(130), 78, GREEN, 'TPU')
    pts = [(330 + k * 24, Y(120) + 38 * math.sin(k * 0.55 + r * 4.5)) for k in range(29)]
    d.line(pts, fill=OL, width=36, joint='curve')
    d.line(pts, fill=GREEN, width=24, joint='curve')
    if r > 1.0:
        T(d, 640, Y(205), 'FLEXÍVEL, TIPO BORRACHA', 26, GRAY, 'mm')
    for k, txt in enumerate(('CAPINHA', 'PÉ DE APOIO', 'VEDAÇÃO')):
        u = min(1.0, pop(r, Dd * (0.42 + 0.13 * k)))
        if u > 0.05:
            chip(d, 215 + k * 325, Y(310), txt, int(250 * u), int(26 * u))
    if r > Dd * 0.86:
        T(d, 540, Y(372), 'IMPRIME MAIS DEVAGAR', 24, GRAY, 'mm')

def sc_which(img, d, t, r, Dd):
    s = pop(r, 0.1)
    for k, col in enumerate((RED, BLUE, GREEN)):
        spool(d, 200 + k * 170, Y(210), 62, col)
    T(d, 780, Y(150), '?', max(1, int(150 * s)), GRAY, 'mm')

def sc_rows(img, d, t, r, Dd):
    rows = (('DECORAÇÃO · TESTE', 'PLA', RED), ('CALOR · ESFORÇO', 'PETG', BLUE), ('PRECISA DOBRAR', 'TPU', GREEN))
    for k, (txt, lab, col) in enumerate(rows):
        if r > 0.3 + k * Dd * 0.27:
            y = Y(85 + k * 100)
            rr(d, (110, y - 38, 970, y + 38), 20, WHITE, OL, 4)
            T(d, 150, y, txt, 30, OL, 'lm')
            arrow(d, 560, y, 650, y)
            T(d, 690, y, lab, 36, OL, 'lm')
            spool(d, 915, y, 28, col)

def sc_checks(img, d, t, r, Dd):
    for k, (lab, col) in enumerate((('PLA', RED), ('PETG', BLUE), ('TPU', GREEN))):
        s = pop(r, 0.1 + k * 0.35)
        x = 210 + k * 330
        if s > 0.03:
            spool(d, x, Y(185), max(4, int(80 * s)), col, lab if s > 0.8 else None)
            if s > 0.8:
                d.ellipse((x + 40, Y(95), x + 90, Y(145)), fill=GREEN, outline=OL, width=4)
                check(d, x + 65, Y(121), 1.3, WHITE)

def sc_cta_f(img, d, t, r, Dd):
    s = pop(r, 0.1)
    spool(d, 540, Y(185), max(4, int(90 * s)), RED, 'PLA' if s > 0.8 else None)
    R = max(2, int(60 * s))
    d.ellipse((830 - R, Y(90) - R, 830 + R, Y(90) + R), fill=GREEN, outline=OL, width=5)
    if s > 0.8:
        check(d, 830, Y(92), 2.2, WHITE)
    T(d, 540, Y(360), 'SALVA E MANDA PRA QUEM USA PLA PRA TUDO', 26, GRAY, 'mm')

def trash(d, cx, cy, s=1.0):
    d.polygon([(cx - 50 * s, cy - 40 * s), (cx + 50 * s, cy - 40 * s), (cx + 40 * s, cy + 50 * s), (cx - 40 * s, cy + 50 * s)], fill=(206, 200, 190), outline=OL)
    d.rounded_rectangle((cx - 60 * s, cy - 58 * s, cx + 60 * s, cy - 40 * s), radius=int(6 * s), fill=GRAY, outline=OL, width=3)
    for k in (-18, 0, 18):
        d.line((cx + k * s, cy - 22 * s, cx + k * s * 0.9, cy + 36 * s), fill=OL, width=3)

SUPC = (226, 176, 74)

def overhang(d, x0, x1, yb, ytop, th=46, cols=7, u=1.0, col=SUPC, legs=True):
    # printed part: slab with two legs at the ends, supports in between
    d.rounded_rectangle((x0, ytop, x1, ytop + th), radius=10, fill=RED, outline=OL, width=4)
    if legs:
        for lx in (x0, x1 - 40):
            d.rectangle((lx, ytop + th, lx + 40, yb), fill=RED, outline=OL, width=3)
    if cols and u > 0:
        n = max(1, int(cols * u))
        step = (x1 - x0 - 120) / max(1, cols - 1)
        for k in range(n):
            x = x0 + 60 + k * step
            d.rectangle((x - 5, ytop + th, x + 5, yb), fill=col, outline=OL, width=2)

def tsupport(d, cx, yb, ytop, u=1.0, col=SUPC):
    # tree support: trunk that branches and touches the slab at a few points
    if u <= 0:
        return
    ymid = yb - (yb - ytop) * 0.55
    d.line((cx, yb, cx, ymid), fill=OL, width=16)
    d.line((cx, yb, cx, ymid), fill=col, width=9)
    tips = [-150, 0, 150]
    for tx in tips:
        pts = [(cx, ymid), (cx + tx * 0.5 * u, ymid - (ymid - ytop) * 0.55 * u), (cx + tx * u, ytop + (ytop * 0) )] if False else None
        x1, y1 = cx + tx * u, ymid - (ymid - ytop) * u
        d.line((cx, ymid, x1, y1), fill=OL, width=14)
        d.line((cx, ymid, x1, y1), fill=col, width=7)

def sc_igual(img, d, t, r, Dd):
    yb = Y(300)
    bed(d, 150, 930, yb)
    overhang(d, 300, 780, yb, Y(150), cols=7, u=clamp(r / 1.6))
    if r > 1.2:
        chip(d, 540, Y(60), 'SUPORTE AUTOMÁTICO', 400, 26)

def sc_colunas(img, d, t, r, Dd):
    yb = Y(300)
    bed(d, 150, 930, yb)
    n = clamp(r / 1.2)
    overhang(d, 250, 730, yb, Y(150), cols=11, u=1.0, col=SUPC if r < Dd * 0.55 else (186, 140, 130))
    if r > Dd * 0.55:
        u = pop(r, Dd * 0.55)
        trash(d, 870, Y(210), 0.9 * u)
        T(d, 870, Y(290), 'LIXO', 26, GRAY, 'mm')
    if r > 0.9:
        T(d, 490, Y(372), 'COLUNA EM TUDO', 28, GRAY, 'mm')

def sc_pouco(img, d, t, r, Dd):
    s = pop(r, 0.1)
    spool(d, 340, Y(185), max(4, int(90 * s)), RED, None)
    if s > 0.05:
        T(d, 700, Y(180), '?', max(1, int(150 * s)), GRAY, 'mm')
    if r > 1.0:
        T(d, 540, Y(360), 'SÓ UM POUQUINHO?', 30, GRAY, 'mm')

def sc_grande(img, d, t, r, Dd):
    yb = Y(300)
    if r < Dd * 0.5:
        bed(d, 130, 950, yb)
        overhang(d, 210, 870, yb, Y(90), th=60, cols=15, u=clamp(r / 1.0))
        T(d, 540, Y(372), 'PEÇA GRANDE: MUITO SUPORTE', 26, GRAY, 'mm') if r > 1.2 else None
    else:
        u = pop(r, Dd * 0.5)
        x0, x1 = 160, 920
        d.rounded_rectangle((x0, Y(100), x1, Y(190)), radius=14, fill=RED, outline=OL, width=4)
        for k in range(12):
            x = x0 + 40 + k * 62
            d.rectangle((x - 5, Y(190), x + 5, Y(250) * 1 if False else Y(250)), fill=SUPC, outline=OL, width=2)
        for k in range(12):
            if r > Dd * 0.5 + 0.2 + k * 0.08:
                x = x0 + 40 + k * 62
                d.ellipse((x - 11, Y(190) - 7, x + 11, Y(190) + 15), fill=(150, 40, 48), outline=OL, width=2)
        if r > Dd * 0.5 + 1.6:
            magnifier(d, 770, Y(205), 52)
            T(d, 540, Y(340), 'MARCA ONDE ENCOSTA', 30, RED, 'mm')

def sc_outro(img, d, t, r, Dd):
    s = pop(r, 0.1)
    if s > 0.05:
        T(d, 540, Y(185), '?', int(220 * s), GRAY, 'mm')
    if r > 0.5:
        T(d, 540, Y(350), 'OUTRO JEITO?', 30, GRAY, 'mm')

def sc_arvore(img, d, t, r, Dd):
    yb = Y(300)
    bed(d, 150, 930, yb)
    if r < Dd * 0.4:
        d.rounded_rectangle((300, Y(150), 780, Y(196)), radius=10, fill=RED, outline=OL, width=4)
        d.rectangle((300, Y(196), 780, yb), fill=SUPC, outline=OL, width=3)
        T(d, 540, Y(250), 'PAREDE CHEIA', 30, OL, 'mm')
        if r > 0.9:
            k = sm((r - 0.9) / 0.4)
            d.line((330, Y(120), 330 + 420 * k, Y(120) + 190 * k), fill=RED, width=12)
            d.line((750, Y(120), 750 - 420 * k, Y(120) + 190 * k), fill=RED, width=12)
    else:
        u = clamp((r - Dd * 0.4) / 1.8)
        d.rounded_rectangle((300, Y(150), 780, Y(196)), radius=10, fill=RED, outline=OL, width=4)
        for lx in (300, 740):
            d.rectangle((lx, Y(196), lx + 40, yb), fill=RED, outline=OL, width=3)
        tsupport(d, 540, yb, Y(196), u)
        if r > Dd * 0.4 + 1.8:
            T(d, 540, Y(372), 'GALHOS SÓ ONDE PRECISA', 28, GRAY, 'mm')
    foot(d, 'exemplo ilustrativo')

def sc_menos(img, d, t, r, Dd):
    u1 = sm((r - 0.3) / 1.2)
    u2 = sm((r - 1.0) / 1.4)
    for k, (lab, col, ln, u) in enumerate((('COMUM', SUPC, 460, u1), ('ÁRVORE', GREEN, 230, u2))):
        y = Y(90 + k * 90)
        T(d, 330, y, lab, 28, OL, 'rm')
        d.rounded_rectangle((350, y - 28, 350 + max(6, ln * u), y + 28), radius=12, fill=col, outline=OL, width=4)
    T(d, 540, Y(60 - 40) if False else Y(30), 'FILAMENTO DE SUPORTE', 26, GRAY, 'mm')
    if r > Dd * 0.55:
        s = pop(r, Dd * 0.55)
        R = max(2, int(36 * s))
        d.ellipse((260 - R, Y(300) - R, 260 + R, Y(300) + R), fill=GREEN, outline=OL, width=4)
        if s > 0.8:
            check(d, 260, Y(302), 1.4, WHITE)
        T(d, 330, Y(300), 'SAI MAIS FÁCIL DE TIRAR', 28, OL, 'lm')
    foot(d, 'comparação ilustrativa')

def sc_ligar(img, d, t, r, Dd):
    s = pop(r, 0.1)
    d.rounded_rectangle((380, Y(150), 700, Y(230)), radius=40, fill=GREEN if r > 0.9 else GRAY, outline=OL, width=5)
    kx = 420 + (240 if r > 0.9 else 0) * 1.0
    d.ellipse((kx - 30, Y(190) - 30, kx + 30, Y(190) + 30), fill=WHITE, outline=OL, width=4)
    if s > 0.05:
        T(d, 540, Y(70), 'LIGAR E PRONTO?', 32, GRAY, 'mm')
        T(d, 850, Y(190), '?', int(110 * s), GRAY, 'mm')

def sc_preview(img, d, t, r, Dd):
    rr(d, (300, Y(40), 780, Y(300)), 16, (240, 236, 228), OL, 4)
    T(d, 540, Y(62), 'PREVIEW', 22, GRAY, 'mm')
    yb = Y(280)
    d.line((320, yb, 760, yb), fill=OL, width=4)
    d.rounded_rectangle((380, Y(120), 700, Y(158)), radius=8, fill=RED, outline=OL, width=3)
    tsupport(d, 540, yb, Y(158), 1.0)
    if r > 0.4:
        chip(d, 160, Y(130), 'MUITO DETALHE', 250, 22)
    if r > 1.6:
        chip(d, 920, Y(130), 'BASE PEQUENA', 230, 22)
    if r > Dd * 0.6:
        s = pop(r, Dd * 0.6)
        magnifier(d, 640, Y(190), max(8, int(48 * s)))
    if r > Dd * 0.75:
        T(d, 540, Y(350), 'CONFERE ANTES DE FATIAR', 28, OL, 'mm')

def sc_testar(img, d, t, r, Dd):
    s = pop(r, 0.1)
    R = max(2, int(95 * s))
    d.ellipse((540 - R, Y(170) - R, 540 + R, Y(170) + R), fill=GREEN, outline=OL, width=5)
    if s > 0.8:
        check(d, 540, Y(176), 3.6, WHITE)
    if r > 0.6:
        T(d, 540, Y(335), 'PRÓXIMA PEÇA', 32, GRAY, 'mm')

def sc_cta_s(img, d, t, r, Dd):
    s = pop(r, 0.1)
    bw, bh = int(420 * s), int(190 * s)
    if bw > 20:
        d.rounded_rectangle((540 - bw // 2, Y(170) - bh // 2, 540 + bw // 2, Y(170) + bh // 2), radius=40, fill=WHITE, outline=OL, width=5)
        d.polygon([(470, Y(170) + bh // 2 - 3), (530, Y(170) + bh // 2 - 3), (470, Y(170) + bh // 2 + 40)], fill=WHITE, outline=OL)
        d.rectangle((474, Y(170) + bh // 2 - 8, 526, Y(170) + bh // 2 - 1), fill=WHITE)
        if s > 0.8:
            T(d, 540, Y(170), '?', 120, OL, 'mm')
    if r > 1.2:
        T(d, 540, Y(350), 'QUAL PEÇA GASTA MAIS SUPORTE?', 26, GRAY, 'mm')

SCENES = [sc_igual, sc_colunas, sc_pouco, sc_grande, sc_outro, sc_arvore, sc_menos, sc_ligar, sc_preview, sc_testar, sc_cta_s]

# ---------------------------------------------------------------- bubbles
BS, BLH, BPAD, BMAXW = 34, 46, 26, 860
EMPH = {'suporte', 'árvore', 'galhos', 'filamento', 'preview', 'lixo', 'marca', 'acabamento', 'menos', 'fácil', 'comentários', 'detalhe', 'pequena', 'grande', 'comum', 'coluna', 'parede'}
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
    if t < P[4]:
        return 'smug'
    if t < P[9]:
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
              (t % 2.6) < 0.12, spk == 'mari', i in (1, 3, 5, 6, 8))
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
            paste_pop(img, pill('COMENTA: QUAL PEÇA?', 38, WHITE, CHAR), 540, 960, (t - t_end) / 0.28)
        else:
            paste_pop(img, pill('MARCA QUEM USA SUPORTE COMUM', 28, WHITE, CHAR, 'send'), 540, 960, (t - sw) / 0.28)
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
    final = f'{OUT}/mavan_suporte.mp4'
    cmd += ['-filter_complex', ';'.join(fc), '-map', f'{N}:v', '-map', '[aout]',
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', f'{TOTAL:.3f}', final + '.tmp.mp4']
    subprocess.check_call(cmd)
    os.rename(final + '.tmp.mp4', final)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':
        preview()
    elif len(sys.argv) > 1 and sys.argv[1] == 'render':
        render()
