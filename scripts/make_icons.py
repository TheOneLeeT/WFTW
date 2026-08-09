#!/usr/bin/env python3
"""Generate high-quality platform icons from WFTW.tif source."""

from pathlib import Path
from PIL import Image

SRC = Path("Media/Icon/WFTW.tif")
OUT_DIR = Path("Media/Icon")
ASSETS_DIR = Path("assets")

print(f"Opening source: {SRC}")
src_img = Image.open(SRC)
print(f"  Mode: {src_img.mode}, Size: {src_img.size}")

# Convert to RGBA if needed
if src_img.mode != "RGBA":
    src_img = src_img.convert("RGBA")

# Ensure source is at least 1024x1024 for highest quality
if src_img.size[0] < 1024 or src_img.size[1] < 1024:
    src_img = src_img.resize((1024, 1024), Image.LANCZOS)

# ============================================================
# Windows .ico (multiple resolutions embedded)
# ============================================================
win_sizes = [16, 32, 48, 64, 128, 256]
win_ico = OUT_DIR / "WFTW.ico"
ico_images = []
for size in win_sizes:
    img = src_img.resize((size, size), Image.LANCZOS)
    ico_images.append(img)
ico_images[0].save(
    win_ico,
    format="ICO",
    sizes=[(s, s) for s in win_sizes],
)
print(f"Created {win_ico} with sizes: {win_sizes}")

# ============================================================
# macOS .icns (multiple resolutions embedded)
# ============================================================
mac_sizes = [16, 32, 64, 128, 256, 512, 1024]
mac_icns = OUT_DIR / "WFTW.icns"
try:
    icns_images = []
    for size in mac_sizes:
        img = src_img.resize((size, size), Image.LANCZOS)
        icns_images.append(img)
    icns_images[0].save(
        mac_icns,
        format="ICNS",
        sizes=[(s, s) for s in mac_sizes],
    )
    print(f"Created {mac_icns} with sizes: {mac_sizes}")
except Exception as e:
    print(f"ICNS creation failed: {e}")
    print("Falling back to high-quality PNG for macOS")
    fallback = src_img.resize((1024, 1024), Image.LANCZOS)
    fallback.save(OUT_DIR / "WFTW_macos_1024.png", format="PNG")

# ============================================================
# Linux / general high-quality PNG
# ============================================================
linux_png = OUT_DIR / "WFTW.png"
png_img = src_img.resize((512, 512), Image.LANCZOS)
png_img.save(linux_png, format="PNG", optimize=True)
print(f"Created {linux_png} at 512x512")

# ============================================================
# Copy to assets/ for Flet build
# ============================================================
ASSETS_DIR.mkdir(exist_ok=True)
import shutil
shutil.copy2(win_ico, ASSETS_DIR / "icon_windows.ico")
shutil.copy2(linux_png, ASSETS_DIR / "icon.png")
print(f"Copied icons to {ASSETS_DIR}/")

print("Done.")
