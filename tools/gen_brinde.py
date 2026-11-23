"""Vídeo B de 23/11/2026: brindes úteis (formato explicativo sem personagem, fotos reais do Ivan).

    python3 -I gen_brinde.py preview|render
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
    out='/out19', af='/aud19/fin/', final='mavan_brinde_util.mp4',
    lines=[
        'Seu cliente joga seu brinde no lixo.',
        'Caneta e caderno igual ao de todo mundo ficam na gaveta e somem.',
        'Brinde bom é o que a pessoa usa, e que combina com o negócio dela.',
        'Pra um chef de cozinha, a Mavan fez um ratatouille. Pra um pet shop, uma pazinha de ração.',
        'E pras festas de fim de ano, um marcador de copo com o logo da sua empresa ou com o seu pet estampado.',
        'Marca aqui quem cuida dos brindes da sua empresa. Ou manda um direct pra Mavan com a palavra BRINDE.',
    ],
    titles=['SEU BRINDE VAI PRO LIXO?', 'CANETA E CADERNO?', 'BRINDE QUE A PESSOA USA', 'RATATOUILLE E PAZINHA',
            'MARCADOR DE COPO', 'MARCA QUEM CUIDA DOS BRINDES'],
    emph={'lixo', 'brinde', 'brindes', 'usa', 'negócio', 'ratatouille', 'pazinha', 'marcador', 'copo', 'logo', 'pet',
          'estampado', 'direct', 'gaveta', 'somem', 'chef', 'mavan'},
    pill1=('MARCA QUEM CUIDA DOS BRINDES', 'send'), pill2=('DIRECT: BRINDE', 'send'),
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


# ---------------------------------------------------------------- fotos reais
def load(n):
    return Image.open(HERE + '/assets/brindes/' + n + '.jpg').convert('RGB')
IMG = {k: load(k) for k in ('ratatouille1', 'ratatouille_grupo', 'pazinha_rex', 'pazinha_racao',
                            'marcadores_pet', 'marcador_copo_pacco')}
CLIP = HERE + '/clip23/'

def card(img, src, crop, box, s=1.0, ol=OL):
    """Foto (PIL) recortada em crop, no retângulo box, com cantos arredondados e pop de escala."""
    if s < 0.05:
        return
    x0, y0, x1, y1 = box
    w, h = int((x1 - x0) * s), int((y1 - y0) * s)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    im = src.crop(crop).resize((x1 - x0, y1 - y0), Image.LANCZOS).convert('RGBA')
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=26, fill=255)
    im.putalpha(m)
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=26, outline=ol, width=6)
    if s < 0.999:
        im = im.resize((max(1, w), max(1, h)), Image.LANCZOS)
    img.paste(im, (cx - im.width // 2, cy - im.height // 2), im)

_clip_cache = {}
def clip_frame(t):
    k = int(t * 30) % 321 + 1
    if k not in _clip_cache:
        _clip_cache[k] = Image.open(CLIP + f'f{k:04d}.png').convert('RGB')
    return _clip_cache[k]

# ---------------------------------------------------------------- cenas
def bin_(d, cx, cy, s=1.0, lid=0.0):
    d.polygon([(cx - 90 * s, cy - 70 * s), (cx + 90 * s, cy - 70 * s), (cx + 72 * s, cy + 120 * s), (cx - 72 * s, cy + 120 * s)],
              fill=(150, 160, 170), outline=OL)
    for k in (-40, 0, 40):
        d.line((cx + k * s, cy - 50 * s, cx + k * 0.8 * s, cy + 100 * s), fill=OL, width=4)
    d.rounded_rectangle((cx - 104 * s - 20 * lid, cy - 104 * s - 30 * lid, cx + 104 * s - 20 * lid, cy - 74 * s - 30 * lid),
                        radius=8, fill=(130, 140, 150), outline=OL, width=4)

def s_hook(img, d, t, r, Dd):
    bin_(d, 700, Y(330), 1.7, sm(r / 1.0))
    u = clamp((r - 0.3) / 1.4)
    gx, gy = lerp(300, 690, u), Y(lerp(190, 260, u * u)) - 70 * math.sin(math.pi * u)
    gift(d, gx, gy, 0.9 * (1 - 0.35 * u))
    chip(d, 330, Y(520), 'BRINDE GENÉRICO', 32, fill=RED, fg=WHITE, s=pop(r, 0.9))
    foot(d)

def s_gaveta(img, d, t, r, Dd):
    # gaveta que fecha e some com caneta e caderno
    d.rounded_rectangle((150, Y(230), 930, Y(480)), radius=20, fill=(196, 150, 104), outline=OL, width=6)
    d.rounded_rectangle((420, Y(320), 660, Y(360)), radius=18, fill=(150, 108, 70), outline=OL, width=5)
    out = 1 - sm((r - 1.2) / 1.6)
    # caderno e caneta caindo na gaveta
    ny = Y(20 + 200 * (1 - out) * 0 + 160 * (1 - out)) if out < 1 else Y(20)
    d.rounded_rectangle((250, Y(30 + 150 * (1 - out)), 450, Y(150 + 150 * (1 - out) )), radius=10, fill=(90, 130, 190), outline=OL, width=5)
    d.line((470, Y(40 + 140 * (1 - out)), 560, Y(150 + 140 * (1 - out))), fill=OL, width=16)
    d.line((470, Y(40 + 140 * (1 - out)), 560, Y(150 + 140 * (1 - out))), fill=GOLD, width=9)
    chip(d, 540, Y(560), 'IGUAL AO DE TODO MUNDO', 30, s=pop(r, 0.7))
    if r > 2.4:
        badge_no(d, 840, Y(120), 40, pop(r, 2.4))
    foot(d)

def s_usa(img, d, t, r, Dd):
    chip(d, 540, Y(110), 'A PESSOA USA', 46, fill=GOLD, fg=OL, s=pop(r, 0.3))
    badge_ok(d, 300, Y(300), 70, pop(r, 0.9))
    chip(d, 640, Y(300), 'COMBINA COM O NEGÓCIO', 32, s=pop(r, 2.0))
    chip(d, 540, Y(470), 'BRINDE QUE NÃO VAI PRA GAVETA', 30, s=pop(r, 3.2))
    foot(d)

def s_chef(img, d, t, r, Dd):
    split = Dd * 0.5
    if r < split:
        s = pop(r, 0.05, 0.4)
        card(img, IMG['ratatouille1'], (180, 330, 780, 1060), (80, Y(10), 470, Y(520)), s)
        card(img, IMG['ratatouille_grupo'], (90, 300, 880, 1130), (500, Y(60), 940, Y(480)), pop(r, 0.7, 0.4))
        chip(d, 540, Y(575), 'CHEF DE COZINHA · RATATOUILLE', 28, s=pop(r, 0.6))
    else:
        u = pop(r, split, 0.4)
        card(img, IMG['pazinha_racao'], (0, 100, 640, 1030), (80, Y(10), 440, Y(520)), u)
        card(img, IMG['pazinha_rex'], (60, 250, 840, 1050), (500, Y(70), 940, Y(470)), pop(r, split + 0.7, 0.4))
        chip(d, 540, Y(575), 'PET SHOP · PAZINHA DE RAÇÃO', 28, s=pop(r, split + 0.2))
    foot(d, 'fotos reais dos produtos')

def s_copo(img, d, t, r, Dd):
    s = pop(r, 0.05, 0.4)
    # clipe real do marcador de copo
    fr = clip_frame(r)
    card(img, fr, (0, 130, 478, 740), (80, Y(10), 440, Y(480)), s)
    card(img, IMG['marcador_copo_pacco'], (200, 190, 800, 810), (470, Y(10), 930, Y(480)), pop(r, 0.5, 0.4))
    chip(d, 330, Y(560), 'LOGO DA EMPRESA', 28, s=pop(r, Dd * 0.45))
    chip(d, 740, Y(560), 'SEU PET ESTAMPADO', 28, fill=GOLD, fg=OL, s=pop(r, Dd * 0.72))
    foot(d, 'fotos e vídeo reais do produto')

def s_cta(img, d, t, r, Dd):
    s = pop(r, 0.1)
    cx, cy = 300, Y(260)
    bw, bh = int(400 * s), int(220 * s)
    if bw > 20:
        d.rounded_rectangle((cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2), radius=44, fill=WHITE, outline=OL, width=6)
        if s > 0.8:
            T(d, cx, cy, '@', 120, OL)
    s2 = pop(r, 1.3)
    if s2 > 0.05:
        x, y = 790, Y(260)
        d.polygon([(x - 90 * s2, y - 30 * s2), (x + 90 * s2, y - 90 * s2), (x + 30 * s2, y + 90 * s2), (x + 10 * s2, y + 20 * s2)], fill=BLUE, outline=OL)
    if r > 2.4:
        chip(d, 540, Y(520), 'BRINDE', 48, fill=GOLD, fg=OL, s=pop(r, 2.4))
    foot(d)

SCENES = [s_hook, s_gaveta, s_usa, s_chef, s_copo, s_cta]

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

