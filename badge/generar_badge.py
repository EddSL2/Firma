"""
Genera el badge animado (GIF en bucle) para la firma de Gmail de Nubosoft.

- Tamaño final: 400x160 px (renderizado a 2x y reducido para bordes suaves).
- Ciclo: 5 s en bucle infinito (Google Cloud -> AWS -> Google Cloud), 20 fps.
- Paleta global única para evitar parpadeos entre fotogramas.

Logos oficiales: si colocas estos PNG (fondo transparente) en ./assets/, se usan
automáticamente en lugar de los marcadores dibujados:
    assets/nubosoft.png      -> logotipo Nubosoft (zona izquierda)
    assets/gcp-partner.png   -> badge oficial Google Cloud Partner (MSP)
    assets/aws-partner.png   -> badge oficial AWS Partner Network

Uso:  python generar_badge.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
ASSETS = HERE / "assets"
OUT_GIF = HERE / "nubosoft-partners-badge.gif"
OUT_PNG = HERE / "nubosoft-partners-badge-preview.png"

S = 2                      # supersampling
W, H = 400 * S, 160 * S    # lienzo de trabajo
FPS = 20
CYCLE = 5.0                # segundos
FRAMES = int(CYCLE * FPS)

# Colores
WHITE = (255, 255, 255)
BORDER = (226, 232, 240)          # #E2E8F0
NAVY = (11, 61, 145)              # #0B3D91
BLUE = (26, 86, 219)              # #1A56DB
CYAN = (6, 182, 212)              # #06B6D4
SLATE_500 = (100, 116, 139)
SLATE_700 = (51, 65, 85)
G_BLUE, G_RED, G_YELLOW, G_GREEN = (66, 133, 244), (234, 67, 53), (251, 188, 4), (52, 168, 83)
AWS_INK, AWS_ORANGE = (35, 47, 62), (255, 153, 0)

FONTS = Path("C:/Windows/Fonts")


def font(name, size):
    for n in name:
        p = FONTS / n
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


F_BOLD = lambda s: font(["segoeuib.ttf", "arialbd.ttf"], s)
F_SEMI = lambda s: font(["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"], s)
F_REG = lambda s: font(["segoeui.ttf", "arial.ttf"], s)


def text_w(draw, txt, f, spacing=0):
    return draw.textlength(txt, font=f) + spacing * max(len(txt) - 1, 0)


def draw_spaced(draw, xy, txt, f, fill, spacing=0):
    x, y = xy
    for ch in txt:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + spacing


def gradient(size, c1, c2, horizontal=False):
    w, h = size
    t = np.linspace(0, 1, w if horizontal else h)
    arr = (np.array(c1)[None, :] * (1 - t)[:, None] + np.array(c2)[None, :] * t[:, None]).astype(np.uint8)
    if horizontal:
        arr = np.repeat(arr[None, :, :], h, axis=0)
    else:
        arr = np.repeat(arr[:, None, :], w, axis=1)
    return Image.fromarray(arr, "RGB")


def load_asset(name, box):
    """Carga un PNG de ./assets ajustado (contain) a box=(w,h). None si no existe."""
    p = ASSETS / name
    if not p.exists():
        return None
    im = Image.open(p).convert("RGBA")
    im.thumbnail(box, Image.LANCZOS)
    canvas = Image.new("RGBA", box, (0, 0, 0, 0))
    canvas.paste(im, ((box[0] - im.width) // 2, (box[1] - im.height) // 2), im)
    return canvas


def cloud_mask(size):
    """Silueta de nube genérica (unión de círculos + base redondeada)."""
    w, h = size
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse((w * 0.08, h * 0.38, w * 0.48, h * 0.98), fill=255)
    d.ellipse((w * 0.26, h * 0.05, w * 0.74, h * 0.80), fill=255)
    d.ellipse((w * 0.52, h * 0.30, w * 0.94, h * 0.98), fill=255)
    d.rounded_rectangle((w * 0.20, h * 0.55, w * 0.80, h * 0.98), radius=h * 0.2, fill=255)
    return m


# ----------------------------------------------------------------------------
# Capa estática: tarjeta + branding Nubosoft (siempre visible)
# ----------------------------------------------------------------------------
BADGE = (412, 28, 772, 268)        # caja del badge (coordenadas 2x)
BW, BH = BADGE[2] - BADGE[0], BADGE[3] - BADGE[1]


def build_base():
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)
    # Tarjeta: radio 12px, borde 1px #E2E8F0
    d.rounded_rectangle((1, 1, W - 2, H - 2), radius=12 * S, fill=WHITE, outline=BORDER, width=1 * S)

    p_nubo = ASSETS / "nubosoft.png"
    if p_nubo.exists():
        raw_nubo = Image.open(p_nubo).convert("RGBA")
        nubo = raw_nubo.copy()
        nubo.thumbnail((320, 100), Image.LANCZOS)
        im.paste(nubo, (36, 46), nubo)
    else:
        # Monograma: círculo con degradado y nube blanca
        size = 84
        g = gradient((size, size), NAVY, CYAN)
        circ = Image.new("L", (size, size), 0)
        ImageDraw.Draw(circ).ellipse((0, 0, size - 1, size - 1), fill=255)
        im.paste(g, (36, 52), circ)
        cm = cloud_mask((52, 36))
        im.paste(Image.new("RGB", cm.size, WHITE), (36 + 16, 52 + 26), cm)
        # Wordmark
        fw = F_BOLD(42)
        d.text((136, 50), "NUBO", font=fw, fill=NAVY)
        d.text((136 + d.textlength("NUBO", font=fw), 50), "SOFT", font=fw, fill=CYAN)
        d.text((138, 104), "Multi-Cloud Solutions", font=F_REG(21), fill=SLATE_500)

    # Texto inferior
    draw_spaced(d, (38, 182), "PARTNER MULTICLOUD", F_BOLD(16), BLUE, spacing=3)
    d.text((38, 208), "México · Colombia · España", font=F_SEMI(20), fill=SLATE_700)

    # Divisor vertical con degradado
    div = gradient((2, 200), BLUE, CYAN)
    im.paste(div, (392, 60))

    # Contenedor del badge (fondo blanco, radio 8px, borde)
    d.rounded_rectangle(BADGE, radius=8 * S, fill=WHITE, outline=BORDER, width=1 * S)
    return im


# ----------------------------------------------------------------------------
# Contenidos alternantes del badge (RGBA, tamaño BW x BH)
# ----------------------------------------------------------------------------
def build_gcp():
    c = Image.new("RGBA", (BW, BH), (255, 255, 255, 0))
    d = ImageDraw.Draw(c)
    
    # Logo oficial Google Cloud
    p_off = ASSETS / "gcp-partner.png"
    if p_off.exists():
        raw = Image.open(p_off).convert("RGBA")
        logo = raw.copy()
        logo.thumbnail((260, 130), Image.LANCZOS)
        c.paste(logo, ((BW - logo.width) // 2, 20), logo)
    
    # Pill oficial: Managed Service Provider
    f_pill = F_BOLD(15)
    t_msp = "MANAGED SERVICE PROVIDER"
    tw = d.textlength(t_msp, font=f_pill)
    px, py = (BW - tw) // 2 - 14, 168
    d.rounded_rectangle((px, py, px + tw + 28, py + 30), radius=15, fill=(232, 240, 254), outline=(194, 214, 249), width=1)
    d.text(((BW - tw) // 2, py + 7), t_msp, font=f_pill, fill=(26, 115, 232))

    # Barra acento 4 colores Google
    seg = 32
    x0 = (BW - seg * 4) // 2
    for i, col in enumerate([(66, 133, 244), (234, 67, 53), (251, 188, 4), (52, 168, 83)]):
        d.rectangle((x0 + i * seg, 212, x0 + (i + 1) * seg - 2, 216), fill=col)
    return c


def build_aws():
    c = Image.new("RGBA", (BW, BH), (255, 255, 255, 0))
    d = ImageDraw.Draw(c)
    
    # Logo oficial AWS
    p_off = ASSETS / "aws-partner.png"
    if p_off.exists():
        raw = Image.open(p_off).convert("RGBA")
        logo = raw.copy()
        logo.thumbnail((240, 120), Image.LANCZOS)
        c.paste(logo, ((BW - logo.width) // 2, 28), logo)
    
    # Pill oficial: AWS Partner Network
    t_apn = "AWS PARTNER NETWORK"
    f_apn = F_BOLD(16)
    tw_a = d.textlength(t_apn, font=f_apn)
    px_a, py_a = (BW - tw_a) // 2 - 14, 164
    d.rounded_rectangle((px_a, py_a, px_a + tw_a + 28, py_a + 30), radius=15, fill=(255, 247, 237), outline=(254, 215, 170), width=1)
    d.text(((BW - tw_a) // 2, py_a + 6), t_apn, font=f_apn, fill=(194, 65, 12))
    return c


# ----------------------------------------------------------------------------
# Animación
# ----------------------------------------------------------------------------
def ease(t):  # easeInOutCubic
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


HOLD, TRANS = 2.0, 0.6          # 2.0 s visible + 0.6 s transición (x2 = 5.2 s)
CYCLE = (HOLD + TRANS) * 2
FRAMES = int(CYCLE * FPS)
SLIDE = 24                      # desplazamiento horizontal sutil (12px reales)


def state(t):
    """Devuelve lista de (capa, offset_x, alpha) y posición del brillo (0..1 o None)."""
    t %= CYCLE
    layers, shine = [], None
    seq = [("gcp", "aws"), ("aws", "gcp")]
    half = HOLD + TRANS
    idx = int(t // half) % 2
    lt = t % half
    cur, nxt = seq[idx]
    if lt < HOLD:
        layers.append((cur, 0, 1.0))
        s0, s1 = 0.5, 1.5      # brillo metálico durante la fase visible
        if s0 <= lt <= s1:
            shine = (lt - s0) / (s1 - s0)
    else:
        # Efecto Carrusel auténtico (Push Slider sin superposición de texto)
        p = ease((lt - HOLD) / TRANS)
        layers.append((cur, -BW * p, 1.0))
        layers.append((nxt, BW * (1.0 - p), 1.0))
    active = cur if lt < HOLD + TRANS / 2 else nxt
    return layers, shine, active


def shine_mask(pos):
    """Banda diagonal suave que recorre el badge."""
    yy, xx = np.mgrid[0:BH, 0:BW]
    diag = xx + yy * 0.45
    span = BW + BH * 0.45
    center = -60 + pos * (span + 120)
    band = np.exp(-((diag - center) / 22.0) ** 2) * 0.75
    return Image.fromarray((band * 255).astype(np.uint8), "L")


def render(base, contents, t):
    frame = base.copy()
    layers, shine, active = state(t)
    badge = Image.new("RGBA", (BW, BH), (255, 255, 255, 0))
    for name, dx, a in layers:
        layer = contents[name]
        if a < 1:
            r, g, b, al = layer.split()
            al = al.point(lambda v, a=a: int(v * a))
            layer = Image.merge("RGBA", (r, g, b, al))
        badge.alpha_composite(layer, (int(round(dx)), 0))
    if shine is not None:
        # El brillo se limita a los píxeles del logo (efecto metálico sobre la marca)
        sm = np.array(shine_mask(shine), dtype=np.float32)
        la = np.array(badge.split()[3], dtype=np.float32) / 255
        glow = Image.fromarray((sm * la).astype(np.uint8), "L")
        white = Image.new("RGBA", (BW, BH), (255, 255, 255, 255))
        white.putalpha(glow)
        badge.alpha_composite(white)
    # Recorte al interior del contenedor (respetando bordes redondeados)
    clip = Image.new("L", (BW, BH), 0)
    ImageDraw.Draw(clip).rounded_rectangle((3, 3, BW - 4, BH - 4), radius=8 * S - 2, fill=255)
    a = Image.fromarray((np.array(badge.split()[3], dtype=np.float32) * (np.array(clip) / 255)).astype(np.uint8))
    badge.putalpha(a)
    frame.paste(badge, BADGE[:2], badge)
    # Indicadores del carrusel
    d = ImageDraw.Draw(frame)
    cx, cy = (BADGE[0] + BADGE[2]) // 2, 290
    for i, name in enumerate(["gcp", "aws"]):
        x = cx - 14 + i * 28
        if name == active:
            d.rounded_rectangle((x - 10, cy - 5, x + 10, cy + 5), radius=5, fill=BLUE)
        else:
            d.ellipse((x - 5, cy - 5, x + 5, cy + 5), fill=BORDER)
    return frame.resize((W // S, H // S), Image.LANCZOS)


def main():
    base = build_base()
    contents = {"gcp": build_gcp(), "aws": build_aws()}
    frames = [render(base, contents, i / FPS) for i in range(FRAMES)]

    # Paleta global: mosaico de fotogramas representativos
    sample = frames[::4]
    mosaic = Image.new("RGB", (W // S, (H // S) * len(sample)))
    for i, f in enumerate(sample):
        mosaic.paste(f, (0, i * (H // S)))
    pal = mosaic.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    # Fuerza blanco puro (#FFFFFF) para que el fondo se funda con el correo
    p = pal.getpalette()[:128 * 3]
    wi = max(range(128), key=lambda i: sum(p[i * 3:i * 3 + 3]))
    p[wi * 3:wi * 3 + 3] = [255, 255, 255]
    pal = Image.new("P", (1, 1))
    pal.putpalette(p + [0] * (768 - len(p)))
    pal_arr = np.array(p, dtype=np.int32).reshape(-1, 3)

    def to_p(f):
        # Mapeo exacto al color más cercano (el de Pillow usa caché aproximada)
        a = np.asarray(f, dtype=np.int32).reshape(-1, 3)
        uniq, inv = np.unique(a, axis=0, return_inverse=True)
        d = ((uniq[:, None, :] - pal_arr[None, :, :]) ** 2).sum(-1)
        idx = d.argmin(1).astype(np.uint8)[inv.ravel()]
        out = Image.fromarray(idx.reshape(f.height, f.width), "P")
        out.putpalette(pal.getpalette())
        return out

    q = [to_p(f) for f in frames]

    q[0].save(OUT_GIF, save_all=True, append_images=q[1:], duration=int(1000 / FPS),
              loop=0, optimize=True, disposal=1)
    frames[0].save(OUT_PNG)
    kb = OUT_GIF.stat().st_size / 1024
    print(f"GIF: {OUT_GIF} | {len(frames)} fotogramas | {CYCLE}s | {kb:.1f} KB")


if __name__ == "__main__":
    main()
