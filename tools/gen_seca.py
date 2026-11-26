"""Vídeo C de 26/11/2026 (TikTok): como secar filamento sem estufa (explicativo sem personagem, cenas desenhadas).

    python3 -I gen_seca.py preview|render
"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
sys.path.insert(0, HERE)
import gen4 as g
from gen4 import (W, H, FPS, CREAM, CHAR, OL, GOLD, GOLDL, WARM, LINEC, GRAY, RED, WHITE, FB, FM,
                  pill, font, eob, paste_pop, paste_center, put, logo_w, logo_bug)

D = g.D
KEY = 'ig'
CFG = dict(
    out='/out22', af='/aud22/fin/', final='mavan_secar_filamento.mp4',
    lines=[
        'Seu filamento está estalando e você continua imprimindo assim. Dá pra secar sem estufa.',
        'Primeiro: o forno da cozinha. Temperatura baixa, abaixo de onde o material amolece, por várias horas. O PLA amolece cedo, então pra ele é ainda mais baixa.',
        'O perigo é o forno errar a temperatura e derreter o rolo. Usa um termômetro de forno e só coloca o rolo depois que a temperatura estabilizar.',
        'Micro-ondas, nem tenta. Ele esquenta de forma desigual e pode derreter o rolo e estragar o aparelho.',
        'Segundo: improvisar com a cama aquecida da impressora e uma caixa por cima. É mais lento, e exige cuidado pra não passar do ponto.',
        'Depois de seco, guarda em caixa fechada, com sílica. Salva esse vídeo pro próximo rolo que estalar, e manda pra quem imprime em 3D.',
    ],
    titles=['FILAMENTO ESTALANDO', 'OPÇÃO 1 · FORNO', 'CUIDADO COM O FORNO', 'MICRO-ONDAS: NÃO', 'OPÇÃO 2 · CAMA AQUECIDA',
            'DEPOIS DE SECO'],
    emph={'estalando', 'estufa', 'forno', 'baixa', 'amolece', 'termômetro', 'derreter', 'micro-ondas', 'nem',
          'desigual', 'cama', 'aquecida', 'lento', 'cuidado', 'sílica', 'salva', 'manda', 'fechada'},
    pill1=('SALVA PRO PRÓXIMO ROLO', 'send'), pill2=('MANDA PRA QUEM IMPRIME', 'send'),
    hold=1.6, endcard=1.2,
)
OUT = D + CFG['out']
os.makedirs(OUT, exist_ok=True)
AF = D + CFG['af']
LEAD, GAP = 0.25, 0.32
HOLD, ENDCARD = CFG['hold'], CFG['endcard']

AUD = []
for k, txt in enumerate(CFG['lines']):
    fn = f'{k + 1:02d}.wav'
    s, e, env = g.analyse(AF + fn)
    AUD.append(dict(file=AF + fn, txt=txt, s=s, e=e, d=e - s, env=env))
P = []
_t = LEAD
for a in AUD:
    P.append(_t)
    _t += a['d'] + GAP
CEND = P[-1] + AUD[-1]['d'] + HOLD
TOTAL = CEND + ENDCARD
N = len(AUD)

# ---------------------------------------------------------------- utilidades de desenho
def sm(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def lerp(a, b, u):
    return a + (b - a) * u

def clamp(x):
    return max(0.0, min(1.0, x))

def pop(r, start, dur=0.3):
    return eob(clamp((r - start) / dur))

def T(d, x, y, txt, size, fill=OL, anchor='mm', fp=None):
    d.text((x, y), txt, font=font(fp or FB, size), fill=fill, anchor=anchor)

def rr(d, box, r, fill, ol=OL, w=4):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=ol, width=w)

def chip(d, cx, cy, txt, size=30, fill=CHAR, fg=GOLDL, s=1.0):
    if s < 0.05:
        return
    f = font(FB, max(8, int(size * s)))
    w = f.getlength(txt) + 44 * s
    h = size * 1.75 * s
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=h / 2, fill=fill, outline=OL, width=3)
    d.text((cx, cy), txt, font=f, fill=fg, anchor='mm')

def check_mark(d, x, y, s=1.0, col=WHITE):
    d.line([(x - 9 * s, y), (x - 2 * s, y + 8 * s), (x + 11 * s, y - 9 * s)], fill=col, width=max(3, int(6 * s)), joint='curve')

def badge_ok(d, cx, cy, R, s=1.0):
    R = int(R * s)
    if R < 3:
        return
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(72, 150, 88), outline=OL, width=4)
    check_mark(d, cx, cy + R * 0.05, R / 11, WHITE)

def badge_no(d, cx, cy, R, s=1.0):
    R = int(R * s)
    if R < 3:
        return
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=RED, outline=OL, width=4)
    q = R * 0.42
    d.line((cx - q, cy - q, cx + q, cy + q), fill=WHITE, width=max(4, int(R * 0.22)))
    d.line((cx - q, cy + q, cx + q, cy - q), fill=WHITE, width=max(4, int(R * 0.22)))

def arrow(d, x0, y0, x1, y1, col=OL, w=6):
    d.line((x0, y0, x1, y1), fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0)
    for s in (-0.5, 0.5):
        d.line((x1, y1, x1 - 22 * math.cos(a + s), y1 - 22 * math.sin(a + s)), fill=col, width=w)

SAND, SANDD = (238, 218, 170), (214, 190, 138)
SEA, SEAD = (110, 178, 214), (72, 140, 190)
SKY = (206, 232, 244)
BLUE = (86, 136, 196)
RUST = (186, 98, 44)
METAL = (176, 180, 188)
GREEN, GREEND = (72, 150, 88), (52, 118, 66)

def sun(d, cx, cy, R, rays=True, t=0.0):
    if rays:
        for k in range(12):
            a = k * math.pi / 6 + t * 0.4
            d.line((cx + (R + 12) * math.cos(a), cy + (R + 12) * math.sin(a),
                    cx + (R + 38) * math.cos(a), cy + (R + 38) * math.sin(a)), fill=GOLD, width=8)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=GOLD, outline=OL, width=5)

def waves(d, x0, x1, y, t, col=SEA, rows=3, amp=8):
    for k in range(rows):
        yy = y + k * 34
        pts = [(x, yy + amp * math.sin(x / 38.0 + t * 2.2 + k * 1.3)) for x in range(int(x0), int(x1) + 1, 10)]
        d.line(pts, fill=col if k % 2 == 0 else SEAD, width=7, joint='curve')

def drop(d, x, y, s=1.0, col=BLUE):
    d.polygon([(x, y - 30 * s), (x - 17 * s, y + 4 * s), (x + 17 * s, y + 4 * s)], fill=col, outline=OL)
    d.ellipse((x - 17 * s, y - 12 * s, x + 17 * s, y + 22 * s), fill=col, outline=OL, width=3)
    d.polygon([(x - 8 * s, y - 14 * s), (x + 8 * s, y - 14 * s), (x, y - 30 * s)], fill=col)

def spool(d, cx, cy, R, col=GOLD):
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=col, outline=OL, width=5)
    for k in (0.78, 0.58):
        d.ellipse((cx - R * k, cy - R * k, cx + R * k, cy + R * k), outline=OL, width=2)
    d.ellipse((cx - R * 0.36, cy - R * 0.36, cx + R * 0.36, cy + R * 0.36), fill=CREAM, outline=OL, width=5)
    d.ellipse((cx - R * 0.12, cy - R * 0.12, cx + R * 0.12, cy + R * 0.12), fill=OL)

def printer(d, cx, yb, s=1.0, t=0.0, cover=0.0, rust=False):
    d.rounded_rectangle((cx - 190 * s, yb - 34 * s, cx + 190 * s, yb), radius=int(8 * s), fill=CHAR, outline=OL, width=3)
    for sx in (-1, 1):
        d.rectangle((cx + sx * 170 * s - 14 * s, yb - 330 * s, cx + sx * 170 * s + 14 * s, yb - 34 * s), fill=METAL, outline=OL, width=3)
    d.rounded_rectangle((cx - 190 * s, yb - 350 * s, cx + 190 * s, yb - 318 * s), radius=int(8 * s), fill=CHAR, outline=OL, width=3)
    d.rectangle((cx - 160 * s, yb - 230 * s, cx + 160 * s, yb - 210 * s), fill=GOLD, outline=OL, width=3)
    hx = cx + 70 * s * math.sin(t * 2.0)
    d.rounded_rectangle((hx - 36 * s, yb - 262 * s, hx + 36 * s, yb - 212 * s), radius=int(8 * s), fill=CHAR, outline=OL, width=3)
    d.polygon([(hx - 20 * s, yb - 212 * s), (hx + 20 * s, yb - 212 * s), (hx + 4 * s, yb - 170 * s), (hx - 4 * s, yb - 170 * s)], fill=GOLD, outline=OL)
    d.rectangle((cx - 130 * s, yb - 74 * s, cx + 130 * s, yb - 50 * s), fill=(206, 200, 190), outline=OL, width=3)
    d.rectangle((cx - 60 * s, yb - 130 * s, cx + 60 * s, yb - 74 * s), fill=GOLD, outline=OL, width=3)
    if rust:
        for dx, dy in ((-170, -200), (170, -120), (-170, -90), (170, -260), (-60, -334)):
            d.ellipse((cx + dx * s - 11 * s, yb + dy * s - 11 * s, cx + dx * s + 11 * s, yb + dy * s + 11 * s), fill=RUST)
    if cover > 0.02:
        top = yb - 350 * s * cover - 20 * s
        d.polygon([(cx - 215 * s, yb + 6 * s), (cx - 195 * s, top + 30 * s), (cx - 120 * s, top), (cx + 120 * s, top),
                   (cx + 195 * s, top + 30 * s), (cx + 215 * s, yb + 6 * s)], fill=(222, 120, 100), outline=OL)
        for k in range(1, 5):
            d.line((cx - 200 * s + k * 80 * s, top + 8 * s, cx - 205 * s + k * 82 * s, yb), fill=(196, 92, 76), width=3)

def kettlebell(d, cx, cy, s=1.0, col=CHAR, hl=True):
    for wd, c in ((int(46 * s), OL), (int(34 * s), col)):
        rx, ry = 92 * s + wd / 2, 62 * s + wd / 2
        d.arc((cx - rx, cy - 74 * s - ry, cx + rx, cy - 74 * s + ry), 180, 360, fill=c, width=wd)
        d.line((cx - 92 * s, cy - 74 * s, cx - 92 * s, cy - 20 * s), fill=c, width=wd)
        d.line((cx + 92 * s, cy - 74 * s, cx + 92 * s, cy - 20 * s), fill=c, width=wd)
    d.ellipse((cx - 128 * s, cy - 62 * s, cx + 128 * s, cy + 150 * s), fill=col, outline=OL, width=5)
    d.rectangle((cx - 74 * s, cy + 138 * s, cx + 74 * s, cy + 156 * s), fill=col, outline=OL, width=4)
    if hl:
        d.arc((cx - 96 * s, cy - 36 * s, cx + 20 * s, cy + 60 * s), 200, 270, fill=(120, 120, 130), width=max(3, int(8 * s)))

def ring(d, cx, cy, R, s=1.0):
    R = R * s
    if R < 4:
        return
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=OL, width=int(R * 0.5) + 6)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=GOLD, width=int(R * 0.5))
    d.polygon([(cx, cy - R * 1.9), (cx - R * 0.45, cy - R * 1.35), (cx, cy - R * 0.95), (cx + R * 0.45, cy - R * 1.35)],
              fill=(150, 210, 240), outline=OL)

def chain(d, cx, cy, w, s=1.0):
    if s < 0.05:
        return
    pts = [(cx - w / 2 + w * u / 24, cy + 110 * s * math.sin(math.pi * u / 24)) for u in range(25)]
    d.line(pts, fill=OL, width=int(11 * s) + 4)
    d.line(pts, fill=GOLD, width=int(11 * s))
    for k in range(1, 24, 2):
        x, y = pts[k]
        d.ellipse((x - 9 * s, y - 9 * s, x + 9 * s, y + 9 * s), outline=OL, width=2)
    px, py = pts[12]
    d.ellipse((px - 22 * s, py + 6 * s, px + 22 * s, py + 50 * s), fill=GOLD, outline=OL, width=4)

def bolt(d, cx, cy, s=1.0, col=GOLD):
    pts = [(0, -90), (-46, 6), (-6, 6), (-26, 90), (48, -18), (6, -18), (30, -90)]
    d.polygon([(cx + x * s, cy + y * s) for x, y in pts], fill=col, outline=OL)

def gift(d, cx, cy, s=1.0):
    d.rectangle((cx - 110 * s, cy - 20 * s, cx + 110 * s, cy + 120 * s), fill=(214, 90, 90), outline=OL, width=5)
    d.rectangle((cx - 124 * s, cy - 56 * s, cx + 124 * s, cy - 6 * s), fill=(230, 110, 110), outline=OL, width=5)
    d.rectangle((cx - 18 * s, cy - 56 * s, cx + 18 * s, cy + 120 * s), fill=GOLD, outline=OL, width=4)
    d.ellipse((cx - 70 * s, cy - 118 * s, cx - 4 * s, cy - 54 * s), outline=OL, width=7)
    d.ellipse((cx + 4 * s, cy - 118 * s, cx + 70 * s, cy - 54 * s), outline=OL, width=7)

def photo_card(img, d, crop, box, s=1.0, ol=OL):
    """Cola um recorte da foto real do produto, com cantos arredondados, no retângulo box."""
    if s < 0.05:
        return
    x0, y0, x1, y1 = box
    w, h = int((x1 - x0) * s), int((y1 - y0) * s)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    im = PHOTO.crop(crop).resize((x1 - x0, y1 - y0), Image.LANCZOS).convert('RGBA')
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=26, fill=255)
    im.putalpha(m)
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=26, outline=ol, width=6)
    if s < 0.999:
        im = im.resize((max(1, w), max(1, h)), Image.LANCZOS)
    img.paste(im, (cx - im.width // 2, cy - im.height // 2), im)


# ---------------------------------------------------------------- janela
SX0, SX1 = 70, 1010
SY0, SY1 = 390, 1080
TB = 62
CY0 = SY0 + TB
CH = SY1 - CY0          # altura útil da cena
CX = 540

def Y(v):
    return CY0 + v

def window(img, i):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((SX0 + 10, SY0 + 12, SX1 + 10, SY1 + 12), radius=28, fill=(214, 206, 192))
    rr(d, (SX0, SY0, SX1, SY1), 28, (253, 251, 247), OL, 5)
    d.rounded_rectangle((SX0, SY0, SX1, SY0 + TB), radius=28, fill=CHAR)
    d.rectangle((SX0, SY0 + 34, SX1, SY0 + TB), fill=CHAR)
    for k, col in enumerate((GOLD, GOLDL, WHITE)):
        d.ellipse((SX0 + 30 + k * 32 - 9, SY0 + 31 - 9, SX0 + 30 + k * 32 + 9, SY0 + 31 + 9), fill=col)
    ttl = CFG['titles'][i]
    size = 34 if len(ttl) < 24 else 30
    T(d, 580, SY0 + 31, ttl, size, GOLD if i in (0, N - 1) else WHITE)
    return d

def foot(d, txt='ilustração'):
    T(d, SX1 - 24, SY1 - 20, txt, 20, GRAY, 'rm', FM)


# ---------------------------------------------------------------- cenas (todas ilustrações)
def oven(d, cx, cy, s=1.0, glow=0.0, spool_in=True, t=0.0):
    w, h = 400 * s, 330 * s
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=int(22 * s), fill=METAL, outline=OL, width=5)
    d.rectangle((cx - w / 2 + 16 * s, cy - h / 2 + 16 * s, cx + w / 2 - 16 * s, cy - h / 2 + 62 * s), fill=CHAR, outline=OL, width=3)
    for k in range(4):
        kx = cx - 120 * s + k * 80 * s
        d.ellipse((kx - 17 * s, cy - h / 2 + 39 * s - 17 * s, kx + 17 * s, cy - h / 2 + 39 * s + 17 * s), fill=GOLD if k == 1 else (90, 90, 96), outline=OL, width=3)
    gx0, gy0, gx1, gy1 = cx - w / 2 + 34 * s, cy - h / 2 + 84 * s, cx + w / 2 - 34 * s, cy + h / 2 - 30 * s
    col = (int(60 + 180 * glow), int(52 + 70 * glow), 46)
    d.rounded_rectangle((gx0, gy0, gx1, gy1), radius=int(12 * s), fill=col, outline=OL, width=4)
    if glow > 0.05:
        for k in range(3):
            yy = gy1 - 18 * s - k * 10 * s
            d.line((gx0 + 20 * s, yy, gx1 - 20 * s, yy), fill=(255, 190, 90), width=max(2, int(4 * s)))
    if spool_in:
        spool(d, (gx0 + gx1) / 2, (gy0 + gy1) / 2 + 6 * s, int(70 * s))

def thermometer(d, cx, cy, s=1.0, level=0.5, col=RED):
    d.rounded_rectangle((cx - 22 * s, cy - 150 * s, cx + 22 * s, cy + 90 * s), radius=int(22 * s), fill=WHITE, outline=OL, width=5)
    d.ellipse((cx - 44 * s, cy + 56 * s, cx + 44 * s, cy + 144 * s), fill=col, outline=OL, width=5)
    top = cy + 70 * s - (210 * s) * level
    d.rounded_rectangle((cx - 9 * s, top, cx + 9 * s, cy + 90 * s), radius=int(8 * s), fill=col)
    for k in range(6):
        yy = cy - 120 * s + k * 34 * s
        d.line((cx + 22 * s, yy, cx + 40 * s, yy), fill=OL, width=3)

def melted(d, cx, cy, s=1.0):
    pts = [(cx - 120 * s, cy + 50 * s), (cx - 100 * s, cy - 30 * s), (cx - 40 * s, cy - 60 * s), (cx + 30 * s, cy - 40 * s),
           (cx + 110 * s, cy - 10 * s), (cx + 140 * s, cy + 50 * s), (cx + 60 * s, cy + 70 * s), (cx - 20 * s, cy + 56 * s)]
    d.polygon(pts, fill=GOLD, outline=OL)
    d.line(pts + [pts[0]], fill=OL, width=4)
    d.ellipse((cx - 26 * s, cy - 14 * s, cx + 26 * s, cy + 22 * s), fill=CREAM, outline=OL, width=4)

def microwave(d, cx, cy, s=1.0, t=0.0, hot=False):
    w, h = 460 * s, 300 * s
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=int(20 * s), fill=(226, 224, 220), outline=OL, width=5)
    d.rounded_rectangle((cx - w / 2 + 24 * s, cy - h / 2 + 24 * s, cx + w / 2 - 150 * s, cy + h / 2 - 24 * s), radius=int(14 * s), fill=(54, 58, 66), outline=OL, width=4)
    px = cx - w / 2 + 24 * s + (w - 174 * s) / 2
    spool(d, px, cy + 6 * s, int(66 * s))
    if hot:
        for k, (ox, oy) in enumerate(((-46, -30), (40, 18))):
            r = (18 + 6 * math.sin(t * 6 + k)) * s
            d.ellipse((px + ox * s - r, cy + oy * s - r, px + ox * s + r, cy + oy * s + r), fill=RED)
    bx = cx + w / 2 - 78 * s
    d.rectangle((bx - 40 * s, cy - h / 2 + 28 * s, bx + 40 * s, cy - h / 2 + 76 * s), fill=CHAR, outline=OL, width=3)
    for k in range(3):
        d.ellipse((bx - 20 * s, cy - 10 * s + k * 52 * s - 16 * s, bx + 20 * s, cy - 10 * s + k * 52 * s + 16 * s), fill=(90, 90, 96), outline=OL, width=3)

def box_closed(d, cx, cy, s=1.0, bag=False, tint=(206, 232, 244)):
    w, h = 420 * s, 280 * s
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=int(20 * s), fill=tint, outline=OL, width=5)
    d.rounded_rectangle((cx - w / 2 - 12 * s, cy - h / 2 - 34 * s, cx + w / 2 + 12 * s, cy - h / 2 + 6 * s), radius=int(14 * s), fill=BLUE, outline=OL, width=5)
    for sx in (-1, 1):
        d.rectangle((cx + sx * 120 * s - 14 * s, cy - h / 2 - 14 * s, cx + sx * 120 * s + 14 * s, cy - h / 2 + 2 * s), fill=GOLD, outline=OL, width=3)
    spool(d, cx - 60 * s, cy + 18 * s, int(82 * s))
    if bag:
        d.rounded_rectangle((cx + 70 * s, cy - 10 * s, cx + 170 * s, cy + 90 * s), radius=int(10 * s), fill=WHITE, outline=OL, width=4)
        for k in range(6):
            d.ellipse((cx + 86 * s + (k % 3) * 28 * s, cy + 6 * s + (k // 3) * 36 * s, cx + 102 * s + (k % 3) * 28 * s, cy + 22 * s + (k // 3) * 36 * s), fill=(150, 150, 160))
        T(d, cx + 120 * s, cy + 100 * s + 14 * s, 'SÍLICA', max(10, int(20 * s)), OL)

def s_hook(img, d, t, r, Dd):
    spool(d, 300, Y(250), 140)
    for k in range(4):
        drop(d, 190 + k * 70, Y(60 + 90 * ((t * 0.9 + k * 0.27) % 1.0)), 0.7, BLUE)
    # bico estalando
    nx = 700
    d.rounded_rectangle((nx - 40, Y(150), nx + 40, Y(215)), radius=10, fill=CHAR, outline=OL, width=4)
    d.polygon([(nx - 22, Y(215)), (nx + 22, Y(215)), (nx + 6, Y(262)), (nx - 6, Y(262))], fill=GOLD, outline=OL)
    if int(t * 7) % 2 == 0 or r < 0.3:
        for k, (dx, dy) in enumerate(((-50, 40), (44, 52), (-26, 80), (30, 20))):
            d.line((nx + dx, Y(250) + dy, nx + dx * 1.4, Y(250) + dy * 1.25 + 10), fill=GOLD, width=6)
    chip(d, 540, Y(450), 'FILAMENTO ESTALANDO', 34, fill=RED, fg=WHITE, s=pop(r, 0.4))
    # estufa riscada
    if r > Dd * 0.55:
        u = pop(r, Dd * 0.55)
        chip(d, 540, Y(535), 'SECAR SEM ESTUFA', 32, fill=GOLD, fg=OL, s=u)
    foot(d)

def s_forno(img, d, t, r, Dd):
    glow = clamp(r / 3.0)
    oven(d, 330, Y(270), 1.0, glow, True, t)
    chip(d, 330, Y(485), 'FORNO · TEMPERATURA BAIXA', 28, s=pop(r, 0.5))
    # termometro baixo -> pla
    s = pop(r, 1.5)
    if s > 0.05:
        thermometer(d, 770, Y(220), 1.0, 0.28, GOLD)
        chip(d, 770, Y(420), 'PLA AMOLECE CEDO', 26, fill=RED, fg=WHITE, s=pop(r, 4.5))
        chip(d, 770, Y(490), 'POR VÁRIAS HORAS', 26, s=pop(r, 7.0))
    foot(d)

def s_perigo(img, d, t, r, Dd):
    oven(d, 290, Y(250), 0.78, 0.7, False, t)
    if r < Dd * 0.35:
        melted(d, 290, Y(262), 0.62)
    else:
        spool(d, 290, Y(262), 54)
    chip(d, 290, Y(450), 'FORNO ERRA A TEMPERATURA', 22, fill=RED, fg=WHITE, s=pop(r, 0.4))
    thermometer(d, 700, Y(210), 1.1, 0.5 + 0.03 * math.sin(t * 3), RED if r < Dd * 0.45 else (72, 150, 88))
    chip(d, 700, Y(430), 'TERMÔMETRO DE FORNO', 28, s=pop(r, Dd * 0.4))
    badge_ok(d, 700, Y(520), 34, pop(r, Dd * 0.72))
    chip(d, 860, Y(520), 'ESPERA ESTABILIZAR', 22, s=pop(r, Dd * 0.72))
    foot(d)

def s_micro(img, d, t, r, Dd):
    microwave(d, 400, Y(260), 1.05, t, hot=True)
    badge_no(d, 790, Y(250), 110, pop(r, 1.2))
    chip(d, 400, Y(470), 'ESQUENTA DESIGUAL', 30, fill=RED, fg=WHITE, s=pop(r, 2.2))
    chip(d, 790, Y(430), 'MICRO-ONDAS', 28, fill=CHAR, fg=GOLDL, s=pop(r, 0.4))
    foot(d)

def s_cama(img, d, t, r, Dd):
    # cama aquecida com caixa por cima (corte lateral)
    d.rounded_rectangle((120, Y(380), 860, Y(420)), radius=10, fill=CHAR, outline=OL, width=4)
    d.rectangle((140, Y(340), 840, Y(380)), fill=(206, 200, 190), outline=OL, width=4)
    for k in range(6):
        x = 220 + k * 110
        a = (t * 0.8 + k * 0.17) % 1.0
        d.line((x, Y(330 - 90 * a), x, Y(300 - 90 * a)), fill=RED, width=5)
    box = (200, Y(110), 780, Y(340))
    d.rounded_rectangle(box, radius=18, fill=(214, 236, 246), outline=OL, width=5)
    spool(d, 380, Y(250), 70)
    spool(d, 560, Y(250), 70)
    chip(d, 490, Y(60), 'CAIXA POR CIMA DA CAMA', 28, s=pop(r, 0.4))
    chip(d, 490, Y(485), 'MAIS LENTO · COM CUIDADO', 28, fill=RED, fg=WHITE, s=pop(r, Dd * 0.5))
    foot(d)

def s_guarda(img, d, t, r, Dd):
    box_closed(d, 330, Y(270), 1.0, True)
    chip(d, 330, Y(480), 'CAIXA FECHADA + SÍLICA', 28, s=pop(r, 0.8))
    badge_ok(d, 790, Y(190), 60, pop(r, 1.6))
    chip(d, 790, Y(320), 'SALVA', 34, fill=GOLD, fg=OL, s=pop(r, 3.4))
    s2 = pop(r, 5.0)
    if s2 > 0.05:
        x, y = 790, Y(450)
        d.polygon([(x - 70 * s2, y - 24 * s2), (x + 70 * s2, y - 70 * s2), (x + 24 * s2, y + 70 * s2), (x + 8 * s2, y + 16 * s2)], fill=BLUE, outline=OL)
    foot(d)

SCENES = [s_hook, s_forno, s_perigo, s_micro, s_cama, s_guarda]


# ---------------------------------------------------------------- legenda grande
SUB_SIZE, SUB_LH, SUB_MAXW = 62, 82, 940
SUB_Y0 = 1135

def split_chunks(txt):
    parts, cur = [], ''
    for w in txt.split(' '):
        cur = (cur + ' ' + w).strip()
        if w[-1:] in '.?!:' or (len(cur) > 46 and w[-1:] == ','):
            parts.append(cur)
            cur = ''
    if cur:
        parts.append(cur)
    out, buf = [], ''
    for p in parts:      # junta pedaços curtos
        if buf and len(buf) + len(p) < 42:
            buf += ' ' + p
        elif buf:
            out.append(buf)
            buf = p
        else:
            buf = p
    if buf:
        out.append(buf)
    return out

CHUNKS = []
for a in AUD:
    ch = split_chunks(a['txt'])
    tot = sum(len(c) for c in ch)
    acc, spans = 0, []
    for c in ch:
        spans.append((acc / tot, (acc + len(c)) / tot, c))
        acc += len(c)
    CHUNKS.append(spans)

def is_emph(w):
    return ''.join(c for c in w.lower() if c.isalnum() or c in '-ç').strip('-') in CFG['emph']

def draw_sub(img, i, t):
    a = AUD[i]
    r = t - P[i]
    frac = clamp(r / max(0.2, a['d']))
    chosen = None
    for f0, f1, c in CHUNKS[i]:
        if frac >= f0 - 0.001:
            chosen = (f0, f1, c)
    if chosen is None:
        return
    f0, f1, c = chosen
    lines = g.wrap(c, SUB_SIZE, SUB_MAXW)
    f = font(FB, SUB_SIZE)
    total = sum(len(l) for l in lines)
    prog = (frac - f0) / max(0.01, (f1 - f0)) * 1.15
    nvis = int(math.ceil(clamp(prog) * total))
    d = ImageDraw.Draw(img)
    hh = len(lines) * SUB_LH
    y0 = SUB_Y0 + 20 + (2 * SUB_LH - hh) // 2 if hh < 2 * SUB_LH else SUB_Y0 + 20
    k = 0
    for li, line in enumerate(lines):
        wl = f.getlength(' '.join(line))
        x = 540 - wl / 2
        y = y0 + li * SUB_LH + SUB_LH // 2
        for wd in line:
            if k < nvis:
                ww = f.getlength(wd)
                if is_emph(wd):
                    d.rounded_rectangle((x - 8, y - 37, x + ww + 8, y + 37), radius=14, fill=GOLDL)
                d.text((x, y), wd, font=f, fill=OL, anchor='lm')
            x += f.getlength(wd + ' ')
            k += 1

# ---------------------------------------------------------------- estado
def scene_index(t):
    k = 0
    for i in range(N):
        if t >= P[i] - 0.05:
            k = i
    return k

def bg(t):
    img = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(img)
    for k in range(0, H + 54, 54):
        y = (k - t * 30) % H
        d.line((0, y, W, y), fill=LINEC, width=2)
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
    d = window(img, i)
    r = t - P[i]
    Dd = AUD[i]['d']
    SCENES[i](img, d, t, r, Dd)
    logo_bug(img, 540, 250, 230)
    draw_sub(img, i, t)
    t_end = P[-1] + AUD[-1]['d'] + 0.15
    if t >= t_end:
        sw = t_end + 1.0
        txt, icon = CFG['pill1'] if t < sw else CFG['pill2']
        st = t_end if t < sw else sw
        paste_pop(img, pill(txt, 38 if len(txt) < 26 else 32, WHITE, CHAR, icon), 540, 1560, (t - st) / 0.28)
    for j in range(1, N):
        c = P[j] - 0.05
        a = max(0.0, 1 - abs(t - c) / 0.08) * 0.9
        if a > 0.01:
            box = (SX0 - 6, SY0 - 6, SX1 + 16, SY1 + 18)
            reg = img.crop(box)
            reg = Image.blend(reg, Image.new('RGB', reg.size, CREAM), a)
            img.paste(reg, box[:2])
    return img

# ---------------------------------------------------------------- execução
def preview():
    moments = []
    for i in range(N):
        moments.append(P[i] + AUD[i]['d'] * 0.45)
        moments.append(P[i] + AUD[i]['d'] * 0.93)
    moments += [CEND - 0.4, CEND + 0.9]
    cols = 6
    rows = (len(moments) + cols - 1) // cols
    sheet = Image.new('RGB', (300 * cols, 533 * rows))
    for k, t in enumerate(moments):
        im = frame(t)
        im.save(f'{OUT}/prev{k + 1:02d}.png')
        sheet.paste(im.resize((300, 533), Image.LANCZOS), (300 * (k % cols), 533 * (k // cols)))
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
    final = f'{OUT}/{CFG["final"]}'
    cmd += ['-filter_complex', ';'.join(fc), '-map', f'{N}:v', '-map', '[aout]',
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', f'{TOTAL:.3f}', final + '.tmp.mp4']
    subprocess.check_call(cmd)
    os.rename(final + '.tmp.mp4', final)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':
        preview()
    elif len(sys.argv) > 1 and sys.argv[1] == 'render':
        render()

