import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H, FPS = 1080, 1920, 30
D = HERE
OUT = D + '/out4'
os.makedirs(OUT, exist_ok=True)
LOGO_PATH = HERE + '/assets/logo.jpg'
FD = '/usr/share/fonts/truetype/google-fonts/'
FB = FD + 'Poppins-ExtraBold.ttf' if os.path.exists(FD + 'Poppins-ExtraBold.ttf') else FD + 'Poppins-Bold.ttf'
FM = FD + 'Poppins-Medium.ttf' if os.path.exists(FD + 'Poppins-Medium.ttf') else FD + 'Poppins-Bold.ttf'

# Mavan identity: charcoal on cream, thin line-art, a gold accent for "value"
CREAM = (248, 245, 239)
CHAR = (38, 36, 40)
OL = CHAR
GOLD = (236, 176, 62)
GOLDL = (255, 226, 150)
WARM = (226, 219, 207)
LINEC = (233, 227, 217)
GRAY = (128, 122, 118)
RED = (214, 64, 64)
WHITE = (255, 255, 255)

LINES = [
    ('633c0a6f-01-cliente.mp3', 'cliente', 'Ué... você imprime em 3D? Deve tá rico, hein?'),
    ('238095e8-02-sofia.mp3', 'mari', 'Rico? Senta aqui que eu te mostro a conta.'),
    ('d404e46a-Sofia_explicando.mp3', 'mari', 'Filamento caro... conta de luz... peça que falha...'),
    ('03a22d49-04-cliente.mp3', 'cliente', 'Mas o guru falou que era só ligar e faturar!'),
    ('61d4daf0-05-sofia.mp3', 'mari', 'Mentira. Quem lucra vende DESIGN, NICHO e MARCA. Não hora de máquina.'),
    ('4bd53f2e-06-sofia.mp3', 'mari', 'Concorda ou tá com raiva? Comenta EU se já perdeu filamento à toa.'),
]
LEAD, GAP, HOLD, ENDCARD = 0.25, 0.35, 1.7, 1.4
SR = 22050

# ---------------------------------------------------------------- audio analysis
def analyse(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    n = SR // FPS
    k = len(x) // n
    rms = np.sqrt((x[:k * n].reshape(k, n) ** 2).mean(1))
    thr = 0.05 * rms.max()
    idx = np.where(rms > thr)[0]
    s = max(0.0, idx[0] / FPS - 0.05)
    e = min(len(x) / SR, (idx[-1] + 1) / FPS + 0.15)
    env = rms[int(s * FPS):int(e * FPS) + 1]
    ref = np.percentile(rms[rms > thr], 90)
    return s, e, np.clip(env / ref, 0, 1.3)

A = os.environ.get('MAVAN_SKIT_AUDIO', HERE + '/aud_skit/')  # só o vídeo-esquete antigo usa isto
if all(os.path.exists(A + fn) for fn, _, _ in LINES):
    AUD = []
    for fn, spk, txt in LINES:
        s, e, env = analyse(A + fn)
        AUD.append(dict(file=A + fn, spk=spk, txt=txt, s=s, e=e, d=e - s, env=env))
    P = []
    tcur = LEAD
    for a in AUD:
        P.append(tcur)
        tcur += a['d'] + GAP

    # scene cuts
    C1 = P[2] - 0.05      # wide -> close A
    C2 = P[3] - 0.05      # close A -> wide
    C3 = P[4] - 0.05      # wide -> close B
    C4 = P[5] - 0.05      # close B -> wide CTA
    C5 = P[5] + AUD[5]['d'] + HOLD   # wide -> end card
    TOTAL = C5 + ENDCARD

else:  # áudios do esquete ausentes: os geradores novos importam apenas os utilitários deste arquivo
    AUD = [dict(d=1.0)] * len(LINES)
    P = [0.0] * len(LINES)
    C1 = C2 = C3 = C4 = C5 = 0.0
    TOTAL = 1.0

# ---------------------------------------------------------------- helpers
_c = {}
def font(path, size):
    k = (path, size)
    if k not in _c:
        _c[k] = ImageFont.truetype(path, size)
    return _c[k]

def tl(txt, size, color, fpath=None):
    key = ('tl', txt, size, color, fpath)
    if key in _c:
        return _c[key]
    f = font(fpath or FB, size)
    w = int(f.getlength(txt)) + 60
    h = int(size * 1.7)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((w // 2, h // 2), txt, font=f, fill=color + (255,), anchor='mm')
    _c[key] = im
    return im

def eob(x):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def paste_pop(img, layer, cx, cy, p, alpha=1.0):
    if p <= 0 or alpha <= 0:
        return
    p = min(1.0, p)
    s = 0.55 + 0.45 * eob(p)
    a = min(1.0, p * 3) * alpha
    lw, lh = max(1, int(layer.width * s)), max(1, int(layer.height * s))
    l2 = layer.resize((lw, lh), Image.LANCZOS) if abs(s - 1) > 0.01 else layer.copy()
    l2.putalpha(l2.getchannel('A').point(lambda v: int(v * a)))
    img.paste(l2, (int(cx - lw / 2), int(cy - lh / 2)), l2)

def put(img, txt, size, color, cx, cy, t, start, fpath=None, alpha=1.0):
    paste_pop(img, tl(txt, size, color, fpath), cx, cy, (t - start) / 0.25, alpha)

# ---------------------------------------------------------------- logo
def load_logo():
    g = np.asarray(Image.open(LOGO_PATH).convert('L')).astype(np.float32)
    alpha = np.clip((235 - g) / (235 - 70), 0, 1)
    ys, xs = np.where(alpha > 0.08)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    alpha = alpha[y0:y1, x0:x1]
    rgba = np.zeros(alpha.shape + (4,), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = CHAR
    rgba[..., 3] = (alpha * 255).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')

LOGO = load_logo()
def logo_w(width):
    k = ('logo', width)
    if k not in _c:
        _c[k] = LOGO.resize((width, int(LOGO.height * width / LOGO.width)), Image.LANCZOS)
    return _c[k]

# ---------------------------------------------------------------- icons and pills
def heart_pts(cx, cy, s, n=48):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * s / 16.0, cy + y * s / 16.0))
    return pts

def draw_icon(d, name, cx, cy, s):
    if name == 'spool':
        d.ellipse((cx - s, cy - s, cx + s, cy + s), fill=GOLD, outline=OL, width=4)
        d.ellipse((cx - s * .35, cy - s * .35, cx + s * .35, cy + s * .35), fill=WHITE, outline=OL, width=3)
        for a in (0, 2.09, 4.19):
            d.line((cx + s * .35 * math.cos(a), cy + s * .35 * math.sin(a), cx + s * .9 * math.cos(a), cy + s * .9 * math.sin(a)), fill=OL, width=3)
    elif name == 'bulb':
        d.ellipse((cx - s * .8, cy - s, cx + s * .8, cy + s * .55), fill=GOLDL, outline=OL, width=4)
        d.rectangle((cx - s * .35, cy + s * .5, cx + s * .35, cy + s * .95), fill=WARM, outline=OL, width=3)
        d.line((cx - s * .3, cy + s * .1, cx, cy - s * .2, cx + s * .3, cy + s * .1), fill=OL, width=3)
    elif name == 'warn':
        d.polygon([(cx, cy - s), (cx + s, cy + s * .8), (cx - s, cy + s * .8)], fill=GOLDL, outline=OL)
        d.line((cx, cy - s * .35, cx, cy + s * .25), fill=OL, width=5)
        d.ellipse((cx - 3, cy + s * .42, cx + 3, cy + s * .42 + 6), fill=OL)
    elif name == 'pencil':
        d.line((cx - s * .8, cy + s * .8, cx + s * .5, cy - s * .5), fill=OL, width=17)
        d.line((cx - s * .8, cy + s * .8, cx + s * .5, cy - s * .5), fill=GOLD, width=9)
        d.polygon([(cx - s, cy + s), (cx - s * .6, cy + s * .55), (cx - s * .45, cy + s * .9)], fill=OL)
    elif name == 'target':
        d.ellipse((cx - s, cy - s, cx + s, cy + s), fill=WHITE, outline=OL, width=4)
        d.ellipse((cx - s * .6, cy - s * .6, cx + s * .6, cy + s * .6), fill=GOLD, outline=OL, width=3)
        d.ellipse((cx - s * .22, cy - s * .22, cx + s * .22, cy + s * .22), fill=OL)
    elif name == 'send':
        d.polygon([(cx - s, cy - s * 0.15), (cx + s, cy - s), (cx + s * 0.25, cy + s), (cx - s * 0.05, cy + s * 0.2)], fill=WHITE, outline=OL)
        d.line((cx - s * 0.05, cy + s * 0.2, cx + s, cy - s), fill=OL, width=3)
    elif name == 'heart':
        d.polygon(heart_pts(cx, cy, s * 1.9), fill=(255, 110, 124), outline=OL)

def pill(txt, size, fg, bg, icon=None):
    key = ('pill', txt, size, fg, bg, icon)
    if key in _c:
        return _c[key]
    f = font(FB, size)
    tw = int(f.getlength(txt))
    pad = 40
    iw = 80 if icon else 0
    w = tw + pad * 2 + iw
    h = int(size * 1.95)
    im = Image.new('RGBA', (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 10 + w, 10 + h), radius=h // 2, fill=bg, outline=OL, width=5)
    if icon:
        draw_icon(d, icon, 10 + pad + 26, 10 + h // 2, 26)
    d.text((10 + pad + iw, 10 + h // 2), txt, font=f, fill=fg, anchor='lm')
    _c[key] = im
    return im

def rot(layer, ang):
    k = ('rot', id(layer), round(ang, 1))
    if k not in _c:
        _c[k] = layer.rotate(ang, expand=True, resample=Image.BICUBIC)
    return _c[k]

# ---------------------------------------------------------------- value items (coins, tag, gem, crown, sparkle)
def sparkle_layer(size, color):
    key = ('sp', size, color)
    if key in _c:
        return _c[key]
    S2 = 3
    n = size * S2
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = n / 2
    pts = []
    for i in range(8):
        r = c * 0.96 if i % 2 == 0 else c * 0.26
        a = math.pi / 4 * i - math.pi / 2
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=color, outline=OL)
    _c[key] = im.resize((size, size), Image.LANCZOS)
    return _c[key]

def coin_layer(r):
    key = ('coin', r)
    if key in _c:
        return _c[key]
    S2 = 3
    n = (2 * r + 16) * S2
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = n / 2
    R = r * S2
    d.ellipse((c - R, c - R, c + R, c + R), fill=GOLD, outline=OL, width=5 * S2 // 2)
    d.ellipse((c - R * .74, c - R * .74, c + R * .74, c + R * .74), fill=GOLDL, outline=OL, width=3 * S2 // 2)
    f = ImageFont.truetype(FB, int(R * 1.0))
    d.text((c, c + R * 0.04), '$', font=f, fill=OL, anchor='mm')
    _c[key] = im.resize((2 * r + 16, 2 * r + 16), Image.LANCZOS)
    return _c[key]

def tag_layer():
    key = ('tag',)
    if key in _c:
        return _c[key]
    S2 = 3
    w, h = 190 * S2, 120 * S2
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(20 * S2, 20 * S2), (130 * S2, 20 * S2), (176 * S2, 60 * S2), (130 * S2, 100 * S2), (20 * S2, 100 * S2)]
    d.polygon(pts, fill=WHITE, outline=OL, width=5 * S2 // 2)
    d.line(pts + [pts[0]], fill=OL, width=5 * S2 // 2, joint='curve')
    d.ellipse((140 * S2, 52 * S2, 156 * S2, 68 * S2), fill=CREAM, outline=OL, width=3 * S2 // 2)
    f = ImageFont.truetype(FB, 44 * S2)
    d.text((72 * S2, 61 * S2), 'R$', font=f, fill=OL, anchor='mm')
    _c[key] = im.resize((190, 120), Image.LANCZOS)
    return _c[key]

def gem_layer():
    key = ('gem',)
    if key in _c:
        return _c[key]
    S2 = 3
    n = 130 * S2
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = S2
    top = [(30 * s, 40 * s), (50 * s, 14 * s), (80 * s, 14 * s), (100 * s, 40 * s)]
    full = top + [(65 * s, 112 * s)]
    d.polygon(full, fill=(190, 228, 246), outline=OL)
    d.line(full + [full[0]], fill=OL, width=5 * s // 2, joint='curve')
    d.line([(30 * s, 40 * s), (100 * s, 40 * s)], fill=OL, width=4 * s // 2)
    d.line([(50 * s, 14 * s), (45 * s, 40 * s), (65 * s, 112 * s)], fill=OL, width=3 * s // 2)
    d.line([(80 * s, 14 * s), (85 * s, 40 * s), (65 * s, 112 * s)], fill=OL, width=3 * s // 2)
    _c[key] = im.resize((130, 130), Image.LANCZOS)
    return _c[key]

def crown_layer():
    key = ('crown',)
    if key in _c:
        return _c[key]
    S2 = 3
    w, h = 170 * S2, 130 * S2
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = S2
    pts = [(20 * s, 100 * s), (14 * s, 36 * s), (54 * s, 66 * s), (85 * s, 16 * s), (116 * s, 66 * s), (156 * s, 36 * s), (150 * s, 100 * s)]
    d.polygon(pts, fill=GOLD, outline=OL)
    d.line(pts + [pts[0]], fill=OL, width=5 * s // 2, joint='curve')
    d.rectangle((20 * s, 100 * s, 150 * s, 114 * s), fill=GOLD, outline=OL, width=4 * s // 2)
    for x in (14, 85, 156):
        yy = 36 if x != 85 else 16
        d.ellipse(((x - 7) * s, (yy - 7) * s, (x + 7) * s, (yy + 7) * s), fill=WHITE, outline=OL, width=3 * s // 2)
    _c[key] = im.resize((170, 130), Image.LANCZOS)
    return _c[key]

def paste_center(img, layer, cx, cy, alpha=1.0):
    if alpha < 1:
        layer = layer.copy()
        layer.putalpha(layer.getchannel('A').point(lambda v: int(v * alpha)))
    img.paste(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)), layer)

def draw_value_items(img, items, t, t0):
    for kind, x, y, sz, ph in items:
        bob = 14 * math.sin((t - t0) * 2.0 + ph)
        ang = 7 * math.sin((t - t0) * 1.4 + ph)
        pop = min(1.0, max(0.0, (t - t0 - 0.12 - ph * 0.08) / 0.3))
        if pop <= 0:
            continue
        s = 0.5 + 0.5 * eob(pop)
        if kind == 'coin':
            base = coin_layer(sz)
            wsc = max(0.12, abs(math.cos((t - t0) * 3.2 + ph)))
            lay = base.resize((max(6, int(base.width * wsc * s)), max(6, int(base.height * s))), Image.LANCZOS)
        else:
            base = {'tag': tag_layer(), 'gem': gem_layer(), 'crown': crown_layer(),
                    'spark': sparkle_layer(sz, GOLDL), 'sparkw': sparkle_layer(sz, WHITE)}[kind]
            lay = base.resize((max(4, int(base.width * s)), max(4, int(base.height * s))), Image.LANCZOS)
            lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC)
        paste_center(img, lay, x, y + bob, alpha=min(1.0, pop * 2))

# ---------------------------------------------------------------- stage drawing (2x supersample, with scale transform)
S = 2

class Stage:
    def __init__(self, w=W, h=800, k=1.0, ox=0.0, oy=0.0):
        self.k, self.ox, self.oy = k, ox, oy
        self.im = Image.new('RGBA', (int(w * S), int(h * S)), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
    def X(self, x): return (x * self.k + self.ox) * S
    def Y(self, y): return (y * self.k + self.oy) * S
    def R(self, r): return r * self.k * S
    def LW(self, w): return max(1, int(round(w * self.k * S)))
    def circ(self, x, y, r, fill, ol=True, w=3, olc=OL):
        X, Y, R = self.X(x), self.Y(y), self.R(r)
        self.d.ellipse((X - R, Y - R, X + R, Y + R), fill=fill, outline=olc if ol else None, width=self.LW(w))
    def ell(self, x0, y0, x1, y1, fill, ol=True, w=3, olc=OL):
        self.d.ellipse((self.X(x0), self.Y(y0), self.X(x1), self.Y(y1)), fill=fill,
                       outline=olc if ol else None, width=self.LW(w))
    def rect(self, x0, y0, x1, y1, fill, rad=0, ol=True, w=3, olc=OL):
        self.d.rounded_rectangle((self.X(x0), self.Y(y0), self.X(x1), self.Y(y1)), radius=self.R(rad), fill=fill,
                                 outline=olc if ol else None, width=self.LW(w))
    def line(self, pts, fill, w, ol=True, ends=True, olc=OL):
        pp = [(self.X(x), self.Y(y)) for x, y in pts]
        ends_pts = [pp[0], pp[-1]] if len(pp) > 1 else pp
        if ol:
            lw = self.LW(w + 6)
            self.d.line(pp, fill=olc, width=lw, joint='curve')
            if ends:
                for x, y in ends_pts:
                    r = lw / 2
                    self.d.ellipse((x - r, y - r, x + r, y + r), fill=olc)
        lw = self.LW(w)
        self.d.line(pp, fill=fill, width=lw, joint='curve')
        if ends:
            for x, y in ends_pts:
                r = lw / 2
                self.d.ellipse((x - r, y - r, x + r, y + r), fill=fill)
    def arc(self, box, a0, a1, fill, w):
        x0, y0, x1, y1 = box
        self.d.arc((self.X(x0), self.Y(y0), self.X(x1), self.Y(y1)), a0, a1, fill=fill, width=self.LW(w))
    def pie(self, box, a0, a1, fill, ol=True, w=3, olc=OL):
        x0, y0, x1, y1 = box
        self.d.pieslice((self.X(x0), self.Y(y0), self.X(x1), self.Y(y1)), a0, a1, fill=fill,
                        outline=olc if ol else None, width=self.LW(w))
    def poly(self, pts, fill, ol=True, w=3, olc=OL):
        pp = [(self.X(x), self.Y(y)) for x, y in pts]
        self.d.polygon(pp, fill=fill)
        if ol:
            self.d.line(pp + [pp[0]], fill=olc, width=self.LW(w), joint='curve')

SKIN_M = (246, 208, 178)
SKIN_C = (214, 160, 122)
MOUTH = (120, 28, 40)

def mouth_open(st, cx, my, lvl, wide=14):
    hs = [0, 8, 16, 26][lvl]
    st.ell(cx - wide, my - 3, cx + wide, my - 3 + hs, MOUTH, ol=True, w=3)

def draw_mari(st, cx, base, t, lvl, e, blink, speaking, conf):
    bob = 3 * math.sin(t * 3.0)
    hdy = (-5 * e if speaking else 0)
    HAIR, HAIRD = (224, 180, 112), (186, 138, 76)
    MAROON, JEANS, APRON = (124, 56, 66), (76, 106, 154), (36, 34, 38)
    # legs / shoes
    st.rect(cx - 54, base - 150, cx - 4, base - 14, JEANS, 10)
    st.rect(cx + 4, base - 150, cx + 54, base - 14, JEANS, 10)
    st.ell(cx - 62, base - 28, cx - 2, base + 4, WHITE)
    st.ell(cx + 2, base - 28, cx + 62, base + 4, WHITE)
    # torso: maroon polo + charcoal apron with Mavan heart
    st.rect(cx - 68, base - 395 + bob, cx + 68, base - 135 + bob, MAROON, 28)
    st.poly([(cx - 24, base - 396 + bob), (cx, base - 366 + bob), (cx + 24, base - 396 + bob)], (146, 72, 82))
    st.rect(cx - 54, base - 318 + bob, cx + 54, base - 138 + bob, APRON, 18)
    st.line([(cx - 38, base - 318 + bob), (cx - 22, base - 384 + bob)], APRON, 9, ol=False)
    st.line([(cx + 38, base - 318 + bob), (cx + 22, base - 384 + bob)], APRON, 9, ol=False)
    st.poly(heart_pts(cx, base - 246 + bob, 38), WHITE, ol=False)
    # neck
    st.rect(cx - 14, base - 425 + bob, cx + 14, base - 385 + bob, SKIN_M, 6)
    # resting arm (hand on hip)
    a0, a1, a2 = (cx - 62, base - 375 + bob), (cx - 108, base - 295 + bob), (cx - 60, base - 232 + bob)
    st.line([a0, a1, a2], SKIN_M, 26)
    st.line([a0, (a0[0] + (a1[0] - a0[0]) * 0.45, a0[1] + (a1[1] - a0[1]) * 0.45)], MAROON, 32)
    st.circ(a2[0], a2[1], 16, SKIN_M)
    # head (bun behind)
    hy = base - 478 + bob + hdy
    st.circ(cx + 56, hy - 54, 28, HAIR)
    st.circ(cx - 66, hy + 8, 12, SKIN_M)
    st.circ(cx + 66, hy + 8, 12, SKIN_M)
    st.circ(cx, hy, 66, SKIN_M, w=4)
    # hair (pulled back) with side locks
    st.pie((cx - 72, hy - 74, cx + 72, hy + 70), 180, 360, HAIR)
    st.rect(cx - 56, hy - 28, cx + 56, hy + 3, SKIN_M, 0, ol=False)
    st.ell(cx - 70, hy - 40, cx - 54, hy + 8, HAIR, ol=False)
    st.ell(cx + 54, hy - 40, cx + 70, hy + 8, HAIR, ol=False)
    st.line([(cx - 4, hy - 70), (cx - 30, hy - 32)], HAIRD, 4, ol=False)
    # blush + freckles
    st.circ(cx - 40, hy + 30, 12, (250, 178, 172), ol=False)
    st.circ(cx + 40, hy + 30, 12, (250, 178, 172), ol=False)
    for dx, dy in ((-34, 24), (-44, 30), (-30, 34), (34, 24), (44, 30), (30, 34)):
        st.circ(cx + dx, hy + dy, 2, (190, 124, 96), ol=False)
    # eyes (no glasses)
    for gx in (cx - 28, cx + 28):
        if blink:
            st.line([(gx - 11, hy + 8), (gx + 11, hy + 8)], OL, 4, ol=False)
        else:
            st.ell(gx - 11, hy - 3, gx + 11, hy + 19, WHITE, w=2)
            st.circ(gx + 1, hy + 8, 9, (72, 150, 88), ol=False)
            st.circ(gx + 1, hy + 8, 4.5, OL, ol=False)
            st.circ(gx + 4, hy + 5, 2.5, WHITE, ol=False)
    up = -6 if conf else 0
    st.line([(cx - 46, hy - 14 + up), (cx - 14, hy - 17 + up)], HAIRD, 5, ol=False)
    st.line([(cx + 14, hy - 17 + up), (cx + 46, hy - 14 + up)], HAIRD, 5, ol=False)
    st.ell(cx - 2, hy + 20, cx + 10, hy + 31, (228, 176, 146), ol=False)
    my = hy + 46
    if lvl > 0:
        mouth_open(st, cx, my, lvl)
    else:
        st.arc((cx - 17, my - 13, cx + 17, my + 6), 20, 160, (206, 100, 110), 4)
    # gesturing arm (in front)
    g = (0.55 + 0.45 * min(1, e)) if speaking else 0.0
    sh = (cx + 62, base - 375 + bob)
    elbow = (cx + 108 + 8 * g, base - 300 + bob - 14 * g)
    hand = (cx + 76 + 70 * g + 16 * g * math.sin(t * 7), base - 228 + bob - 160 * g + 10 * g * math.cos(t * 9))
    st.line([sh, elbow, hand], SKIN_M, 26)
    st.line([sh, (sh[0] + (elbow[0] - sh[0]) * 0.45, sh[1] + (elbow[1] - sh[1]) * 0.45)], MAROON, 32)
    st.circ(hand[0], hand[1], 17, SKIN_M)

def draw_cliente(st, cx, base, t, lvl, e, blink, speaking, mood):
    bob = 3 * math.sin(t * 2.6 + 1.2)
    hdy = (-4 * e if speaking else 0)
    HOOD, KHAKI, HAIR = (76, 80, 96), (176, 166, 150), (30, 26, 34)
    st.rect(cx - 48, base - 150, cx - 6, base - 14, KHAKI, 10)
    st.rect(cx + 6, base - 150, cx + 48, base - 14, KHAKI, 10)
    st.ell(cx - 62, base - 28, cx - 2, base + 4, WHITE)
    st.ell(cx + 2, base - 28, cx + 62, base + 4, WHITE)
    st.rect(cx - 76, base - 395 + bob, cx + 76, base - 135 + bob, HOOD, 30)
    st.rect(cx - 40, base - 240 + bob, cx + 40, base - 190 + bob, (62, 66, 80), 10)
    st.rect(cx - 15, base - 425 + bob, cx + 15, base - 385 + bob, SKIN_C, 6)
    st.line([(cx - 16, base - 392 + bob), (cx - 18, base - 330 + bob)], WHITE, 5, ol=False)
    st.line([(cx + 16, base - 392 + bob), (cx + 18, base - 330 + bob)], WHITE, 5, ol=False)
    hy = base - 478 + bob + hdy
    angry_point = (mood == 'angry' and speaking)
    if angry_point:
        hand = (cx - 175 + 10 * math.sin(t * 11), base - 420 + 12 * math.cos(t * 9) - 20 * e)
        st.line([(cx - 70, base - 375 + bob), (cx - 120, base - 340 + bob), hand], HOOD, 30)
        st.circ(hand[0], hand[1], 18, SKIN_C)
        st.line([(cx + 70, base - 318 + bob), (cx - 40, base - 278 + bob)], HOOD, 30)
        st.circ(cx - 44, base - 278 + bob, 17, SKIN_C)
    else:
        st.line([(cx - 72, base - 305 + bob), (cx + 56, base - 266 + bob)], HOOD, 30)
        st.line([(cx + 72, base - 322 + bob), (cx - 52, base - 280 + bob)], HOOD, 30)
        st.circ(cx + 58, base - 266 + bob, 17, SKIN_C)
        st.circ(cx - 54, base - 280 + bob, 17, SKIN_C)
    st.circ(cx - 66, hy + 6, 12, SKIN_C)
    st.circ(cx + 66, hy + 6, 12, SKIN_C)
    st.circ(cx, hy, 66, SKIN_C, w=4)
    st.pie((cx - 70, hy - 72, cx + 70, hy + 68), 180, 360, HAIR)
    st.rect(cx - 62, hy - 26, cx + 62, hy - 4, SKIN_C, 0, ol=False)
    st.ell(cx - 58, hy - 106, cx + 36, hy - 44, HAIR)
    wide = mood in ('worry', 'angry')
    for ex in (cx - 25, cx + 25):
        ry = 19 if wide else 16
        st.ell(ex - 15, hy + 2 - ry, ex + 15, hy + 2 + ry, WHITE, w=3)
        px, py = ex - 4, hy + 2
        if mood == 'deflated':
            py += 8
        if blink:
            st.rect(ex - 17, hy - 20, ex + 17, hy + 24, SKIN_C, 0, ol=False)
            st.line([(ex - 14, hy + 4), (ex + 14, hy + 4)], OL, 4, ol=False)
        else:
            st.circ(px, py, 6, OL, ol=False)
            if mood in ('smug', 'deflated'):
                st.rect(ex - 17, hy - 22, ex + 17, hy + 1, SKIN_C, 0, ol=False)
                st.line([(ex - 15, hy + 1), (ex + 15, hy + 1)], OL, 4, ol=False)
    if mood == 'smug':
        st.line([(cx - 42, hy - 28), (cx - 12, hy - 38)], HAIR, 7, ol=False)
        st.line([(cx + 12, hy - 22), (cx + 42, hy - 21)], HAIR, 7, ol=False)
    elif mood == 'worry':
        st.line([(cx - 42, hy - 24), (cx - 12, hy - 36)], HAIR, 7, ol=False)
        st.line([(cx + 12, hy - 36), (cx + 42, hy - 24)], HAIR, 7, ol=False)
    elif mood == 'angry':
        st.line([(cx - 42, hy - 38), (cx - 12, hy - 22)], HAIR, 8, ol=False)
        st.line([(cx + 12, hy - 22), (cx + 42, hy - 38)], HAIR, 8, ol=False)
    else:
        st.line([(cx - 42, hy - 20), (cx - 12, hy - 28)], HAIR, 7, ol=False)
        st.line([(cx + 12, hy - 28), (cx + 42, hy - 20)], HAIR, 7, ol=False)
    st.ell(cx - 10, hy + 18, cx + 4, hy + 30, (190, 138, 104), ol=False)
    my = hy + 46
    if lvl > 0:
        mouth_open(st, cx, my, lvl, 15)
    elif mood == 'smug':
        st.line([(cx - 16, my + 2), (cx + 8, my + 2), (cx + 20, my - 8)], OL, 4, ol=False)
    elif mood == 'worry':
        st.line([(cx - 14, my + 2), (cx - 5, my - 2), (cx + 5, my + 4), (cx + 14, my)], OL, 4, ol=False)
    elif mood == 'deflated':
        st.arc((cx - 14, my - 2, cx + 14, my + 16), 200, 340, OL, 4)
    else:
        st.line([(cx - 14, my + 2), (cx + 14, my + 2)], OL, 4, ol=False)
    if mood in ('worry', 'deflated'):
        dy = 8 * ((t * 1.3) % 1.0)
        sx, sy = cx + 70, hy - 30 + dy
        st.poly([(sx, sy - 18), (sx - 10, sy + 2), (sx + 10, sy + 2)], (120, 200, 255), ol=False)
        st.circ(sx, sy + 3, 10, (120, 200, 255), ol=False)

# ---------------------------------------------------------------- printer (wide shots)
PX, BED_Y, HMAX, SPEED = 540, 505, 200, 12.0

def profile_w(h):
    return 34 + 26 * math.sin(h / 200.0 * math.pi * 0.9 + 0.3)

def draw_object(st, h):
    layer = 5
    n = int(h // layer)
    for i in range(n):
        y = BED_Y - (i + 1) * layer
        w = profile_w(i * layer)
        col = GOLD if i % 2 == 0 else (244, 196, 96)
        st.d.rectangle((st.X(PX - w), st.Y(y), st.X(PX + w), st.Y(y + layer)), fill=col)
    if n > 0:
        w = profile_w(0)
        st.d.line((st.X(PX - w), st.Y(BED_Y), st.X(PX - w), st.Y(BED_Y - n * layer)), fill=OL, width=2 * S)
        st.d.line((st.X(PX + w), st.Y(BED_Y), st.X(PX + w), st.Y(BED_Y - n * layer)), fill=OL, width=2 * S)

def draw_spaghetti(st, h, t):
    ytop = BED_Y - h * 0.75
    draw_object(st, h * 0.75)
    for i in range(9):
        pts = []
        for k in range(22):
            u = k / 21.0
            x = PX + (i - 4) * 12 * (u + 0.3) + 55 * math.sin(k * 0.8 + i * 2.1 + t * 1.5) * u
            y = ytop - 10 + u * (BED_Y - ytop + 10) + 7 * math.sin(k * 1.3 + i)
            pts.append((x, y))
        st.line(pts, GOLD if i % 2 else (250, 206, 110), 4, ol=False, ends=False)

TF = P[2] + AUD[2]['d'] * 0.74

def draw_printer(st, t):
    st.rect(330, 560, 750, 594, (176, 150, 120), 8)
    st.rect(352, 594, 378, 770, (150, 126, 100), 4)
    st.rect(702, 594, 728, 770, (150, 126, 100), 4)
    st.rect(380, 520, 700, 562, WHITE, 10)
    st.rect(396, 190, 420, 524, WHITE, 6)
    st.rect(660, 190, 684, 524, WHITE, 6)
    st.rect(384, 176, 696, 206, WHITE, 10)
    st.rect(420, 508, 660, 522, WARM, 4)
    st.circ(PX, 128, 44, GOLD, w=4)
    st.circ(PX, 128, 14, WHITE, w=3)
    for k in range(3):
        a = t * 2.0 + k * 2.094
        st.line([(PX, 128), (PX + 36 * math.cos(a), 128 + 36 * math.sin(a))], (190, 130, 30), 4, ol=False)
    st.poly(heart_pts(PX, 548, 22), OL, ol=False)  # Mavan heart on the base
    if t < TF:
        h, state = min(HMAX, SPEED * t), 'grow'
        hf = h
    elif t < P[4]:
        hf = min(HMAX, SPEED * TF)
        h, state = hf, 'fail'
    else:
        h, state = min(HMAX, SPEED * (t - P[4])), 'grow'
    if state == 'fail':
        draw_spaghetti(st, hf, t)
        ny, nw = BED_Y - hf - 10, 45
    else:
        draw_object(st, h)
        ny, nw = BED_Y - h - 10, profile_w(h)
    by = ny - 40
    st.rect(402, by, 678, by + 20, (214, 208, 196), 5)
    nx = PX + nw * math.sin(t * 9.0)
    st.rect(nx - 20, by - 6, nx + 20, by + 28, GOLD, 6)
    st.poly([(nx - 10, by + 28), (nx + 10, by + 28), (nx, by + 46)], WARM, ol=True, w=2)

# ---------------------------------------------------------------- backgrounds
def make_wide_bg():
    base = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(base)
    floor_y = 1470
    d.rectangle((0, floor_y, W, H), fill=WARM)
    for i in range(0, 14):
        y = floor_y + 14 + i * 46
        d.line((0, y, W, y), fill=(214, 206, 192), width=3)
    d.rectangle((0, floor_y - 5, W, floor_y), fill=CHAR)
    return base

BG_WIDE = make_wide_bg()

def bg_wide(t):
    img = BG_WIDE.copy()
    d = ImageDraw.Draw(img)
    for k in range(0, 1470, 54):
        y = (k - t * 30) % 1470
        d.line((0, y, W, y), fill=LINEC, width=2)
    return img

def bg_cu(t, mx):
    img = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(img)
    for k in range(0, H + 54, 54):
        y = (k - t * 30) % H
        d.line((0, y, W, y), fill=LINEC, width=2)
    cx, cy = mx, 1250
    d.ellipse((cx - 470, cy - 470, cx + 470, cy + 470), fill=(252, 238, 204))
    for i in range(28):
        a = i * (2 * math.pi / 28) + t * 0.15
        d.line((cx + 480 * math.cos(a), cy + 480 * math.sin(a), cx + 760 * math.cos(a), cy + 760 * math.sin(a)),
               fill=(240, 226, 196), width=4)
    d.ellipse((cx - 500, cy - 500, cx + 500, cy + 500), outline=CHAR, width=3)
    return img

# ---------------------------------------------------------------- bubbles
def wrap(txt, size, maxw):
    f = font(FB, size)
    lines, cur = [], []
    for w in txt.split():
        if cur and f.getlength(' '.join(cur + [w])) > maxw:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    lines.append(cur)
    return lines

def is_emph(w):
    z = ''.join(c for c in w if c.isalpha())
    return len(z) >= 2 and z.isupper() and not any(c.isdigit() for c in w)

BSIZE, BLH, BPAD, BMAXW = 48, 64, 34, 640
_bub = {}

def make_bubble(i, tipx, x0=None):
    key = (i, tipx)
    if key in _bub:
        return _bub[key]
    a = AUD[i]
    lines = wrap(a['txt'], BSIZE, BMAXW)
    f = font(FB, BSIZE)
    wmax = max(f.getlength(' '.join(l)) for l in lines)
    w = int(wmax + 2 * BPAD)
    h = int(len(lines) * BLH + 2 * BPAD - 8)
    if x0 is None:
        x0 = tipx - w * 0.3 if tipx < 540 else tipx - w * 0.7
    x0 = max(30, min(W - 30 - w, x0))
    tx = int(min(max(tipx - x0, 60), w - 60))
    col = WHITE if a['spk'] == 'mari' else (240, 235, 226)
    pad = 12
    im = Image.new('RGBA', (w + 2 * pad, h + 60 + pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((pad, pad, pad + w, pad + h), radius=38, fill=col, outline=OL, width=6)
    d.polygon([(pad + tx - 22, pad + h - 3), (pad + tx + 22, pad + h - 3), (pad + tx, pad + h + 40)], fill=col, outline=OL)
    d.rectangle((pad + tx - 18, pad + h - 6, pad + tx + 18, pad + h - 1), fill=col)
    _bub[key] = dict(im=im, lines=lines, x0=x0, w=w, h=h, tx=tx, pad=pad)
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
    words_total = sum(len(l) for l in b['lines'])
    prog = (t - P[i]) / max(0.2, a['d'] * 0.92)
    nvis = int(math.ceil(max(0.0, min(1.0, prog)) * words_total))
    f = font(FB, BSIZE)
    k = 0
    for li, line in enumerate(b['lines']):
        x = b['pad'] + BPAD
        y = b['pad'] + BPAD - 4 + li * BLH + BLH // 2
        for wd in line:
            if k < nvis:
                if is_emph(wd):
                    wl = f.getlength(wd)
                    d.rounded_rectangle((x - 7, y - 31, x + wl + 5, y + 31), radius=12, fill=GOLDL)
                d.text((x, y), wd, font=f, fill=OL, anchor='lm')
            x += f.getlength(wd + ' ')
            k += 1
    tipx_layer = b['pad'] + b['tx']
    tipy_layer = b['pad'] + b['h'] + 40
    pp = min(1.0, (t - st) / 0.22)
    if pp <= 0:
        return
    s = 0.55 + 0.45 * eob(pp)
    lw, lh = max(1, int(im.width * s)), max(1, int(im.height * s))
    l2 = im.resize((lw, lh), Image.LANCZOS) if abs(s - 1) > 0.01 else im
    aa = min(1.0, pp * 3) * alpha
    l2 = l2.copy()
    l2.putalpha(l2.getchannel('A').point(lambda v: int(v * aa)))
    img.paste(l2, (int(tipx - tipx_layer * s), int(tipy - tipy_layer * s)), l2)

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
    if t < P[2] + AUD[2]['d'] * 0.45:
        return 'smug'
    if t < P[3]:
        return 'worry'
    if t < P[3] + AUD[3]['d'] + 0.2:
        return 'angry'
    if t < P[4] + 1.2:
        return 'worry'
    return 'deflated'

def state(t):
    ai = active_line(t)
    spk = AUD[ai]['spk'] if ai is not None else None
    e = env_at(ai, t) if ai is not None else 0.0
    return spk, e, (lvl_of(e) if ai is not None else 0)

# ---------------------------------------------------------------- scenes
CX_M, CX_L = 228, 840
WK = 1.18
FLOOR_Y = 1470
WOX = 540 * (1 - WK)
WOY = (FLOOR_Y - 560) - 770 * WK
def wx(x): return x * WK + WOX
HEAD_TOP_W = 560 + (770 - 478 - 66) * WK + WOY
TIP_W = HEAD_TOP_W - 6

def logo_bug(img, cx=540, cy=330, width=300, alpha=1.0):
    lg = logo_w(width)
    paste_center(img, lg, cx, cy, alpha)

def scene_wide(t, lines_here, limit, hook=False, names=True):
    img = bg_wide(t)
    st = Stage(W, 960, WK, WOX, WOY)
    draw_printer(st, t)
    spk, e, lvl = state(t)
    blink_c = (t % 2.6) < 0.12
    blink_l = ((t + 1.1) % 3.1) < 0.12
    conf = (P[4] <= t < P[4] + AUD[4]['d'])
    draw_mari(st, CX_M, 770, t, lvl if spk == 'mari' else 0, e if spk == 'mari' else 0.0, blink_c, spk == 'mari', conf)
    draw_cliente(st, CX_L, 770, t, lvl if spk == 'cliente' else 0, e if spk == 'cliente' else 0.0,
                 blink_l, spk == 'cliente', cliente_mood(t))
    small = st.im.resize((W, 960), Image.LANCZOS)
    img.paste(small, (0, 560), small)
    logo_bug(img)
    if names:
        for txt, cx in (('MARI', CX_M), ('CLIENTE', CX_L)):
            l = tl(txt, 34, GRAY, FM)
            img.paste(l, (int(wx(cx) - l.width / 2), FLOOR_Y + 22), l)
    if hook:
        paste_pop(img, pill('IMPRESSORA 3D DÁ DINHEIRO FÁCIL?', 38, WHITE, CHAR), 540, 488, (t + 0.3) / 0.28)
    for i in lines_here:
        tipx = wx(CX_M) if AUD[i]['spk'] == 'mari' else wx(CX_L)
        draw_bubble(img, i, t, tipx, TIP_W, limit)
    return img

def cards_and_values(img, t, t0, cards, items, d_line, p_line, mir):
    draw_value_items(img, items, t, t0)
    for txt, icon, cx, cy, ang, fr in cards:
        st0 = p_line + d_line * fr
        if t < st0:
            continue
        gold = (txt == 'MARCA')
        lay = pill(txt, 38, OL, GOLD if gold else WHITE, icon)
        lay = rot(lay, ang)
        cxx = min(max(cx, 44 + lay.width / 2), (W - 150) - lay.width / 2)
        paste_pop(img, lay, cxx, cy, (t - st0) / 0.28)

CU_K = 2.0
MARI_X = 280
CU_HY = 1060

def scene_close(t, i, t0, mirror, cards, items):
    mx = W - MARI_X if mirror else MARI_X
    img = bg_cu(t, mx)
    cards_and_values(img, t, t0, cards, items, AUD[i]['d'], P[i], mirror)
    cx_char, base = 300, 770
    hy_char = base - 478
    Y0 = 500
    ox = MARI_X - cx_char * CU_K
    oy = (CU_HY - Y0) - hy_char * CU_K
    prog = (t - t0) / max(0.1, (P[i + 1] if i + 1 < len(P) else TOTAL) - t0)
    k = CU_K + 0.10 * min(1, max(0, prog))
    st = Stage(W, H - Y0, k, MARI_X - cx_char * k, (CU_HY - Y0) - hy_char * k)
    spk, e, lvl = state(t)
    draw_mari(st, cx_char, base, t, lvl, e, (t % 2.6) < 0.12, True, i == 4)
    small = st.im.resize((W, H - Y0), Image.LANCZOS)
    if mirror:
        small = ImageOps.mirror(small)
    img.paste(small, (0, Y0), small)
    logo_bug(img)
    tipy = CU_HY - 74 * k - 8
    draw_bubble(img, i, t, mx, tipy, (C2 if i == 2 else C4))
    return img

CARDS_A = [('Filamento caro', 'spool', 790, 1010, -3, 0.06),
           ('Conta de luz', 'bulb', 800, 1170, 2.5, 0.40),
           ('Peça que falha', 'warn', 790, 1330, -2, 0.70)]
ITEMS_A = [('coin', 900, 860, 46, 0.0), ('coin', 640, 1560, 40, 1.4), ('tag', 900, 1520, 0, 0.7),
           ('spark', 630, 900, 44, 0.3), ('spark', 890, 1080, 34, 1.1), ('sparkw', 700, 1400, 30, 2.0)]
CARDS_B = [('DESIGN', 'pencil', 300, 1010, 3, 0.28),
           ('NICHO', 'target', 290, 1170, -2.5, 0.50),
           ('MARCA', 'heart', 300, 1330, 2, 0.70)]
ITEMS_B = [('crown', 250, 850, 0, 0.0), ('gem', 520, 1560, 0, 0.8), ('coin', 150, 1520, 44, 1.5),
           ('coin', 330, 1580, 36, 0.4), ('spark', 480, 930, 44, 0.3), ('spark', 90, 1120, 34, 1.1)]

def scene_cta(t):
    img = scene_wide(t, [5], C5, names=False)
    t0 = P[5] + 0.9
    swap = P[5] + AUD[5]['d'] + 0.1
    if t0 <= t < swap:
        paste_pop(img, pill('COMENTA “EU”', 54, WHITE, CHAR), 540, 1535, (t - t0) / 0.28)
    elif t >= swap:
        paste_pop(img, pill('MANDA PRA QUEM ACHA QUE É FÁCIL', 36, WHITE, CHAR, 'send'), 520, 1535, (t - swap) / 0.28)
    return img

def scene_end(t):
    t0 = C5
    img = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(img)
    for k in range(0, H + 54, 54):
        y = (k - t * 30) % H
        d.line((0, y, W, y), fill=LINEC, width=2)
    p = min(1.0, (t - t0) / 0.5)
    lg = logo_w(800)
    s = 0.85 + 0.15 * eob(p)
    lay = lg.resize((int(lg.width * s), int(lg.height * s)), Image.LANCZOS)
    paste_center(img, lay, 540, 860, alpha=min(1.0, p * 2))
    put(img, '@mavan.3d', 54, OL, 540, 1180, t, t0 + 0.6, FM)
    return img

def frame(t):
    if t < C1:
        img = scene_wide(t, [0, 1], C1, hook=True)
    elif t < C2:
        img = scene_close(t, 2, C1, False, CARDS_A, ITEMS_A)
    elif t < C3:
        img = scene_wide(t, [3], C3)
        if t >= C2 + 0.1:
            put(img, 'FALHOU!', 96, RED, 540, 1300, t, C2 + 0.1)
    elif t < C4:
        img = scene_close(t, 4, C3, True, CARDS_B, ITEMS_B)
    elif t < C5:
        img = scene_cta(t)
    else:
        img = scene_end(t)
    # quick cream flash at every cut
    for c in (C1, C2, C3, C4, C5):
        a = max(0.0, 1 - abs(t - c) / 0.08) * 0.9
        if a > 0.01:
            img = Image.blend(img, Image.new('RGB', (W, H), CREAM), a)
    return img

# ---------------------------------------------------------------- run
def preview():
    moments = [0.05, P[2] + AUD[2]['d'] * 0.92, P[3] + 1.4, P[4] + 4.8, P[5] + 3.0, C5 - 0.6, C5 + 0.9]
    sheet = Image.new('RGB', (360 * 7, 640))
    for n, t in enumerate(moments):
        im = frame(t)
        im.save(f'{OUT}/prev{n + 1}.png')
        sheet.paste(im.resize((360, 640), Image.LANCZOS), (360 * n, 0))
    sheet.save(f'{OUT}/sheet.png')
    print('P', [round(float(x), 2) for x in P], 'cuts', [round(float(x), 2) for x in (C1, C2, C3, C4, C5)], 'TOTAL', round(float(TOTAL), 2))

def render():
    tmp = f'{OUT}/video.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '18',
                          '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    n = int(round(TOTAL * FPS))
    for i in range(n):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        sys.exit('ffmpeg video failed')
    os.rename(tmp, f'{OUT}/video.mp4')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error']
    for a in AUD:
        cmd += ['-i', a['file']]
    cmd += ['-i', f'{OUT}/video.mp4']
    fc = []
    for i, a in enumerate(AUD):
        ms = int(P[i] * 1000)
        fc.append(f"[{i}:a]atrim=start={a['s']:.3f}:end={a['e']:.3f},asetpts=PTS-STARTPTS,"
                  f"aformat=sample_rates=44100:channel_layouts=mono,adelay={ms}:all=1[a{i}]")
    mix = ''.join(f'[a{i}]' for i in range(len(AUD)))
    fc.append(f"{mix}amix=inputs={len(AUD)}:normalize=0:duration=longest,apad,atrim=0:{TOTAL:.3f},"
              f"loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
    cmd += ['-filter_complex', ';'.join(fc), '-map', f'{len(AUD)}:v', '-map', '[aout]',
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', f'{TOTAL:.3f}', f'{OUT}/mavan_esquete_2d_v3.tmp.mp4']
    subprocess.check_call(cmd)
    os.rename(f'{OUT}/mavan_esquete_2d_v3.tmp.mp4', f'{OUT}/mavan_esquete_2d_v2.mp4')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':
        preview()
    else:
        render()
