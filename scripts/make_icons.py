#!/usr/bin/env python3
"""Generate high-quality platform icons from WFTW.svg using Inkscape."""

from pathlib import Path
import io
import struct
import shutil
import subprocess

from PIL import Image

SRC = Path("Media/Icon/WFTW.svg")
OUT_DIR = Path("Media/Icon")
ASSETS_DIR = Path("assets")
INKSCAPE = Path(r"C:\Program Files\Inkscape\bin\inkscape.exe")

print(f"Opening source: {SRC}")
print(f"  SVG size: {SRC.stat().st_size} bytes")

# Ensure output directories exist
OUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# Helper: render SVG at requested size via Inkscape CLI
# ============================================================
def render_svg_to_png(size: int) -> bytes:
    out = OUT_DIR / f"_tmp_{size}.png"
    subprocess.run(
        [
            str(INKSCAPE),
            str(SRC),
            "--export-type=png",
            f"--export-filename={out}",
            "-w", str(size),
            "-h", str(size),
        ],
        check=True,
        capture_output=True,
    )
    data = out.read_bytes()
    out.unlink()
    return data

# ============================================================
# Windows .ico (multiple resolutions embedded)
# ============================================================
win_sizes = [16, 32, 48, 64, 128, 256]
ico_path = OUT_DIR / "WFTW.ico"

pngs = []
for size in win_sizes:
    png = render_svg_to_png(size)
    pngs.append((size, png))

# Build multi-resolution ICO manually
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
icns_path = OUT_DIR / "WFTW.icns"

icns_images = []
for size in mac_sizes:
    png = render_svg_to_png(size)
    img = Image.open(io.BytesIO(png)).convert("RGBA")
    icns_images.append(img)

icns_images[0].save(
    icns_path,
    format="ICNS",
    sizes=[(s, s) for s in mac_sizes],
)
print(f"Created {icns_path} with sizes: {mac_sizes}")

# ============================================================
# Linux / general high-quality PNG
# ============================================================
linux_png = OUT_DIR / "WFTW.png"
linux_size = 1024
linux_png_data = render_svg_to_png(linux_size)
linux_img = Image.open(io.BytesIO(linux_png_data)).convert("RGBA")
linux_img.save(linux_png, format="PNG", optimize=True)
print(f"Created {linux_png} at {linux_size}x{linux_size}")

# ============================================================
# Copy to assets/ for Flet build
# ============================================================
shutil.copy2(ico_path, ASSETS_DIR / "icon_windows.ico")
shutil.copy2(linux_png, ASSETS_DIR / "icon.png")
print(f"Copied icons to {ASSETS_DIR}/")

print("Done.")
