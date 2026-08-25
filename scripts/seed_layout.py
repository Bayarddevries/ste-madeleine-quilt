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
"""
import json, random, os
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
    rng = random.Random(hash(src) & 0xffff)
    base = rng.choice([140, 160, 180, 200, 240, 280, 320, 380, 420])
    if ar >= 1:
        w, h = base, int(base / ar)
    else:
        w, h = int(base * ar), base
    # use a downscaled thumb for the quilt tile; keep the full-res original for
    # the lightbox (viewer opens data-fullsrc). Thumbs make the quilt load fast.
    import os
    thumb = 'media/thumbs/' + os.path.basename(src)
    if not os.path.exists(ROOT / thumb):
        thumb = src
    return {'id': t.get('id'), 'src': thumb, 'fullSrc': src, 'type': t.get('type', 'photo'),
            'kind': 'people',  # curation flag: 'people'|'land' (default people; mark land in editor)
            'w': max(w, 60), 'h': max(h, 60),
            'caption': t.get('cap', 'Ste. Madeleine Métis Days 2026'),
            'title': t.get('title', '')}


def pack_organic(tiles, textures, start_x, start_y, rng):
    # Staggered column packing: columns start at different y (no aligned rows),
    # tiles varied size/rotate/overlap, textures placed SMALL between clusters.
    placed = []
    # Columns: 6 vertical strips; distribute tiles round-robin for balance
    ncol = 9
    # Assign tiles to columns by shuffling then distributing
    cols = [[] for _ in range(ncol)]
    sh = tiles[:]; rng.shuffle(sh)
    for i,t in enumerate(sh): cols[i % ncol].append(t)
    # Column x positions with small gaps (= seams)
    col_w = 250
    for ci, col in enumerate(cols):
        cx = start_x + ci * (col_w + 4)
        cy = start_y + ci * 90 + rng.randint(-30, 30)  # staggered starts
        # Stack in column with small overlaps and seams
        y_cursor = cy
        # Small texture accent between clusters (every ~5th tile or at column start/end)
        if ci > 0 and textures:
            tex = textures[ci % len(textures)]
            # Small stitch: ~80x40, z=0, near column top
            placed.append((tex if isinstance(tex,str) else tex, cx-20, y_cursor-25, 85, 45, 'stitch'))
        for j,t in enumerate(col):
            tw, th = t['w'], t['h']
            # Slight rotate
            rot = rng.randint(-3, 3)
            # Small overlap with previous (y decreases slightly) or gap
            overlap = rng.choice([14, 20, 30])
            y_cursor = max(start_y, y_cursor - overlap + (6 if j>0 else 0))
            # Slight x jitter within column
            jx = cx + rng.randint(-15, 15)
            placed.append((t, jx, y_cursor, tw, th, 'photo'))
            y_cursor += th - overlap
        # Stitch at bottom of column
        if textures and ci < ncol-1:
            tex = textures[(ci+3)%len(textures)]
            placed.append((tex if isinstance(tex,str) else tex, cx+col_w-40, y_cursor+10, 90, 50, 'stitch'))
    return placed

def build():
    aspect = probe_aspect()
    rng = random.Random(7)

    photos = [t for t in TILES if t['type'] == 'photo']
    videos = [t for t in TILES if t['type'] == 'video']
    audios = [t for t in TILES if t['type'] == 'audio']
    scans  = [t for t in TILES if t['type'] == 'sphere']
    rng.shuffle(photos)

    # texture/filler tiles: the strips that stretch to seal gaps (gapless quilt)
    tex_dir = ROOT / 'media' / 'textures'
    textures = []
    if tex_dir.exists():
        for f in sorted(tex_dir.iterdir()):
            if f.suffix.lower() in ('.jpg', '.jpeg', '.png'):
                rel = str(f.relative_to(ROOT))
                # prefer the downscaled thumb for fast loading
                thumb = 'media/thumbs/' + f.stem + '.jpg'
                textures.append(thumb if (ROOT / thumb).exists() else rel)
    if not textures:
        textures = ['media/ste-madeleine-sign-tile.png']  # fallback filler

    sections = []

    # ---- Band 0: Story (title + a few land-like frames) ----
    # A simple opening: title text + a few photos that read as "the place"
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
        hist_tiles.append(t)
    sections.append({'id':'band-story','title':'The Story','chapter':1,'designWidth':1600,
                     'height':420,'tiles':hist_tiles})

    # ---- Band 1: Reclamation — photos + videos + audio packed gaplessly ----
    pool = [('photo', p) for p in photos] + [('video', v) for v in videos] + [('audio', a) for a in audios]
    rng.shuffle(pool)
    seq_tiles = [tile_from_manifest(m, aspect) for _, m in pool]
    # annotate video/audio types
    for (kind, m), t in zip(pool, seq_tiles):
        if kind == 'video': t['type'] = 'video'
        elif kind == 'audio': t['type'] = 'audio'; t['cover'] = 'media/ste-madeleine-sign-tile.png'
    placed = pack_organic(seq_tiles, textures, 60, 60, rng)
    reclam_tiles = []
    for entry in placed:
        kind = entry[5]
        t, px, py, pw, ph, _ = entry
        if kind == 'stitch':
            reclam_tiles.append({'id':'stitch-'+str(px)+str(py),'type':'texture','src':t,'x':int(px),'y':int(py),'w':int(pw),'h':int(ph),'z':0,'rotate':0,'rx':0,'caption':'stitch'})
        else:
            t['x']=int(px); t['y']=int(py); t['w']=int(pw); t['h']=int(ph)
            t['z']=2 if t.get('type')=='video' else 1
            t['rotate']=rng.randint(-3,3)
            t['rx']=t['w']//2
            reclam_tiles.append(t)
    # scans at the end
    sx = max((t['x']+t['w'] for t in reclam_tiles), default=60) + 40
    for sc in scans:
        t = tile_from_manifest(sc, aspect); t['type']='scan'; t['poster']='media/ste-madeleine-sign-tile.png'
        t['x']=sx; t['y']=120; sx+=t['w']+20
        reclam_tiles.append(t)
    sections.append({'id':'band-reclamation','title':'Reclamation','chapter':2,'designWidth':1600,
                     'height':640,'tiles':reclam_tiles})

    return {'sections': sections, 'meta': {
        'title': 'Ste. Madeleine — A Quilt of Memory & Reclamation',
        'generated': 'organic-seed-v3',
        'note': 'Free-pan 2D quilt. Tiles packed interconnected at original aspect ratios. Rearrange + mark land tiles (Kind: Land) in the editor.'
    }}

def main():
    layout = build()
    OUT.write_text(json.dumps(layout, indent=2))
    n = sum(len(s['tiles']) for s in layout['sections'])
    print(f"Wrote {OUT} — {len(layout['sections'])} bands, {n} tiles")
    from collections import Counter
    for s in layout['sections']:
        print(f"  {s['title']}: {dict(Counter(t['type'] for t in s['tiles']))} ({len(s['tiles'])} tiles)")
    # aspect check
    from PIL import Image
    bad = 0
    for s in layout['sections']:
        for t in s['tiles']:
            if t.get('src') and (ROOT/t['src']).exists() and t['type'] in ('photo','video'):
                try:
                    iw, ih = Image.open(ROOT/t['src']).size
                    if abs((t['w']/t['h']) - (iw/ih)) > 0.03: bad += 1
                except: pass
    print(f"Aspect-ratio mismatches: {bad}")

if __name__ == '__main__':
    main()
