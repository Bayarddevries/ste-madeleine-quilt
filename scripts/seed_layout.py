#!/usr/bin/env python3
"""Ste. Madeleine Quilt — organic quilt seed layout generator.
Packs tiles interconnected (edges touching/overlapping, staggered, NOT a grid),
preserving original aspect ratios. Lay out in a gentle narrative flow across the
free-pan 2D canvas.

NOTE on people-vs-land: filenames don't reliably separate people from land/plant
shots (PXL/_MG_/IMG all contain both). That classification is Bayard's curation
job in the editor (Kind: People/Land toggle). This seed defaults every tile to
'kind':'people'; mark the land/plant/cemetery/landscape shots as Land in the editor.

The result is a STARTING POINT that Bayard rearranges in the editor.
Run:  python3 scripts/seed_layout.py

Reclamation band v4:
  * Photos/videos/audio are placed in STAGGERED COLUMNS with small SEAMS
    (6-10px gaps) instead of stacked overlaps — so pieces don't pile on each
    other. Organic/non-grid: varied sizes, column widths, jitter, rotation (-3..3),
    staggered column tops. Original aspect ratios preserved exactly.
  * A TEXTURE BACKING layer sits behind all photos: MANY small texture tiles
    (~170-250px, patchwork style) tiled across the full surface bbox at z=0,
    mixed from the 12 texture files. Photos sit on top at z=1. The small seams
    between photos reveal the backing = reads as stitching/cloth between pieces.
"""
import json, random, os, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TILES = json.load(open(ROOT / 'quilt-tiles.json'))
OUT = ROOT / 'layout.json'

def probe_aspect():
    from PIL import Image
    asp = {}
    for t in TILES:
        p = ROOT / t['src']
        if p.exists():
            try:
                im = Image.open(p)
                asp[t['src']] = im.size[0] / im.size[1]
            except Exception:
                pass
    return asp

def tile_from_manifest(t, aspect):
    src = t['src']
    ar = aspect.get(src, 1.0)
    # deterministic per-src seed (NOT hash(), which is randomized per process)
    seed = int.from_bytes(hashlib.md5(src.encode()).digest()[:4], 'big')
    rng = random.Random(seed)
    base = rng.choice([140, 160, 180, 200, 240, 280, 320, 380, 420])
    # Preserve aspect EXACTLY: size the long side from `base`, derive the short side
    # by rounding. If the short side would fall below min_px, instead fix the short
    # side at min_px and size the long side from it (no ratio-breaking clamp).
    min_px = 60
    if ar >= 1:  # landscape / panorama
        long_side = base
        short_side = int(round(long_side / ar))
        if short_side < min_px:
            short_side = min_px
            long_side = int(round(min_px * ar))
        w, h = long_side, short_side
    else:        # portrait
        long_side = base
        short_side = int(round(long_side * ar))
        if short_side < min_px:
            short_side = min_px
            long_side = int(round(min_px / ar))
        w, h = short_side, long_side
    thumb = 'media/thumbs/' + os.path.basename(src)
    if not os.path.exists(ROOT / thumb):
        thumb = src
    return {'id': t.get('id'), 'src': thumb, 'fullSrc': src, 'type': t.get('type', 'photo'),
            'kind': 'people',
            'w': max(w, 60), 'h': max(h, 60),
            'caption': t.get('cap', 'Ste. Madeleine Métis Days 2026'),
            'title': t.get('title', '')}


def pack_reclamation_columns(tiles, start_x, start_y, rng):
    """Staggered-column packing with SEAMS (gaps), not overlaps.
    Each column is a vertical strip whose width = its widest tile + seam margin,
    so columns never overlap horizontally. Within a column tiles are stacked with
    6-10px gaps (never overlapping vertically). Column tops are staggered and widths
    vary -> organic, non-grid. Tiles keep exact aspect. Returns list of
    (tile, x, y, w, h, rotate)."""
    ncol = rng.randint(6, 8)
    cols = [[] for _ in range(ncol)]
    sh = tiles[:]
    rng.shuffle(sh)
    for i, t in enumerate(sh):
        cols[i % ncol].append(t)

    placed = []
    x_cursor = start_x
    for ci, col in enumerate(cols):
        if not col:
            continue
        max_w = max(t['w'] for t in col)
        col_w = max_w + 12                      # widest tile + seam margin
        cx = x_cursor + rng.randint(0, 10)      # horizontal stagger
        cy = start_y + rng.randint(-60, 80)     # staggered column top
        y = cy
        for t in col:
            tw, th = t['w'], t['h']
            rot = rng.randint(-3, 3)
            # x jitter, clamped so tile stays inside its column (no cross-col overlap)
            slack = max(0, col_w - tw)
            jx = cx + rng.randint(-slack // 2, slack // 2)
            placed.append((t, jx, y, tw, th, rot))
            y += th + rng.randint(6, 10)        # SEAM between stacked photos
        x_cursor = cx + col_w + rng.randint(10, 20)
    return placed


def build_backing(content, textures, rng):
    """Tile MANY small texture pieces (patchwork backing) across the full bbox of
    `content` at z=0. Small jittered pieces with 2-4px gaps read as varied cloth,
    NOT one stretched blurry texture. Returns backing tile dicts (z=0)."""
    if not content or not textures:
        return []
    min_x = min(t['x'] for t in content) - 30
    min_y = min(t['y'] for t in content) - 30
    max_x = max(t['x'] + t['w'] for t in content) + 30
    max_y = max(t['y'] + t['h'] for t in content) + 30

    backing = []
    gap = rng.randint(2, 4)
    tmin, tmax = 170, 250
    x = min_x
    idx = 0
    while x < max_x:
        y = min_y
        row_w = rng.randint(tmin, tmax)         # column of consistent width
        while y < max_y:
            th = rng.randint(tmin, tmax)        # varied height per piece
            tex = rng.choice(textures)
            jx = x + rng.randint(-4, 4)
            jy = y + rng.randint(-4, 4)
            backing.append({
                'id': 'back-%d' % idx, 'type': 'texture', 'src': tex,
                'x': int(jx), 'y': int(jy), 'w': row_w, 'h': th,
                'z': 0, 'rotate': rng.randint(-2, 2), 'rx': 0,
                'caption': 'backing'})
            idx += 1
            y += th + gap
        x += row_w + gap
    return backing


def build():
    aspect = probe_aspect()
    rng = random.Random(7)

    photos = [t for t in TILES if t['type'] == 'photo']
    videos = [t for t in TILES if t['type'] == 'video']
    audios = [t for t in TILES if t['type'] == 'audio']
    scans  = [t for t in TILES if t['type'] == 'sphere']
    rng.shuffle(photos)

    # texture files: mixed patchwork backing
    tex_dir = ROOT / 'media' / 'textures'
    textures = []
    if tex_dir.exists():
        for f in sorted(tex_dir.iterdir()):
            if f.suffix.lower() in ('.jpg', '.jpeg', '.png'):
                rel = str(f.relative_to(ROOT))
                thumb = 'media/thumbs/' + f.stem + '.jpg'
                textures.append(thumb if (ROOT / thumb).exists() else rel)
    if not textures:
        textures = ['media/ste-madeleine-sign-tile.png']

    sections = []

    # ---- Band 0: Story (title + a few land-like frames) ---- KEEP INTACT
    opening = photos[:3]
    hist_tiles = []
    x, y = 60, 60
    hist_tiles.append({'id':'h0','type':'text','src':None,'w':460,'h':120,'x':x,'y':y,
                       'text':'The community, the land, the loss, the reclamation.',
                       'fontSize':26,'z':2,'rotate':0})
    x += 480
    for p in opening:
        t = tile_from_manifest(p, aspect)
        t['x']=x; t['y']=y+rng.randint(0,20); x+=t['w']+6
        t['rotate']=rng.choice([-2,-1,1,2]); t['rx']=8
        t['z']=1
        hist_tiles.append(t)
    sections.append({'id':'band-story','title':'The Story','chapter':1,'designWidth':1600,
                     'height':420,'tiles':hist_tiles})

    # ---- Band 1: Reclamation — photos + videos + audio, seams + texture backing ----
    # exclude the 3 photos already used in the Story band so each id appears once
    opening_ids = {p.get('id') for p in opening}
    rest_photos = [p for p in photos if p.get('id') not in opening_ids]
    pool = [('photo', p) for p in rest_photos] + [('video', v) for v in videos] + [('audio', a) for a in audios]
    rng.shuffle(pool)
    seq_tiles = [tile_from_manifest(m, aspect) for _, m in pool]
    for (kind, m), t in zip(pool, seq_tiles):
        if kind == 'video': t['type'] = 'video'
        elif kind == 'audio': t['type'] = 'audio'; t['cover'] = 'media/ste-madeleine-sign-tile.png'

    placed = pack_reclamation_columns(seq_tiles, 60, 60, rng)
    content = []
    for (t, px, py, pw, ph, rot) in placed:
        t['x']=int(px); t['y']=int(py); t['w']=int(pw); t['h']=int(ph)
        t['z']=1
        t['rotate']=rot
        t['rx']=3   # subtle, not pill-shaped
        content.append(t)

    # scans to the right of the packed block
    sx = max((t['x']+t['w'] for t in content), default=60) + 40
    for sc in scans:
        t = tile_from_manifest(sc, aspect); t['type']='scan'; t['poster']='media/ste-madeleine-sign-tile.png'
        t['x']=sx; t['y']=120; t['z']=1; t['rotate']=rng.randint(-2,2); t['rx']=3
        sx += t['w']+20
        content.append(t)

    # TEXTURE BACKING: many small patchwork tiles at z=0 covering full bbox
    backing = build_backing(content, textures, rng)
    reclam_tiles = backing + content
    sections.append({'id':'band-reclamation','title':'Reclamation','chapter':2,'designWidth':1600,
                     'height':640,'tiles':reclam_tiles})

    return {'sections': sections, 'meta': {
        'title': 'Ste. Madeleine — A Quilt of Memory & Reclamation',
        'generated': 'organic-seed-v4',
        'note': 'Free-pan 2D quilt. Reclamation photos sit with seams on a patchwork texture backing (z=0); photos z=1. Rearrange + mark land tiles (Kind: Land) in the editor.'
    }}


def _overlap(a, b):
    return (min(a['x']+a['w'], b['x']+b['w']) - max(a['x'], b['x']) > 0 and
            min(a['y']+a['h'], b['y']+b['h']) - max(a['y'], b['y']) > 0)


def main():
    layout = build()
    OUT.write_text(json.dumps(layout, indent=2))
    n = sum(len(s['tiles']) for s in layout['sections'])
    print(f"Wrote {OUT} — {len(layout['sections'])} bands, {n} tiles")
    from collections import Counter
    for s in layout['sections']:
        print(f"  {s['title']}: {dict(Counter(t['type'] for t in s['tiles']))} ({len(s['tiles'])} tiles)")

    # aspect check: verify each tile preserves its TRUE source aspect (via fullSrc,
    # not the display thumb which can differ by a pixel of rounding)
    from PIL import Image
    aspect = probe_aspect()
    bad = 0
    for s in layout['sections']:
        for t in s['tiles']:
            if t.get('fullSrc') and t['type'] in ('photo','video'):
                fs = t['fullSrc']
                if fs in aspect:
                    ar = aspect[fs]
                    if abs((t['w']/t['h']) - ar) > 0.02:
                        bad += 1
    print(f"Aspect-ratio mismatches (vs true source): {bad}")

    # verification: Reclamation band
    rec = [t for t in layout['sections'][1]['tiles']]
    content = [t for t in rec if t['type'] != 'texture']
    backing = [t for t in rec if t['type'] == 'texture']
    ov = sum(1 for i in range(len(content)) for j in range(i+1, len(content))
             if _overlap(content[i], content[j]))
    print(f"Reclamation: content={len(content)} backing={len(backing)} "
          f"photo-photo overlaps={ov}")
    if content:
        bx0=min(t['x'] for t in content); by0=min(t['y'] for t in content)
        bx1=max(t['x']+t['w'] for t in content); by1=max(t['y']+t['h'] for t in content)
        bb_area=(bx1-bx0)*(by1-by0)
        def rect_area(t): return max(0, t['w'])*max(0,t['h'])
        # coverage = union area of content + backing / bbox area (discretized grid)
        G=12
        cov=0; tot=(bx1-bx0)*(by1-by0)//(G*G)+1
        for cx0 in range(bx0, bx1, G):
            for cy0 in range(by0, by1, G):
                x1=cx0+G; y1=cy0+G
                hit=False
                for t in rec:
                    if (min(t['x']+t['w'],x1)-max(t['x'],cx0)>0 and
                        min(t['y']+t['h'],y1)-max(t['y'],cy0)>0):
                        hit=True; break
                if hit: cov+=1
        print(f"Reclamation bbox=({bx0},{by0})-({bx1},{by1}) "
              f"photo+backing coverage={100.0*cov/tot:.1f}%")
    # z-order check
    z0=sum(1 for t in backing if t['z']==0)
    z1=sum(1 for t in content if t['z']==1)
    print(f"z-order: backing@z0={z0} content@z1={z1}")


if __name__ == '__main__':
    main()
