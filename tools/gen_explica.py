"""Vídeo explicativo SEM personagem (formato novo de 21/11/2026).

Só narração (voz da Mari, fora de cena) sobre cenas desenhadas, legenda grande queimada no vídeo
e as pílulas finais. Dois vídeos neste arquivo, escolhidos pelo primeiro argumento:

    python3 -I gen_explica.py tt preview|render   # TikTok: 5 problemas de imprimir na praia
    python3 -I gen_explica.py ig preview|render   # Instagram: kettlebell porta-joias

Para um vídeo novo no mesmo formato: copiar este arquivo, trocar o dicionário em VIDEOS
(áudios, textos, títulos, pílulas, ênfases) e as funções de cena.
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
KEY = sys.argv[1] if len(sys.argv) > 1 else 'tt'

# ---------------------------------------------------------------- conteúdo
TT = dict(
    out='/out17', af='/aud17/fin/', final='mavan_praia_problemas.mp4',
    lines=[
        'Imprimir na praia parece uma boa ideia. Até a impressora sentir o clima.',
        'Problema um: umidade. O filamento absorve água do ar e a peça sai com bolhas, fiapos e acabamento áspero.',
        'Guarda o rolo fechado, com sílica, e seca antes de imprimir se ele já pegou ar.',
        'Problema dois: maresia. O ar salgado enferruja parafuso, eixo e qualquer metal da impressora.',
        'Limpa e lubrifica os eixos como o manual manda, e com mais frequência.',
        'Problema três: areia. Um grão no eixo ou na ventoinha vira barulho e desgaste. Deixa a impressora longe da porta e coberta quando estiver parada.',
        'Problema quatro: calor. O PLA amolece, então peça perto de janela com sol, ou dentro do carro, pode entortar.',
        'Problema cinco: energia oscilando. Queda no meio da impressão pode estragar a peça. Estabilizador ou nobreak ajuda.',
        'Umidade, maresia, areia, calor e energia. Esses são os cinco.',
        'Qual deles já te pegou? Conta nos comentários e salva pra quando for imprimir na praia.',
    ],
    titles=['IMPRIMIR NA PRAIA?', '1 · UMIDADE', 'DICA: ROLO FECHADO + SÍLICA', '2 · MARESIA', 'DICA: LIMPAR E LUBRIFICAR',
            '3 · AREIA', '4 · CALOR', '5 · ENERGIA OSCILANDO', 'OS CINCO PROBLEMAS', 'QUAL JÁ TE PEGOU?'],
    emph={'umidade', 'maresia', 'areia', 'calor', 'energia', 'sílica', 'lubrifica', 'nobreak', 'estabilizador', 'pla',
          'cinco', 'bolhas', 'fiapos', 'enferruja', 'entortar', 'coberta', 'salva', 'comentários'},
    pill1=('COMENTA: QUAL JÁ TE PEGOU?', 'send'), pill2=('SALVA PRA IMPRIMIR NA PRAIA', None),
    hold=1.6, endcard=1.2,
)
IG = dict(
    out='/out18', af='/aud18/fin/', final='mavan_kettlebell_ferias.mp4',
    lines=[
        'Férias não são desculpa pra parar de treinar. Treino na areia, de manhã cedinho.',
        'Só que na hora de treinar, o que você faz com a aliança e a correntinha?',
        'No bolso, elas se perdem. Na bolsa, ficam soltas e se arranham. Na toalha, é só dar bobeira.',
        'A Mavan faz um kettlebell porta-joias, impresso em 3D.',
        'Ele abre com rosca. Dentro, você guarda a aliança e a correntinha.',
        'Por fora, parece só um kettlebell. Isso ajuda a deixar suas joias longe dos olhos, na areia ou no quarto.',
        'E a aliança não arranha, porque não fica no dedo enquanto você puxa peso.',
        'Depois das férias ele continua em casa, organizando suas joias.',
        'E é um ótimo presente pra quem treina.',
        'Manda esse vídeo pra quem treina nas férias. Ou manda um direct pra Mavan com a palavra KETTLEBELL.',
    ],
    titles=['FÉRIAS E TREINO', 'E A ALIANÇA?', 'ONDE DEIXAR AS JOIAS?', 'KETTLEBELL PORTA-JOIAS', 'ABRE COM ROSCA',
            'PARECE SÓ UM KETTLEBELL', 'NÃO ARRANHA A ALIANÇA', 'DEPOIS DAS FÉRIAS', 'PRESENTE PRA QUEM TREINA', 'MANDA PRA QUEM TREINA'],
    emph={'treinar', 'aliança', 'correntinha', 'kettlebell', 'porta-joias', 'rosca', 'arranha', 'joias', 'presente',
          'direct', 'perdem', 'arranham', 'mavan'},
    pill1=('MANDA PRA QUEM TREINA', 'send'), pill2=('DIRECT: KETTLEBELL', 'send'),
    hold=1.6, endcard=1.2,
)
CFG = TT if KEY == 'tt' else IG
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

PHOTO = Image.open(HERE + '/assets/kettlebell_real.jpg').convert('RGB') if KEY == 'ig' else None

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

# ---------------------------------------------------------------- cenas TikTok
def tt_hook(img, d, t, r, Dd):
    d.rectangle((SX0 + 3, Y(0), SX1 - 3, Y(380)), fill=SKY)
    sun(d, 850, Y(110), 62, True, t)
    waves(d, SX0 + 5, SX1 - 5, Y(300), t, rows=2)
    d.rectangle((SX0 + 3, Y(380), SX1 - 3, SY1 - 3), fill=SAND)
    d.line((SX0 + 3, Y(380), SX1 - 3, Y(380)), fill=OL, width=4)
    # guarda-sol
    d.line((250, Y(150), 250, Y(440)), fill=OL, width=8)
    d.pieslice((130, Y(80), 370, Y(260)), 180, 360, fill=(214, 90, 90), outline=OL, width=5)
    printer(d, 600, Y(560), 0.82, t)
    s = pop(r, 2.6)
    for k in range(3):
        drop(d, 700 + k * 52, Y(300 + 14 * math.sin(t * 5 + k)) , 0.7 * s, (150, 200, 235))

def tt_umidade(img, d, t, r, Dd):
    spool(d, 330, Y(260), 150, GOLD)
    # umidade no ar
    for k in range(6):
        u = (t * 0.7 + k * 0.17) % 1.0
        drop(d, 140 + k * 70 + 20 * math.sin(k + t), Y(40 + 330 * u), 0.8, BLUE)
    for k, (txt, y0) in enumerate((('BOLHAS', 120), ('FIAPOS', 250), ('ÁSPERO', 380))):
        s = pop(r, 2.2 + k * 1.3)
        chip(d, 770, Y(y0), txt, 34, fill=CHAR, fg=GOLDL, s=s)
    if r > 1.0:
        T(d, 330, Y(470), 'FILAMENTO ABSORVE ÁGUA', 28, GRAY)

def tt_umidade_dica(img, d, t, r, Dd):
    rr(d, (170, Y(110), 650, Y(430)), 26, (232, 244, 250), OL, 6)
    spool(d, 410, Y(270), 108, GOLD)
    for k, (x, y) in enumerate(((220, 170), (600, 170), (220, 380), (600, 380))):
        s = pop(r, 0.7 + k * 0.3)
        if s > 0.05:
            d.rounded_rectangle((x - 30 * s, y + CY0 - CY0 - 22 * s + 0, x + 30 * s, y + 22 * s), radius=6, fill=WHITE, outline=OL, width=3) if False else None
            d.rounded_rectangle((x - 30 * s, Y(y) - 20 * s, x + 30 * s, Y(y) + 20 * s), radius=6, fill=WHITE, outline=OL, width=3)
            for q in range(4):
                d.ellipse((x - 18 * s + (q % 2) * 20 * s, Y(y) - 12 * s + (q // 2) * 16 * s, x - 10 * s + (q % 2) * 20 * s, Y(y) - 4 * s + (q // 2) * 16 * s), fill=GRAY)
    chip(d, 410, Y(480), 'CAIXA FECHADA', 30, s=pop(r, 0.4))
    chip(d, 800, Y(190), 'SÍLICA', 36, fill=GOLD, fg=OL, s=pop(r, 2.0))
    if r > Dd * 0.55:
        s = pop(r, Dd * 0.55)
        chip(d, 800, Y(330), 'SECA ANTES', 32, s=s)
        badge_ok(d, 800, Y(430), 40, s)

def tt_maresia(img, d, t, r, Dd):
    d.rectangle((SX0 + 3, Y(0), SX1 - 3, Y(250)), fill=SKY)
    waves(d, SX0 + 5, SX1 - 5, Y(170), t, rows=3)
    rod_y = Y(400)
    d.rounded_rectangle((170, rod_y - 26, 910, rod_y + 26), radius=26, fill=METAL, outline=OL, width=5)
    n = int(7 * clamp(r / 3.5))
    for k in range(n):
        x = 220 + k * 105
        d.ellipse((x - 20, rod_y - 18, x + 20, rod_y + 18), fill=RUST, outline=(130, 66, 28), width=2)
    for k in range(3):
        u = (t * 0.5 + k * 0.33) % 1.0
        T(d, 250 + k * 280, Y(260 + 60 * u), 'NaCl', 26, (150, 160, 175))
    for k, txt in enumerate(('PARAFUSO', 'EIXO', 'METAL')):
        chip(d, 250 + k * 290, Y(540), txt, 30, s=pop(r, 2.6 + k * 0.9))

def tt_maresia_dica(img, d, t, r, Dd):
    rod_y = Y(300)
    d.rounded_rectangle((120, rod_y - 26, 960, rod_y + 26), radius=26, fill=METAL, outline=OL, width=5)
    clean = clamp((r - 0.6) / 2.4)
    for k in range(7):
        x = 190 + k * 110
        if x > 120 + 840 * clean:
            d.ellipse((x - 20, rod_y - 18, x + 20, rod_y + 18), fill=RUST, outline=(130, 66, 28), width=2)
    wx = 120 + 840 * clean
    d.rounded_rectangle((wx - 55, rod_y - 70, wx + 55, rod_y + 70), radius=20, fill=(240, 232, 214), outline=OL, width=5)
    s = pop(r, 3.4)
    if s > 0.05:
        d.polygon([(300, Y(110)), (380, Y(110)), (400, Y(170)), (280, Y(170))], fill=GOLD, outline=OL)
        drop(d, 340, Y(210 + 50 * (t * 1.5 % 1)), 0.8 * s, (230, 190, 70))
        T(d, 340, Y(60), 'LUBRIFICAR', 30, OL)
    chip(d, 540, Y(470), 'MAIS VEZES QUE O NORMAL', 30, s=pop(r, 4.6))

def tt_areia(img, d, t, r, Dd):
    split = Dd * 0.6
    d.rectangle((SX0 + 3, Y(470), SX1 - 3, SY1 - 3), fill=SAND)
    d.line((SX0 + 3, Y(470), SX1 - 3, Y(470)), fill=OL, width=4)
    if r < split:
        d.rounded_rectangle((200, Y(190), 880, Y(246)), radius=28, fill=METAL, outline=OL, width=5)
        # ventoinha
        cx, cy = 780, Y(380)
        d.ellipse((cx - 90, cy - 90, cx + 90, cy + 90), fill=(236, 232, 224), outline=OL, width=5)
        for k in range(4):
            a = t * 6 + k * math.pi / 2
            d.polygon([(cx, cy), (cx + 80 * math.cos(a - 0.35), cy + 80 * math.sin(a - 0.35)), (cx + 80 * math.cos(a + 0.35), cy + 80 * math.sin(a + 0.35))], fill=GRAY, outline=OL)
        for k in range(26):
            u = (t * 0.6 + k * 0.077) % 1.0
            x = 160 + (k * 83) % 760 + 30 * math.sin(k + t)
            d.ellipse((x - 4, Y(30 + 380 * u) - 4, x + 4, Y(30 + 380 * u) + 4), fill=(190, 160, 110))
        T(d, 330, Y(380), 'GRÃO NO EIXO', 28, GRAY)
        chip(d, 330, Y(540), 'BARULHO + DESGASTE', 28, s=pop(r, 1.5))
    else:
        u = pop(r, split)
        printer(d, 420, Y(450), 0.9, t, cover=clamp((r - split - 1.0) / 1.2))
        d.rounded_rectangle((760, Y(260), 970, Y(450)), radius=18, fill=(240, 232, 214), outline=OL, width=5)
        T(d, 865, Y(330), 'PORTA', 28, GRAY)
        arrow(d, 760, Y(370), 640, Y(370), RED, 7)
        chip(d, 330, Y(560), 'LONGE DA PORTA', 28, s=u)
        chip(d, 740, Y(560), 'COBERTA', 28, s=pop(r, split + 1.4))

def tt_calor(img, d, t, r, Dd):
    sun(d, 220, Y(110), 76, True, t)
    d.rectangle((SX0 + 3, Y(470), SX1 - 3, SY1 - 3), fill=SANDD)
    # peça PLA que entorta
    bend = sm((r - 1.2) / 3.0)
    base_y = Y(420)
    pts = []
    for k in range(21):
        x = 380 + k * 24
        u = k / 20.0
        y = base_y - 20 + (bend * 120 * u * u)
        pts.append((x, y))
    d.line(pts, fill=OL, width=64)
    d.line(pts, fill=GOLD, width=50)
    d.rectangle((340, base_y - 30, 392, base_y + 60), fill=CHAR)
    # termômetro
    d.rounded_rectangle((120, Y(260), 170, Y(520)), radius=24, fill=WHITE, outline=OL, width=5)
    h = 40 + 190 * sm(r / 3.5)
    d.rounded_rectangle((132, Y(510) - h, 158, Y(510)), radius=12, fill=RED)
    d.ellipse((108, Y(480), 182, Y(554)), fill=RED, outline=OL, width=5)
    chip(d, 720, Y(190), 'PLA AMOLECE', 34, s=pop(r, 1.0))
    chip(d, 640, Y(560), 'JANELA COM SOL · CARRO', 28, s=pop(r, Dd * 0.55))

def tt_energia(img, d, t, r, Dd):
    split = Dd * 0.68
    if r < split:
        d.rectangle((150, Y(430), 560, Y(500)), fill=GOLD, outline=OL, width=4)
        d.rectangle((150, Y(300), 560, Y(430)), fill=(236, 232, 224), outline=OL, width=4)
        for k in range(1, 6):
            d.line((150, Y(430) - k * 22, 560, Y(430) - k * 22), fill=(214, 206, 192), width=2)
        T(d, 355, Y(560), 'PEÇA PELA METADE', 28, RED)
        flick = int(t * 10) % 2
        bolt(d, 780, Y(250), 1.6 if flick else 1.45)
        for k in range(3):
            d.arc((820 + k * 24, Y(160), 920 + k * 24, Y(340)), 300, 60, fill=GOLD, width=5)
        if r > 0.9:
            badge_no(d, 430, Y(260), 52, pop(r, 0.9))
    else:
        u = pop(r, split)
        d.rounded_rectangle((250, Y(200), 830, Y(400)), radius=26, fill=CHAR, outline=OL, width=5)
        bx = 300
        for k in range(4):
            d.rounded_rectangle((bx + k * 90, Y(250), bx + k * 90 + 70, Y(350)), radius=8, fill=GREEN if k < 3 or int(t * 4) % 2 else GREEND, outline=OL, width=3)
        d.rectangle((bx + 4 * 90, Y(285), bx + 4 * 90 + 18, Y(315)), fill=GOLD)
        bolt(d, 540, Y(110), 0.8)
        chip(d, 300, Y(500), 'ESTABILIZADOR', 28, s=u)
        chip(d, 780, Y(500), 'NOBREAK', 28, s=pop(r, split + 0.7))
        badge_ok(d, 540, Y(300), 0.1, 0)

def tt_resumo(img, d, t, r, Dd):
    labels = ['UMIDADE', 'MARESIA', 'AREIA', 'CALOR', 'ENERGIA']
    for k, lab in enumerate(labels):
        s = pop(r, 0.15 + k * Dd * 0.16)
        y = Y(60 + k * 112)
        if s > 0.05:
            R = int(40 * s)
            d.ellipse((190 - R, y - R, 190 + R, y + R), fill=GOLD, outline=OL, width=4)
            if s > 0.7:
                T(d, 190, y + 2, str(k + 1), 40, OL)
            chip(d, 560, y, lab, 40, fill=CHAR, fg=GOLDL, s=s)

def tt_cta(img, d, t, r, Dd):
    s = pop(r, 0.1)
    bw, bh = int(440 * s), int(230 * s)
    if bw > 20:
        cx, cy = 400, Y(250)
        d.rounded_rectangle((cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2), radius=44, fill=WHITE, outline=OL, width=6)
        d.polygon([(cx - 80, cy + bh // 2 - 3), (cx - 20, cy + bh // 2 - 3), (cx - 90, cy + bh // 2 + 56)], fill=WHITE, outline=OL)
        d.rectangle((cx - 76, cy + bh // 2 - 9, cx - 24, cy + bh // 2 - 1), fill=WHITE)
        if s > 0.8:
            T(d, cx, cy, '?', 150, OL)
    s2 = pop(r, 1.4)
    if s2 > 0.05:
        x, y = 800, Y(250)
        d.polygon([(x - 62 * s2, y - 100 * s2), (x + 62 * s2, y - 100 * s2), (x + 62 * s2, y + 100 * s2), (x, y + 56 * s2), (x - 62 * s2, y + 100 * s2)], fill=GOLD, outline=OL)
        T(d, x, Y(420), 'SALVA', 34, OL)

# ---------------------------------------------------------------- cenas Instagram
def ig_hook(img, d, t, r, Dd):
    d.rectangle((SX0 + 3, Y(0), SX1 - 3, Y(330)), fill=(252, 226, 196))
    sun(d, 760, Y(250 - 80 * sm(r / 3.0)), 74, True, t)
    waves(d, SX0 + 5, SX1 - 5, Y(330), t, rows=2)
    d.rectangle((SX0 + 3, Y(400), SX1 - 3, SY1 - 3), fill=SAND)
    d.line((SX0 + 3, Y(400), SX1 - 3, Y(400)), fill=OL, width=4)
    kettlebell(d, 330, Y(380), 1.5, CHAR)
    for k in range(3):
        d.ellipse((700 + k * 70 - 10, Y(520) - 5, 700 + k * 70 + 10, Y(520) + 5), fill=SANDD)
    if r > 2.8:
        chip(d, 540, Y(600), 'TREINO NA AREIA · MANHÃ CEDO', 28, s=pop(r, 2.8))

def ig_pergunta(img, d, t, r, Dd):
    s = pop(r, 0.2)
    ring(d, 330, Y(300), 70, s)
    chain(d, 700, Y(220), 330, s)
    q = pop(r, 1.4)
    if q > 0.05:
        T(d, 540, Y(60), '?', int(130 * q), GRAY)
    if r > 2.2:
        chip(d, 540, Y(560), 'ALIANÇA + CORRENTINHA', 32, s=pop(r, 2.2))

def ig_onde(img, d, t, r, Dd):
    cols = [(210, 'BOLSO', 'SE PERDEM'), (540, 'BOLSA', 'SE ARRANHAM'), (870, 'TOALHA', 'DÁ BOBEIRA')]
    for k, (x, name, bad) in enumerate(cols):
        s = pop(r, 0.2 + k * Dd * 0.29)
        if s < 0.05:
            continue
        if k == 0:     # bolso
            d.polygon([(x - 80 * s, Y(140)), (x + 80 * s, Y(140)), (x + 80 * s, Y(300)), (x, Y(350)), (x - 80 * s, Y(300))], fill=BLUE, outline=OL)
            d.line((x - 80 * s, Y(140), x + 80 * s, Y(140)), fill=OL, width=6)
        elif k == 1:   # bolsa
            d.rounded_rectangle((x - 100 * s, Y(190), x + 100 * s, Y(350)), radius=18, fill=(190, 120, 90), outline=OL, width=5)
            d.arc((x - 60 * s, Y(100), x + 60 * s, Y(250)), 180, 360, fill=OL, width=9)
        else:          # toalha
            d.rounded_rectangle((x - 96 * s, Y(170), x + 96 * s, Y(340)), radius=10, fill=(236, 120, 130), outline=OL, width=5)
            for q in range(3):
                d.line((x - 96 * s, Y(210 + q * 50), x + 96 * s, Y(210 + q * 50)), fill=WHITE, width=10)
        T(d, x, Y(90), name, int(34 * s), OL)
        chip(d, x, Y(430), bad, 24, fill=RED, fg=WHITE, s=s)
        badge_no(d, x, Y(520), 34, s)

def ig_produto(img, d, t, r, Dd):
    s = pop(r, 0.1, 0.4)
    photo_card(img, d, (90, 820, 1390, 1805), (197, Y(14), 883, Y(534)), s)
    chip(d, 540, Y(578), 'IMPRESSO EM 3D · MAVAN', 30, s=pop(r, 0.9))
    foot(d, 'foto real do produto')

def ig_rosca(img, d, t, r, Dd):
    split = Dd * 0.1
    # corte esquemático do kettlebell (ilustração do conceito)
    cx, cy = 400, Y(330)
    open_ = sm((r - 0.5) / 1.4)
    kettlebell(d, cx, cy, 1.35, CHAR, hl=False)
    capy = cy - 150 * 1.35 - 40 * open_ * 1.3
    d.ellipse((cx - 90, cy - 70 * 1.35 - 22 - 60 * open_, cx + 90, cy - 70 * 1.35 + 16 - 60 * open_), fill=GOLD, outline=OL, width=4)
    for k in range(4):
        y = cy - 70 * 1.35 - 12 - 60 * open_ + k * 4
        d.line((cx - 70, y, cx + 70, y), fill=OL, width=2)
    # seta de rosca
    d.arc((cx - 120, cy - 70 * 1.35 - 130 - 60 * open_, cx + 120, cy - 70 * 1.35 - 10 - 60 * open_), 200, 340, fill=RED, width=7)
    ax, ay = cx + 120 * math.cos(math.radians(340)), cy - 70 * 1.35 - 70 - 60 * open_ + 60 * math.sin(math.radians(340))
    if r > Dd * 0.3:
        u = sm((r - Dd * 0.3) / 1.6)
        ring(d, 760, Y(200) + 120 * u, 38)
        chain(d, 760, Y(300) + 40 * u, 200, 0.6)
        T(d, 760, Y(120), 'DENTRO', 28, GRAY)
        arrow(d, 690, Y(220), 560, Y(300), OL, 5)
    chip(d, 540, Y(570), 'ABRE COM ROSCA', 34, s=pop(r, split))
    foot(d, 'ilustração do conceito')

def ig_parece(img, d, t, r, Dd):
    s = pop(r, 0.1, 0.4)
    photo_card(img, d, (725, 820, 1409, 1720), (100, Y(20), 540, Y(600)), s)
    # olho cortado
    e = pop(r, 1.6)
    if e > 0.05:
        cx, cy = 790, Y(180)
        d.ellipse((cx - 90 * e, cy - 52 * e, cx + 90 * e, cy + 52 * e), fill=WHITE, outline=OL, width=6)
        d.ellipse((cx - 30 * e, cy - 30 * e, cx + 30 * e, cy + 30 * e), fill=CHAR)
        d.line((cx - 100 * e, cy + 70 * e, cx + 100 * e, cy - 70 * e), fill=RED, width=10)
    chip(d, 790, Y(320), 'JOIAS FORA DA VISTA', 26, s=pop(r, Dd * 0.45))
    chip(d, 790, Y(420), 'NA AREIA', 30, s=pop(r, Dd * 0.62))
    chip(d, 790, Y(510), 'NO QUARTO', 30, s=pop(r, Dd * 0.75))

def ig_nao_arranha(img, d, t, r, Dd):
    # esquerda: aliança no dedo durante o treino (ruim). direita: guardada
    d.line((540, Y(40), 540, Y(560)), fill=(214, 206, 192), width=4)
    d.rounded_rectangle((170, Y(170), 290, Y(500)), radius=56, fill=(246, 208, 178), outline=OL, width=5)
    d.rounded_rectangle((165, Y(300), 295, Y(344)), radius=20, outline=OL, width=14)
    d.rounded_rectangle((165, Y(300), 295, Y(344)), radius=20, outline=GOLD, width=8)
    d.line((140, Y(250), 200, Y(280)), fill=RED, width=5)
    d.line((300, Y(250), 255, Y(285)), fill=RED, width=5)
    # peso na mão (halter simplificado) para indicar treino
    d.rounded_rectangle((100, Y(100), 360, Y(140)), radius=14, fill=CHAR, outline=OL, width=4)
    chip(d, 230, Y(570), 'NO DEDO', 28, fill=RED, fg=WHITE, s=pop(r, 0.6))
    badge_no(d, 230, Y(60), 34, pop(r, 1.2))
    k = pop(r, Dd * 0.35)
    kettlebell(d, 790, Y(300), 1.1, CHAR)
    if k > 0.05:
        ring(d, 790, Y(330), 34, k)
        badge_ok(d, 790, Y(60), 34, k)
    chip(d, 790, Y(570), 'NO KETTLEBELL', 28, fill=GREEN, fg=WHITE, s=pop(r, Dd * 0.35))

def ig_depois(img, d, t, r, Dd):
    s = pop(r, 0.1, 0.4)
    photo_card(img, d, (90, 820, 1390, 1805), (197, Y(14), 883, Y(534)), s)
    chip(d, 540, Y(578), 'EM CASA, ORGANIZANDO SUAS JOIAS', 28, s=pop(r, 0.9))
    foot(d, 'foto real do produto')

def ig_presente(img, d, t, r, Dd):
    gift(d, 350, Y(300), 1.6 * pop(r, 0.15))
    s = pop(r, 1.0)
    kettlebell(d, 790, Y(300), 1.1 * s, CHAR) if s > 0.05 else None
    if r > 1.6:
        chip(d, 540, Y(560), 'PRESENTE QUE ORGANIZA', 32, s=pop(r, 1.6))

def ig_cta(img, d, t, r, Dd):
    s = pop(r, 0.1)
    cx, cy = 300, Y(260)
    bw, bh = int(400 * s), int(220 * s)
    if bw > 20:
        d.rounded_rectangle((cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2), radius=44, fill=WHITE, outline=OL, width=6)
        if s > 0.8:
            kettlebell(d, cx, cy + 20, 0.8, CHAR)
    s2 = pop(r, 1.3)
    if s2 > 0.05:
        x, y = 790, Y(260)
        d.polygon([(x - 90 * s2, y - 30 * s2), (x + 90 * s2, y - 90 * s2), (x + 30 * s2, y + 90 * s2), (x + 10 * s2, y + 20 * s2)], fill=BLUE, outline=OL)
    if r > 2.4:
        chip(d, 540, Y(520), 'KETTLEBELL', 44, fill=GOLD, fg=OL, s=pop(r, 2.4))

SCENES_TT = [tt_hook, tt_umidade, tt_umidade_dica, tt_maresia, tt_maresia_dica, tt_areia, tt_calor, tt_energia, tt_resumo, tt_cta]
SCENES_IG = [ig_hook, ig_pergunta, ig_onde, ig_produto, ig_rosca, ig_parece, ig_nao_arranha, ig_depois, ig_presente, ig_cta]
SCENES = SCENES_TT if KEY == 'tt' else SCENES_IG

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
    if len(sys.argv) > 2 and sys.argv[2] == 'preview':
        preview()
    elif len(sys.argv) > 2 and sys.argv[2] == 'render':
        render()
