#!/usr/bin/env python3
"""Generate a rich patchwork-fabric backing for the quilt viewer.

Replaces the ~693 per-tile DOM backing nodes with a SINGLE CSS background image
on #surface. Composes a MOSAIC of irregular, varied-size cloth patches (drawn
from source fabric-texture strips, each colour-graded) with soft, fine seams
blending into the dark site background (#1a120b). A gentle vignette + light
fabric grain finish it so it reads as hand-sewn cloth — not a mechanical grid.
"""
import os, random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THUMBS = os.path.join(ROOT, 'media', 'thumbs')
OUT = os.path.join(ROOT, 'assets', 'img', 'backing-patchwork.jpg')

TEXTURES = [
    'PXL_234825299_tex.jpg', 'IMG_0057b.jpg', 'PXL_230910285~2.jpg',
    'PXL_215908225_tex.jpg', 'PXL_230910285_tex.jpg', 'PXL_215919709_tex.jpg',
    'PXL_texture.jpg', 'PXL_010029509_tex.jpg', 'PXL_215901711_tex.jpg',
    'IMG_0057.jpg', 'PXL_225807164_tex.jpg', 'IMG_0053.jpg',
]

TILE = 1280            # repeating tile size (matches backgroundSize in viewer.js)
MIN_DIM = 120          # smallest allowed patch dimension (px)
TARGET_PATCHES = 26    # ~ number of irregular patches per tile
SEAM = 4               # fine seam width (px)
BG = (30, 21, 13)      # soft dark base, blends with #1a120b
VIGNETTE = 0.24        # gentle edge darkening (do NOT crush the fabric)


def cover_crop(im, w, h):
    """Cover-fit im into (w,h) with slight zoom variety."""
    iw, ih = im.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    im = im.resize((nw, nh), Image.LANCZOS)
    left = random.randint(0, max(0, nw - w))
    top = random.randint(0, max(0, nh - h))
    return im.crop((left, top, left + w, top + h))


def grade(patch):
    """Vary brightness/contrast/saturation so each patch reads as a distinct
    scrap of cloth rather than one repeated texture."""
    patch = ImageEnhance.Brightness(patch).enhance(random.uniform(0.92, 1.25))
    patch = ImageEnhance.Contrast(patch).enhance(random.uniform(0.88, 1.2))
    patch = ImageEnhance.Color(patch).enhance(random.uniform(0.85, 1.35))
    return patch


def mosaic(rects, target):
    """Recursively split rectangles to build an irregular patchwork layout."""
    while len(rects) < target:
        candidates = [i for i, (x, y, w, h) in enumerate(rects)
                      if w >= 2 * MIN_DIM and h >= 2 * MIN_DIM]
        if not candidates:
            break
        i = random.choice(candidates)
        x, y, w, h = rects[i]
        if random.random() < 0.5 or h < 2 * MIN_DIM:
            cut = random.randint(MIN_DIM, w - MIN_DIM)   # vertical split
            rects[i] = (x, y, cut, h)
            rects.append((x + cut, y, w - cut, h))
        else:
            cut = random.randint(MIN_DIM, h - MIN_DIM)   # horizontal split
            rects[i] = (x, y, w, cut)
            rects.append((x, y + cut, w, h - cut))
    return rects


def seam_mask(w, h):
    """White band along the top+left edge of a patch -> stitched highlight."""
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    d.rectangle([0, 0, w, min(h, 2)], fill=110)
    d.rectangle([0, 0, min(w, 2), h], fill=110)
    return m.filter(ImageFilter.GaussianBlur(1.0))


def main():
    random.seed(20260825)
    canvas = Image.new('RGB', (TILE, TILE), BG)

    for (x, y, w, h) in mosaic([(0, 0, TILE, TILE)], TARGET_PATCHES):
        src = random.choice(TEXTURES)
        im = Image.open(os.path.join(THUMBS, src)).convert('RGB')
        pw, ph = w - SEAM * 2, h - SEAM * 2
        patch = grade(cover_crop(im, pw, ph))

        # subtle stitched highlight along top+left edge of the patch
        hl = ImageEnhance.Brightness(patch).enhance(1.25)
        canvas.paste(hl, (x + SEAM, y + SEAM), mask=seam_mask(pw, ph))
        canvas.paste(patch, (x + SEAM, y + SEAM))

    # soft vignette so the repeat blends into the dark surround
    mask = Image.new('L', (TILE, TILE), 0)
    dm = ImageDraw.Draw(mask)
    dm.ellipse((-TILE * 0.4, -TILE * 0.4, TILE * 1.4, TILE * 1.4), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(TILE * 0.30))
    dk = Image.new('RGB', (TILE, TILE), (18, 12, 7))
    canvas = Image.composite(canvas, dk, mask.point(lambda v: int(v * (1 - VIGNETTE) + VIGNETTE * 255)))

    # light ADDITIVE fabric grain (kept subtle, never darkens the cloth)
    grain = Image.effect_noise((TILE, TILE), 14).convert('L')
    grain = grain.point(lambda v: v // 6)              # 0..~90, gentle
    canvas = ImageChops.add(canvas, grain.convert('RGB'))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    canvas.save(OUT, 'JPEG', quality=84, optimize=True)
    print('wrote', OUT, canvas.size, os.path.getsize(OUT), 'bytes')


if __name__ == '__main__':
    main()
