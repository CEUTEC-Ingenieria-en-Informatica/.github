"""Dibuja el logo de la comunidad y lo guarda como SVG y PNG de 500x500.

El logo es propio: un icono de app con degradado, tres mosaicos de app y en el
cuarto la curva de la pluma de un editor de diseño (anclas y manijas).
No usa escudo, nombre ni colores oficiales de ninguna universidad.

Uso:
    python generar_logo.py            (necesita Pillow solo para el PNG)
"""
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TAM = 500

# Paleta propia
VIOLETA = (108, 77, 246)   # #6C4DF6
TURQUESA = (0, 191, 166)   # #00BFA6
NOCHE = (27, 24, 54)       # #1B1836
BLANCO = (255, 255, 255)

# Geometría en coordenadas de 500x500
FONDO = (20, 20, 480, 480, 112)              # x0, y0, x1, y1, radio
MOSAICOS = [
    (110, 110, 230, 230, 32, 1.0),           # x0, y0, x1, y1, radio, opacidad
    (270, 110, 390, 230, 60, 0.55),
    (110, 270, 230, 390, 32, 0.55),
]
P0, C1, C2, P3 = (270, 390), (270, 310), (390, 350), (390, 270)
TRAZO = 14


def hexa(c):
    return "#%02X%02X%02X" % c


def svg():
    x0, y0, x1, y1, r = FONDO
    partes = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" role="img" aria-labelledby="titulo">',
        '  <title id="titulo">Logo de la comunidad CEUTEC Ingeniería en Informática (no oficial)</title>',
        '  <defs>',
        '    <linearGradient id="fondo" x1="0" y1="0" x2="1" y2="1">',
        f'      <stop offset="0" stop-color="{hexa(VIOLETA)}"/>',
        f'      <stop offset="1" stop-color="{hexa(TURQUESA)}"/>',
        '    </linearGradient>',
        '  </defs>',
        f'  <rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{r}" fill="url(#fondo)"/>',
    ]
    for a, b, c, d, rr, op in MOSAICOS:
        extra = "" if op == 1.0 else f' fill-opacity="{op}"'
        partes.append(f'  <rect x="{a}" y="{b}" width="{c - a}" height="{d - b}" rx="{rr}" fill="#FFFFFF"{extra}/>')
    partes += [
        f'  <line x1="{P0[0]}" y1="{P0[1]}" x2="{C1[0]}" y2="{C1[1]}" stroke="#FFFFFF" stroke-width="4" stroke-opacity="0.8"/>',
        f'  <line x1="{P3[0]}" y1="{P3[1]}" x2="{C2[0]}" y2="{C2[1]}" stroke="#FFFFFF" stroke-width="4" stroke-opacity="0.8"/>',
        f'  <path d="M{P0[0]} {P0[1]} C{C1[0]} {C1[1]} {C2[0]} {C2[1]} {P3[0]} {P3[1]}" fill="none" stroke="#FFFFFF" stroke-width="{TRAZO}" stroke-linecap="round"/>',
        f'  <circle cx="{C1[0]}" cy="{C1[1]}" r="9" fill="#FFFFFF"/>',
        f'  <circle cx="{C2[0]}" cy="{C2[1]}" r="9" fill="#FFFFFF"/>',
    ]
    for x, y in (P0, P3):
        partes.append(f'  <rect x="{x - 14}" y="{y - 14}" width="28" height="28" rx="6" fill="#FFFFFF" stroke="{hexa(NOCHE)}" stroke-width="5"/>')
    partes.append("</svg>")
    return "\n".join(partes) + "\n"


def bezier(t):
    u = 1 - t
    return tuple(u ** 3 * P0[i] + 3 * u * u * t * C1[i] + 3 * u * t * t * C2[i] + t ** 3 * P3[i] for i in range(2))


def png(ruta):
    from PIL import Image, ImageDraw

    s = 4  # se dibuja grande y se reduce para suavizar bordes
    n = TAM * s
    k = lambda v: v * s  # noqa: E731

    degradado = Image.new("RGB", (n, n))
    d = ImageDraw.Draw(degradado)
    for i in range(2 * n):
        t = i / (2 * n - 1)
        color = tuple(round(VIOLETA[c] + (TURQUESA[c] - VIOLETA[c]) * t) for c in range(3))
        d.line([(i, 0), (0, i)], fill=color, width=2)

    lienzo = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    mascara = Image.new("L", (n, n), 0)
    x0, y0, x1, y1, r = FONDO
    ImageDraw.Draw(mascara).rounded_rectangle([k(x0), k(y0), k(x1), k(y1)], radius=k(r), fill=255)
    lienzo.paste(degradado, (0, 0), mascara)

    capa = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    for a, b, c, e, rr, op in MOSAICOS:
        dc.rounded_rectangle([k(a), k(b), k(c), k(e)], radius=k(rr), fill=BLANCO + (round(255 * op),))
    lienzo = Image.alpha_composite(lienzo, capa)

    capa = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    manija = BLANCO + (204,)
    dc.line([k(P0[0]), k(P0[1]), k(C1[0]), k(C1[1])], fill=manija, width=k(4))
    dc.line([k(P3[0]), k(P3[1]), k(C2[0]), k(C2[1])], fill=manija, width=k(4))
    lienzo = Image.alpha_composite(lienzo, capa)

    dl = ImageDraw.Draw(lienzo)
    # la curva se dibuja como una fila de círculos pegados: queda lisa y con puntas redondas
    rad = k(TRAZO) / 2
    for i in range(1201):
        x, y = (k(v) for v in bezier(i / 1200))
        dl.ellipse([x - rad, y - rad, x + rad, y + rad], fill=BLANCO)
    for x, y in (C1, C2):
        dl.ellipse([k(x - 9), k(y - 9), k(x + 9), k(y + 9)], fill=BLANCO)
    for x, y in (P0, P3):
        dl.rounded_rectangle([k(x - 14), k(y - 14), k(x + 14), k(y + 14)], radius=k(6),
                             fill=BLANCO, outline=NOCHE, width=k(5))

    lienzo.resize((TAM, TAM), Image.LANCZOS).save(ruta, optimize=True)


if __name__ == "__main__":
    (AQUI / "logo.svg").write_text(svg(), encoding="utf-8")
    print("logo.svg listo")
    try:
        png(AQUI / "logo.png")
        print("logo.png listo (500x500)")
    except ImportError:
        print("Falta Pillow: el PNG no se generó. Instalalo en un entorno virtual con pip install pillow.")
