#!/usr/bin/env python3
"""Generate downscaled thumbnail tiles for fast quilt loading.
The full quilt has ~2.2GB of phone-camera JPEGs. Serving those at full res makes
the quilt load slowly. This creates a media/thumbs/ dir with ~700px-wide JPEGs
(~80-150KB each) used in the quilt surface; the lightbox still loads the full-res
original. Run from project root.

Usage:  python3 scripts/make_thumbs.py
"""
import os, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
THUMB_W = 700          # max width for quilt tiles
QUALITY = 78

def main():
    src_dirs = [ROOT / 'media' / 'weekend-2026', ROOT / 'media' / 'textures']
    dst = ROOT / 'media' / 'thumbs'
    dst.mkdir(parents=True, exist_ok=True)

    count = 0
    total_before = 0
    total_after = 0
    for src_dir in src_dirs:
        if not src_dir.exists():
            continue
        for f in sorted(src_dir.iterdir()):
            if f.suffix.lower() not in ('.jpg', '.jpeg', '.png', '.heic'):
                continue
            out = dst / (f.stem + '.jpg')
            if out.exists():
                continue
            try:
                im = Image.open(f)
                im.load()
            except Exception as e:
                print(f"  SKIP {f.name}: {e}")
                continue
            total_before += os.path.getsize(f)
            # downscale to max width
            if im.width > THUMB_W:
                ratio = THUMB_W / im.width
                im = im.resize((THUMB_W, int(im.height * ratio)), Image.LANCZOS)
            im.convert('RGB').save(out, 'JPEG', quality=QUALITY, optimize=True)
            total_after += os.path.getsize(out)
            count += 1

    print(f"Created {count} thumbnails in {dst}/")
    print(f"Total original: {round(total_before/1024/1024,1)}MB → thumbs: {round(total_after/1024/1024,1)}MB")
    print("Now point layout tiles at media/thumbs/<name>.jpg and the lightbox at the originals.")

if __name__ == '__main__':
    main()
