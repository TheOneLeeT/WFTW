#!/usr/bin/env python3
"""Generate platform icons from pre-rendered SVGs in Media/Icon/svg/."""

from pathlib import Path
import io
import struct
import shutil
import subprocess

from PIL import Image

SVG_DIR = Path("Media/Icon/svg")
PNG_DIR = Path("Media/Icon/png")
ICO_DIR = Path("Media/Icon/ico")
ICNS_DIR = Path("Media/Icon/icns")
ASSETS_DIR = Path("assets")
INKSCAPE = Path(r"C:\Program Files\Inkscape\bin\inkscape.exe")

# Ensure output directories exist
for d in [PNG_DIR, ICO_DIR, ICNS_DIR, ASSETS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ============================================================
# Helper: convert SVG to PNG via Inkscape CLI
# ============================================================
def svg_to_png(svg_path: Path, png_path: Path, size: int):
    subprocess.run(
        [
            str(INKSCAPE),
            str(svg_path),
            "--export-type=png",
            f"--export-filename={png_path}",
            "-w", str(size),
            "-h", str(size),
        ],
        check=True,
        capture_output=True,
    )

# ============================================================
# Convert all SVGs to PNGs
# ============================================================
print("Converting SVGs to PNGs...")
for svg_file in SVG_DIR.glob("*.svg"):
    if "x" not in svg_file.stem:
        continue
    png_file = PNG_DIR / f"{svg_file.stem}.png"
    if png_file.exists():
        continue
    size = int(svg_file.stem.split("x")[0])
    svg_to_png(svg_file, png_file, size)
    print(f"  {svg_file.name} -> {png_file.name}")

print("SVG to PNG conversion done.")

# ============================================================
# Windows .ico (multiple resolutions embedded)
# ============================================================
win_sizes = [16, 32, 48, 64, 128, 256]
ico_path = ICO_DIR / "WFTW.ico"

pngs = []
for size in win_sizes:
    png_file = PNG_DIR / f"{size}x{size}.png"
    if not png_file.exists():
        raise FileNotFoundError(f"Missing PNG: {png_file}")
    pngs.append((size, png_file.read_bytes()))

num = len(pngs)
header = struct.pack("<HHH", 0, 1, num)
entries = b""
offset = 6 + 16 * num
for size, png in pngs:
    w = 0 if size == 256 else size
    h = 0 if size == 256 else size
    entry = struct.pack(
        "<BBBBHHII",
        w, h, 0, 0, 0, 32, len(png), offset
    )
    entries += entry
    offset += len(png)

with open(ico_path, "wb") as f:
    f.write(header)
    f.write(entries)
    for _, png in pngs:
        f.write(png)

print(f"Created {ico_path} with sizes: {win_sizes}")

# ============================================================
# macOS .icns (multiple resolutions embedded)
# ============================================================
mac_sizes = [16, 32, 64, 128, 256, 512, 1024]
icns_path = ICNS_DIR / "WFTW.icns"

icns_images = []
for size in mac_sizes:
    png_file = PNG_DIR / f"{size}x{size}.png"
    if not png_file.exists():
        raise FileNotFoundError(f"Missing PNG: {png_file}")
    img = Image.open(png_file).convert("RGBA")
    icns_images.append(img)

icns_images[0].save(
    icns_path,
    format="ICNS",
    sizes=[(s, s) for s in mac_sizes],
)
print(f"Created {icns_path} with sizes: {mac_sizes}")

# ============================================================
# Copy to assets/ for Flet build
# ============================================================
shutil.copy2(ico_path, ASSETS_DIR / "icon_windows.ico")
shutil.copy2(PNG_DIR / "512x512.png", ASSETS_DIR / "icon.png")
print(f"Copied icons to {ASSETS_DIR}/")

print("Done.")

