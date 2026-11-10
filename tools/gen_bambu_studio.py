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
OUT = D + '/out5'
os.makedirs(OUT, exist_ok=True)
AF = D + '/aud5/fin/'

LINES = [
    ('01.wav', 'cliente', 'Comprei uma Bambu, apertei imprimir e deu ruim. Impressora ruim, né?'),
    ('02.wav', 'mari', 'Não é a impressora. O Bambu Studio esconde metade das configurações. Primeiro: muda pro modo Avançado, no canto superior direito.'),
    ('03.wav', 'mari', 'Segundo: clica em Auto Orient antes de fatiar. A peça fica na melhor posição e usa menos suporte.'),
    ('04.wav', 'mari', 'Terceiro: infill de 15%, padrão Gyroid. Acima disso você só gasta filamento.'),
    ('05.wav', 'mari', 'Quarto: suporte Tree Slim. Gasta menos filamento e quase não deixa marca.'),
    ('06.wav', 'mari', 'Quinto: abre o Preview e arrasta as camadas antes de imprimir. Dá pra achar o erro antes de perder três horas.'),
    ('07.wav', 'mari', 'E se não lembra onde fica cada opção, aperta Control F e digita o nome. A barra de busca acha pra você.'),
    ('08.wav', 'cliente', 'Então o problema nunca foi a impressora. Fui eu.'),
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

TITLES = ['SUA IMPRESSORA JOGA FILAMENTO FORA', '1 · MODO AVANÇADO', '2 · AUTO ORIENT', '3 · INFILL 15% GYROID',
          '4 · SUPORTE TREE SLIM', '5 · PREVIEW ANTES DE IMPRIMIR', 'BÔNUS · BARRA DE BUSCA', 'CHECKLIST MAVAN']

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

# ---------------------------------------------------------------- scene contents (y relative to CY0)
def Y(v):
    return CY0 + v

def sc_hook(img, d, t, r, Dd):
    bx0, bx1, by0, by1 = 380, 700, Y(30), Y(350)
    rr(d, (bx0, by0, bx1, by1), 16, (250, 246, 238), OL, 4)
    for k in range(1, 8):
        d.line((bx0 + k * 40, by0 + 4, bx0 + k * 40, by1 - 4), fill=LINEC, width=2)
        d.line((bx0 + 4, by0 + k * 40, bx1 - 4, by0 + k * 40), fill=LINEC, width=2)
    base = (540, by1 - 30)
    for i in range(11):
        pts = []
        for k in range(26):
            u = k / 25.0
            x = base[0] + (i - 5) * 13 * (u + 0.3) + 90 * math.sin(k * 0.7 + i * 2.1 + t * 1.5) * u
            y = base[1] - u * 250 + 8 * math.sin(k * 1.3 + i)
            pts.append((x, y))
        d.line(pts, fill=GOLD if i % 2 else (250, 206, 110), width=5, joint='curve')
    d.ellipse((base[0] - 70, base[1] - 8, base[0] + 70, base[1] + 14), fill=GOLD, outline=OL, width=3)
    # left: filament counter
    n = int(187 * sm(r / max(0.5, Dd)))
    T(d, 105, Y(80), 'FILAMENTO', 26, GRAY)
    T(d, 105, Y(112), 'NO LIXO', 26, GRAY)
    T(d, 105, Y(190), f'{n} g', 78, RED)
    # right: warning
    draw_icon(d, 'warn', 850, Y(120), 62)
    T(d, 850, Y(230), 'PRINT FALHOU', 24, RED, 'mm')
    put(img, 'FALHOU!', 74, RED, 540, Y(188), t, P[0] + 0.55)
    foot(d)

ROWS = ['Altura da camada', 'Velocidade', 'Paredes', 'Preenchimento', 'Suporte', 'Borda (brim)',
        'Ordem das paredes', 'Costura', 'Camada variável', 'Fluxo']

def sc_adv(img, d, t, r, Dd):
    tc = 0.62 * Dd
    adv = sm((r - tc) / 0.25)
    T(d, 92, Y(22), 'PROCESSO', 22, GRAY, 'lm', FM)
    for k, name in enumerate(ROWS):
        y0 = Y(42 + k * 34)
        if k < 4:
            rr(d, (90, y0, 540, y0 + 30), 8, WHITE, (210, 202, 190), 2)
            T(d, 106, y0 + 15, name, 22)
        else:
            u = sm((r - tc - 0.1 - (k - 4) * 0.07) / 0.2)
            if u <= 0:
                rr(d, (90, y0, 540, y0 + 30), 8, (240, 235, 226), (222, 214, 200), 2)
                lock(d, 104, y0 - 1, (176, 168, 158))
                T(d, 140, y0 + 15, '· · · · ·', 22, (176, 168, 158))
            else:
                fill = tuple(int(lerp(a, b, u)) for a, b in zip(GOLDL, WHITE)) if u < 1 else WHITE
                rr(d, (90, y0, 540, y0 + 30), 8, fill, GOLD if u < 1 else (210, 202, 190), 3 if u < 1 else 2)
                T(d, 106, y0 + 15, name, 22)
    # toggle Simples | Avançado
    T(d, 640, Y(22), 'MODO', 22, GRAY, 'lm', FM)
    rr(d, (640, Y(40), 980, Y(90)), 25, (240, 235, 226), OL, 4)
    x0 = 645 + adv * 165
    rr(d, (x0, Y(45), x0 + 165, Y(85)), 20, CHAR, CHAR, 1)
    T(d, 727, Y(65), 'Simples', 24, WHITE if adv < 0.5 else GRAY, 'mm')
    T(d, 892, Y(65), 'Avançado', 24, WHITE if adv >= 0.5 else GRAY, 'mm')
    # preview plate
    rr(d, (640, Y(150), 980, Y(350)), 16, (250, 246, 238), OL, 3)
    rr(d, (770, Y(200), 850, Y(330)), 10, GOLD, OL, 4)
    d.ellipse((770, Y(188), 850, Y(214)), fill=GOLDL, outline=OL, width=3)
    cx, cy = path(r, [(0, 800, Y(300)), (tc - 0.12, 898, Y(66)), (Dd + 1, 898, Y(66))])
    cursor(img, cx, cy, (r - tc) / 0.4)

def sc_orient(img, d, t, r, Dd):
    tc = 0.28 * Dd
    bed_y = Y(BED_REL)
    # toolbar
    for k in range(4):
        y0 = Y(26 + k * 84)
        on = (k == 2)
        rr(d, (90, y0, 156, y0 + 64), 14, GOLD if on else WHITE, OL, 4)
        cxk, cyk = 123, y0 + 32
        if k == 0:
            d.line((cxk - 16, cyk, cxk + 16, cyk), fill=OL, width=4); d.line((cxk, cyk - 16, cxk, cyk + 16), fill=OL, width=4)
        elif k == 1:
            d.arc((cxk - 16, cyk - 16, cxk + 16, cyk + 16), 40, 330, fill=OL, width=4)
            d.polygon([(cxk + 12, cyk - 18), (cxk + 22, cyk - 6), (cxk + 6, cyk - 6)], fill=OL)
        elif k == 2:
            d.arc((cxk - 17, cyk - 17, cxk + 17, cyk + 17), 20, 300, fill=OL, width=5)
            d.polygon([(cxk + 16, cyk - 16), (cxk + 26, cyk - 2), (cxk + 8, cyk - 4)], fill=OL)
            d.rectangle((cxk - 7, cyk - 7, cxk + 7, cyk + 7), fill=OL)
        else:
            d.rectangle((cxk - 14, cyk - 14, cxk + 14, cyk + 14), outline=OL, width=4)
    T(d, 172, Y(26 + 2 * 84 + 32), 'Auto Orient', 24, OL, 'lm')
    # bed and model
    rr(d, (330, Y(40), 750, bed_y + 18), 16, (250, 246, 238), OL, 4)
    d.line((344, bed_y, 736, bed_y), fill=OL, width=3)
    theta = math.radians(50 * (1 - sm((r - tc) / 0.6)))
    x0 = 410
    w, h = 240, 66
    u = (math.cos(theta), -math.sin(theta))
    v = (-math.sin(theta), -math.cos(theta))
    P0 = (x0, bed_y)
    P1 = (P0[0] + w * u[0], P0[1] + w * u[1])
    P2 = (P1[0] + h * v[0], P1[1] + h * v[1])
    P3 = (P0[0] + h * v[0], P0[1] + h * v[1])
    if P1[1] < bed_y - 2:
        slope = (P1[1] - P0[1]) / (P1[0] - P0[0])
        xx = P0[0]
        while xx < P1[0]:
            yy = P0[1] + (xx - P0[0]) * slope
            d.line((xx, yy, xx, bed_y), fill=RED, width=2)
            xx += 11
        d.line((P0[0], bed_y, P1[0], bed_y), fill=RED, width=2)
        d.line((P1[0], P1[1], P1[0], bed_y), fill=RED, width=2)
    d.polygon([P0, P1, P2, P3], fill=GOLD)
    d.line([P0, P1, P2, P3, P0], fill=OL, width=4, joint='curve')
    # support meter
    need = 0.14 + 0.86 * (math.degrees(theta) / 50.0)
    rr(d, (780, Y(60), 985, Y(200)), 16, WHITE, OL, 3)
    T(d, 800, Y(84), 'SUPORTE', 22, GRAY, 'lm', FM)
    rr(d, (800, Y(110), 965, Y(142)), 10, (240, 235, 226), OL, 3)
    colr = tuple(int(lerp(a, b, need)) for a, b in zip((120, 190, 120), RED))
    rr(d, (800, Y(110), 800 + 165 * need, Y(142)), 10, colr, OL, 3)
    if need < 0.2:
        put(img, 'MENOS!', 34, (60, 140, 70), 882, Y(170), t, P[2] + tc + 0.7, FB)
    cx, cy = path(r, [(0, 700, Y(260)), (tc - 0.12, 150, Y(26 + 2 * 84 + 40)), (Dd + 1, 150, Y(26 + 2 * 84 + 40))])
    cursor(img, cx, cy, (r - tc) / 0.4)
    foot(d)

def infill_pattern(d, box, spacing, amp, phase):
    x0, y0, x1, y1 = box
    ww = 6
    # sine/straight lines in both directions, clipped by drawing within the box
    xs = x0 + spacing / 2
    while xs < x1 - 6:
        pts = []
        for k in range(0, int(y1 - y0) + 1, 6):
            pts.append((min(x1 - 8, max(x0 + 8, xs + amp * math.sin(k / 22.0 + phase))), y0 + k))
        d.line(pts, fill=GOLD, width=5, joint='curve')
        xs += spacing
    ys = y0 + spacing / 2
    while ys < y1 - 6:
        pts = []
        for k in range(0, int(x1 - x0) + 1, 6):
            pts.append((x0 + k, min(y1 - 8, max(y0 + 8, ys + amp * math.sin(k / 22.0 + phase + 1.6)))))
        d.line(pts, fill=GOLD, width=5, joint='curve')
        ys += spacing
    rr(d, (x0, y0, x1, y1), 6, None, OL, 8)

def sc_infill(img, d, t, r, Dd):
    t1, t2 = 0.18 * Dd, 0.46 * Dd
    # field 1
    T(d, 540, Y(36), 'Densidade de preenchimento', 22, GRAY, 'lm', FM)
    rr(d, (540, Y(52), 780, Y(102)), 12, WHITE, OL, 4)
    if r < t1 + 0.05:
        val = '40%'
    else:
        val = typed('15%', r, t1 + 0.1, t1 + 0.55)
        if (t * 3) % 1 < 0.6 and r < t1 + 0.9:
            val += '|'
    T(d, 560, Y(77), val, 30)
    # field 2
    T(d, 540, Y(134), 'Padrão de preenchimento', 22, GRAY, 'lm', FM)
    rr(d, (540, Y(150), 860, Y(200)), 12, WHITE, OL, 4)
    sel = r >= 0.64 * Dd
    T(d, 560, Y(175), 'Gyroid' if sel else 'Grid', 30)
    d.polygon([(830, Y(168)), (848, Y(168)), (839, Y(182))], fill=OL)
    if 0.50 * Dd <= r < 0.66 * Dd:
        rr(d, (540, Y(204), 860, Y(300)), 12, WHITE, OL, 3)
        for k, nm in enumerate(('Grid', 'Gyroid', 'Triângulos')):
            yy = Y(212 + k * 28)
            if nm == 'Gyroid':
                d.rectangle((546, yy, 854, yy + 26), fill=GOLDL)
            T(d, 560, yy + 13, nm, 22)
    # cross-section
    dens = sm((r - t1 - 0.15) / 0.5)
    spacing = lerp(26, 66, dens)
    amp = 16 * sm((r - 0.62 * Dd) / 0.4)
    infill_pattern(d, (110, Y(40), 410, Y(340)), spacing, amp, t * 0.6)
    T(d, 260, Y(366), 'corte da peça', 18, GRAY, 'mm', FM)
    if r > 0.72 * Dd:
        lay = pill('+ DE 40% = SÓ GASTA FILAMENTO', 24, RED, (255, 238, 236))
        paste_pop(img, lay, 745, Y(340), (r - 0.72 * Dd) / 0.28)
    cx, cy = path(r, [(0, 700, Y(300)), (t1, 690, Y(80)), (0.40 * Dd, 690, Y(80)), (t2 + 0.1, 760, Y(176)), (0.62 * Dd, 700, Y(255)), (Dd + 1, 700, Y(255))])
    cursor(img, cx, cy, (r - 0.62 * Dd) / 0.4 if r > 0.6 * Dd else (r - t1) / 0.4)
    foot(d)

def mushroom(d, cx, bed_y, support):
    cap_y0, cap_y1 = bed_y - 190, bed_y - 150
    stem_x0, stem_x1 = cx - 28, cx + 28
    return cap_y0, cap_y1

def sc_tree(img, d, t, r, Dd):
    tc = 0.30 * Dd
    # style chip
    rr(d, (330, Y(8), 750, Y(46)), 19, (240, 235, 226), OL, 3)
    T(d, 350, Y(27), 'Estilo do suporte:', 20, GRAY, 'lm', FM)
    chip = 'Tree Slim' if r >= tc else 'Normal'
    T(d, 578, Y(27), chip, 24, OL)
    cards = [(90, 520, 'NORMAL', False), (560, 990, 'TREE SLIM', True)]
    for x0, x1, name, tree in cards:
        hl = tree and r > 0.5 * Dd
        rr(d, (x0, Y(62), x1, Y(384)), 18, WHITE, GOLD if hl else OL, 7 if hl else 3)
        T(d, (x0 + x1) // 2, Y(88), name, 26, OL, 'mm')
        cx = (x0 + x1) // 2
        bed = Y(342)
        d.line((x0 + 20, bed, x1 - 20, bed), fill=OL, width=4)
        cap0, cap1 = Y(160), Y(196)
        stem = (cx - 26, cap1, cx + 26, bed)
        show = r > (0.05 * Dd if not tree else 0.35 * Dd)
        if show:
            if not tree:
                for sx0, sx1 in ((cx - 100, cx - 26), (cx + 26, cx + 100)):
                    d.rectangle((sx0, cap1, sx1, bed), fill=(255, 232, 230))
                    xx = sx0
                    while xx <= sx1:
                        d.line((xx, cap1, xx, bed), fill=RED, width=2)
                        xx += 7
                    d.rectangle((sx0, cap1, sx1, bed), outline=RED, width=2)
            else:
                for bx in (-62, 62):
                    b = (cx + bx, bed)
                    m = (cx + bx * 1.3, Y(270))
                    d.line([b, m], fill=(190, 130, 30), width=4)
                    for ex in (-18, 18):
                        d.line([m, (cx + bx * 1.45 + ex, cap1)], fill=(190, 130, 30), width=3)
        rr(d, (cx - 110, cap0, cx + 110, cap1), 10, GOLD, OL, 4)
        rr(d, stem, 6, GOLD, OL, 4)
        if show and r > 0.45 * Dd:
            if tree:
                put(img, 'gasta menos', 26, (60, 130, 70), cx, Y(364), t, P[4] + 0.5 * Dd)
            else:
                put(img, 'gasta mais', 26, RED, cx, Y(364), t, P[4] + 0.45 * Dd)
    cx, cy = path(r, [(0, 560, Y(300)), (tc - 0.12, 560, Y(27)), (Dd + 1, 560, Y(27))])
    cursor(img, cx, cy, (r - tc) / 0.4)

NL = 46

def vase_w(i):
    return 62 + 44 * math.sin(i / NL * math.pi * 1.25 + 0.3)

def sc_preview(img, d, t, r, Dd):
    prog = sm((r - 0.12 * Dd) / (0.62 * Dd))
    L = int(round(NL * prog))
    bottom = Y(364)
    cx = 400
    for i in range(NL):
        y = bottom - (i + 1) * 7
        if i == 26:
            continue
        if i < L:
            col = GOLD if i % 2 == 0 else (244, 196, 96)
            d.rectangle((cx - vase_w(i), y, cx + vase_w(i), y + 7), fill=col)
        else:
            d.rectangle((cx - vase_w(i), y, cx + vase_w(i), y + 7), outline=(226, 219, 207), width=1)
    d.line((cx - 120, bottom, cx + 120, bottom), fill=OL, width=3)
    if L > 27:
        gy = bottom - 27 * 7
        for k in range(-int(vase_w(26)), int(vase_w(26)), 12):
            d.line((cx + k, gy + 4, cx + k + 6, gy + 4), fill=RED, width=3)
        pulse = 6 + 4 * math.sin(t * 8)
        d.ellipse((cx - 100 - pulse, gy - 20 - pulse, cx + 100 + pulse, gy + 28 + pulse), outline=RED, width=5)
    # slider
    d.line((930, bottom, 930, Y(40)), fill=(210, 202, 190), width=10)
    hy = bottom - (bottom - Y(40)) * prog
    d.line((930, bottom, 930, hy), fill=GOLD, width=10)
    d.ellipse((912, hy - 18, 948, hy + 18), fill=WHITE, outline=OL, width=4)
    T(d, 720, Y(26), f'Camada {int(prog * 230)}/230', 24, GRAY, 'lm', FM)
    if L > 27:
        paste_pop(img, pill('ERRO NO MEIO!', 34, WHITE, RED), 700, Y(150), (r - (0.12 + 0.62 * 27 / NL) * Dd) / 0.3)
    if r > 0.80 * Dd:
        paste_pop(img, pill('ACHOU ANTES DE PERDER 3h', 26, OL, GOLDL), 640, Y(300), (r - 0.80 * Dd) / 0.3)
    cx2, cy2 = 930, hy + 24
    cursor(img, cx2, cy2, -1)
    foot(d)

def keycap(d, x, y, txt, wd):
    d.rounded_rectangle((x - wd / 2, y - 36 + 8, x + wd / 2, y + 36 + 8), radius=14, fill=(200, 192, 180))
    rr(d, (x - wd / 2, y - 36, x + wd / 2, y + 36), 14, WHITE, OL, 4)
    T(d, x, y, txt, 34, OL, 'mm')

def sc_search(img, d, t, r, Dd):
    rr(d, (110, Y(20), 970, Y(76)), 28, WHITE, OL, 4)
    d.ellipse((134, Y(36), 158, Y(60)), outline=GRAY, width=4)
    d.line((154, Y(58), 166, Y(70)), fill=GRAY, width=4)
    q = typed('infill', r, 0.46 * Dd, 0.70 * Dd)
    if q:
        T(d, 182, Y(48), q + ('|' if (t * 3) % 1 < 0.6 and r < 0.9 * Dd else ''), 28)
    else:
        T(d, 182, Y(48), 'Buscar configuração...', 26, (176, 168, 158), 'lm', FM)
    if r < 0.50 * Dd:
        u = sm((r - 0.12 * Dd) / 0.25)
        if u > 0:
            kx = 540
            dy = (1 - u) * 20
            d2 = d
            keycap(d2, kx - 100, Y(190) + dy, 'Ctrl', 170)
            T(d, kx, Y(190) + dy, '+', 40, GRAY, 'mm')
            keycap(d2, kx + 100, Y(190) + dy, 'F', 110)
    else:
        res = [('Preenchimento', 'Densidade de preenchimento', True),
               ('Preenchimento', 'Padrão de preenchimento', True),
               ('Preenchimento', 'Sobreposição das paredes', False)]
        for k, (a, b, m) in enumerate(res):
            u = sm((r - 0.72 * Dd - k * 0.12) / 0.2)
            if u <= 0:
                continue
            y0 = Y(110 + k * 70)
            rr(d, (110, y0, 970, y0 + 58), 14, GOLDL if (m and k == 0) else WHITE, GOLD if m else (210, 202, 190), 4 if m else 2)
            T(d, 134, y0 + 29, a + '  ▸  ', 24, GRAY, 'lm', FM)
            wa = font(FM, 24).getlength(a + '  ▸  ')
            T(d, 134 + wa, y0 + 29, b, 26, OL)
    foot(d)

CHECKS = ['Modo Avançado', 'Auto Orient', 'Infill 15% + Gyroid', 'Suporte Tree Slim', 'Preview antes de imprimir',
          'Ctrl + F  =  busca']

def sc_recap(img, d, t, r, Dd):
    for k, txt in enumerate(CHECKS):
        u = sm((r - 0.05 * Dd - k * 0.35) / 0.25)
        if u <= 0:
            continue
        y = Y(36 + k * 58)
        rr(d, (150, y - 24, 930, y + 24), 24, WHITE, OL, 3)
        d.ellipse((166, y - 18, 202, y + 18), fill=GOLD, outline=OL, width=3)
        check(d, 184, y + 1, 0.9)
        T(d, 226, y, txt, 30)

SCENES = [sc_hook, sc_adv, sc_orient, sc_infill, sc_tree, sc_preview, sc_search, sc_recap]

# ---------------------------------------------------------------- bubbles
BS, BLH, BPAD, BMAXW = 36, 48, 26, 860
EMPH = {'primeiro', 'segundo', 'terceiro', 'quarto', 'quinto', 'avançado', 'auto', 'orient', 'gyroid', 'tree',
        'slim', 'preview', 'control', 'f', '15%'}
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
    if t < P[7]:
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
              (t % 2.6) < 0.12, spk == 'mari', i == 5)
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
            paste_pop(img, pill('MANDA PRA QUEM COMPROU IMPRESSORA', 32, WHITE, CHAR, 'send'), 540, 960, (t - sw) / 0.28)
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
    moments = [0.6, P[1] + AUD[1]['d'] * 0.40, P[1] + AUD[1]['d'] * 0.95,
               P[2] + AUD[2]['d'] * 0.20, P[2] + AUD[2]['d'] * 0.90,
               P[3] + AUD[3]['d'] * 0.35, P[3] + AUD[3]['d'] * 0.95,
               P[4] + AUD[4]['d'] * 0.85, P[5] + AUD[5]['d'] * 0.55, P[5] + AUD[5]['d'] * 0.95,
               P[6] + AUD[6]['d'] * 0.35, P[6] + AUD[6]['d'] * 0.95, P[7] + AUD[7]['d'] * 0.8, CEND - 0.5, CEND + 0.9]
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
    final = f'{OUT}/mavan_bambu_studio_dicas.mp4'
    cmd += ['-filter_complex', ';'.join(fc), '-map', f'{N}:v', '-map', '[aout]',
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', f'{TOTAL:.3f}', final + '.tmp.mp4']
    subprocess.check_call(cmd)
    os.rename(final + '.tmp.mp4', final)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':
        preview()
    elif len(sys.argv) > 1 and sys.argv[1] == 'render':
        render()
