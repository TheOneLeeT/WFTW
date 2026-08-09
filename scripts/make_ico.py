#!/usr/bin/env python3
"""Write a proper multi-resolution Windows .ico file."""

import struct
from pathlib import Path
from PIL import Image

SRC = Path("Media/Icon/WFTW.tif")
OUT = Path("Media/Icon/WFTW.ico")

src = Image.open(SRC).convert("RGBA")
sizes = [16, 32, 48, 64, 128, 256]

# Prepare images
images = []
for s in sizes:
    img = src.resize((s, s), Image.LANCZOS)
    # Save as PNG in memory
    buf = img.tobytes()
    images.append((s, buf, img.mode))

# ICO format:
# ICONDIR: 6 bytes
# ICONDIRENTRY: 16 bytes each
# Then PNG data for each image

num = len(images)
header = struct.pack("<HHH", 0, 1, num)  # Reserved, type=1 (ICO), count

entries = b""
offset = 6 + 16 * num
png_data = []

for s, buf, mode in images:
    img = src.resize((s, s), Image.LANCZOS)
    # Save as PNG to bytes
    import io
    png_buf = io.BytesIO()
    img.save(png_buf, format="PNG")
    png_bytes = png_buf.getvalue()
    png_data.append(png_bytes)

    w = s
    h = s
    colors = 0 if mode == "RGBA" else 256
    entry = struct.pack(
        "<BBBBHHII",
        w,        # width
        h,        # height
        colors,   # color palette
        0,        # reserved
        0,        # color planes
        32,       # bits per pixel
        len(png_bytes),  # size of image data
        offset,   # offset
    )
    entries += entry
    offset += len(png_bytes)

with open(OUT, "wb") as f:
    f.write(header)
    f.write(entries)
    for data in png_data:
        f.write(data)

print(f"Created {OUT} with {num} resolutions: {sizes}")
