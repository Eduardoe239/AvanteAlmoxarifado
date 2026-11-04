"""Gera as versões da logo Avante Tech Jr sem fundo, a partir da imagem enviada.

Saídas em <saida>/:
  - logo-avantetechjr-ciano.svg / .png        (para fundos escuros: marca, login, splash)
  - logo-avantetechjr-navy.svg / .png         (para fundos claros)
  - logo-avantetechjr-branca.svg / .png       (sobre a cor de marca ou fotos)
  - simbolo-avante-*.svg / .png               (só o "A", para ícone do app, favicon e etiquetas)
  - icone-app-512.png / icone-app-maskable-512.png / favicon-32.png
Uso: python logo_build.py <entrada.png> <saida_dir>
"""
import sys
from pathlib import Path

import numpy as np
import potrace
from PIL import Image

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)

im = np.array(Image.open(src).convert("RGB")).astype(float)
h, w, _ = im.shape

# Fundo é um degradê horizontal (esquerda escura -> direita índigo): modelo linear por coluna.
left = im[:, :6].reshape(-1, 3).mean(0)
right = im[:, -6:].reshape(-1, 3).mean(0)
t = np.linspace(0, 1, w)[None, :, None]
bg = left * (1 - t) + right * t
FG = np.array([19, 241, 252], float)  # ciano mediano medido na logo

# Alfa pelo canal verde (onde ciano e fundo mais se diferem), descontando o fundo local.
alpha = np.clip((im[..., 1] - bg[..., 1]) / (FG[1] - bg[..., 1]), 0, 1)

ys, xs = np.where(alpha > 0.05)
pad = 6
y0, y1, x0, x1 = max(ys.min() - pad, 0), min(ys.max() + pad, h), max(xs.min() - pad, 0), min(xs.max() + pad, w)
alpha = alpha[y0:y1, x0:x1]

# Separa símbolo (A) do texto: maior faixa vazia horizontal entre os dois.
rows = (alpha > 0.3).any(1)
gaps, start = [], None
for i, r in enumerate(rows):
    if not r and start is None:
        start = i
    if r and start is not None:
        gaps.append((start, i)); start = None
cut = max(gaps, key=lambda g: g[1] - g[0])  # vão entre o "A" e "AVANTE"
def fill_holes(a: np.ndarray) -> np.ndarray:
    """Preenche furos internos (trilhas de circuito de ~1 px, irrecuperáveis nesta resolução).
    Fundo = região conectada à borda; qualquer outro vazio vira tinta."""
    from PIL import ImageDraw
    m = Image.fromarray(((a > 0.5) * 255).astype(np.uint8)).convert("L")
    m = Image.fromarray(np.pad(np.array(m), 1)).copy()  # borda livre; copy() torna a imagem gravável
    ImageDraw.floodfill(m, (0, 0), 128)
    arr = np.array(m)[1:-1, 1:-1]
    solid = arr != 128  # tudo que não é fundo externo
    return np.where(solid, np.maximum(a, 1.0 * solid), a)

# Símbolo simplificado (sem trilhas); o texto mantém os vãos das letras (A, R).
alpha[: cut[0] + 2] = fill_holes(alpha[: cut[0] + 2])
symbol_alpha = alpha[: cut[0] + 2]

SCALE = 8  # traça numa versão ampliada para curvas mais suaves


def trace(a: np.ndarray) -> tuple[str, int, int]:
    big = Image.fromarray((a * 255).astype(np.uint8)).resize((a.shape[1] * SCALE, a.shape[0] * SCALE), Image.LANCZOS)
    bmp = potrace.Bitmap(np.array(big) <= 127)  # potracer traça o valor False como tinta
    path = bmp.trace(turdsize=2, alphamax=1.0, opticurve=True, opttolerance=0.2)
    d = []
    for curve in path:
        d.append(f"M{curve.start_point.x:.1f},{curve.start_point.y:.1f}")
        for seg in curve.segments:
            if seg.is_corner:
                d.append(f"L{seg.c.x:.1f},{seg.c.y:.1f}L{seg.end_point.x:.1f},{seg.end_point.y:.1f}")
            else:
                d.append(f"C{seg.c1.x:.1f},{seg.c1.y:.1f} {seg.c2.x:.1f},{seg.c2.y:.1f} {seg.end_point.x:.1f},{seg.end_point.y:.1f}")
        d.append("Z")
    return "".join(d), big.width, big.height


def write_svg(d: str, vw: int, vh: int, color: str, name: str, title: str) -> Path:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vw} {vh}" role="img" aria-labelledby="t">'
           f'<title id="t">{title}</title><path fill="{color}" fill-rule="evenodd" d="{d}"/></svg>\n')
    p = out / name
    p.write_text(svg)
    return p


COLORS = {"ciano": "#13F1FC", "navy": "#10243E", "branca": "#FFFFFF"}
full_d, fw, fh = trace(alpha)
sym_d, sw, sh = trace(symbol_alpha)

import subprocess

for cname, col in COLORS.items():
    for d, vw, vh, base, title in ((full_d, fw, fh, "logo-avantetechjr", "Avante Tech Jr"),
                                   (sym_d, sw, sh, "simbolo-avante", "Avante")):
        svg = write_svg(d, vw, vh, col, f"{base}-{cname}.svg", title)
        subprocess.run(["rsvg-convert", "-w", "1024", "-o", str(out / f"{base}-{cname}.png"), str(svg)], check=True)

# Ícone do app: símbolo ciano sobre o degradê da marca; maskable com área segura de 80%.
def app_icon(size: int, safe: float, name: str) -> None:
    grad = np.zeros((size, size, 3), float)
    tt = np.linspace(0, 1, size)[None, :, None]
    grad[:] = np.array([25, 18, 86]) * (1 - tt) + np.array([49, 46, 185]) * tt
    canvas = Image.fromarray(grad.astype(np.uint8)).convert("RGBA")
    sym = Image.open(out / "simbolo-avante-ciano.png").convert("RGBA")
    box = int(size * safe)
    sym.thumbnail((box, box), Image.LANCZOS)
    canvas.alpha_composite(sym, ((size - sym.width) // 2, (size - sym.height) // 2))
    canvas.convert("RGB").save(out / name)

app_icon(512, 0.62, "icone-app-512.png")
app_icon(512, 0.50, "icone-app-maskable-512.png")   # cabe no círculo de 80% do padrão maskable
app_icon(192, 0.62, "icone-app-192.png")
Image.open(out / "icone-app-192.png").resize((32, 32), Image.LANCZOS).save(out / "favicon-32.png")

print("cortes:", (y0, y1, x0, x1), "vão símbolo/texto:", cut)
for p in sorted(out.iterdir()):
    print(f"{p.name:40s} {p.stat().st_size:>8d} bytes")
