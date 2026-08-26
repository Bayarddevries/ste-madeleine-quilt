#!/usr/bin/env python3
"""Generate a seamless repeating patchwork-texture backing for the quilt viewer.

Replaces the ~693 per-tile DOM backing nodes with a SINGLE CSS background image
on #surface. Composes a grid of cover-cropped fabric patches (drawn from the
source texture strips) into one repeating image. Straight grid seams read as a
quilt; the image tiles seamlessly in both axes.
"""
import os, random
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THUMBS = os.path.join(ROOT, 'media', 'thumbs')
OUT = os.path.join(ROOT, 'assets', 'img', 'backing-patchwork.jpg')

TEXTURES = [
    'PXL_234825299_tex.jpg', 'IMG_0057b.jpg', 'PXL_230910285~2.jpg',
    'PXL_215908225_tex.jpg', 'PXL_230910285_tex.jpg', 'PXL_215919709_tex.jpg',
    'PXL_texture.jpg', 'PXL_010029509_tex.jpg', 'PXL_215901711_tex.jpg',
    'IMG_0057.jpg', 'PXL_225807164_tex.jpg', 'IMG_0053.jpg',
]

COLS, ROWS = 5, 5      # 5x5 grid of patches -> 25 pieces
CELL = 144             # patch size in px
SEAM = 6               # dark seam border width between patches
VIGNETTE = 0.30        # edge-darkening to blend with the dark site bg

def cover_crop(im, size):
    """Cover-fit a square crop from im into (size,size)."""
    w, h = im.size
    s = min(w, h)
    left = random.randint(0, w - s)
    top = random.randint(0, max(1, h - s))
    sq = im.crop((left, top, left + s, top + s))
    return sq.resize((size, size), Image.LANCZOS)

def main():
    W, H = COLS * CELL, ROWS * CELL
    canvas = Image.new('RGB', (W, H), (18, 12, 6))
    draw = ImageDraw.Draw(canvas)

    for r in range(ROWS):
        for c in range(COLS):
            src = TEXTURES[(r * COLS + c) % len(TEXTURES)]
            im = Image.open(os.path.join(THUMBS, src)).convert('RGB')
            patch = cover_crop(im, CELL - SEAM * 2)
            x = c * CELL + SEAM
            y = r * CELL + SEAM
            canvas.paste(patch, (x, y))

    # soft vignette so patch edges blend into the dark surround
    mask = Image.new('L', (W, H), 0)
    dm = ImageDraw.Draw(mask)
    dm.ellipse((-W * 0.3, -H * 0.3, W * 1.3, H * 1.3), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(W * 0.35))
    dark = Image.new('RGB', (W, H), (16, 10, 5))
    canvas = Image.composite(canvas, dark, mask.point(lambda v: int(v * (1 - VIGNETTE) + VIGNETTE * 255)))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    canvas.save(OUT, 'JPEG', quality=78, optimize=True)
    print('wrote', OUT, canvas.size, os.path.getsize(OUT), 'bytes')

if __name__ == '__main__':
    main()
