#!/usr/bin/env python3
"""Ste. Madeleine Quilt — organic quilt seed layout generator.
Packs tiles interconnected (edges touching/overlapping, staggered, NOT a grid),
preserving original aspect ratios. Lay out in a gentle narrative flow across the
free-pan 2D canvas.

NOTE on people-vs-land: filenames don't reliably separate people from land/plant
shots (PXL/_MG_/IMG all contain both). That classification is Bayard's curation
job in the editor (mark-as-land toggle). This seed treats all photos as photos.

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
    base = rng.choice([200, 220, 240, 260, 280, 300])
    if ar >= 1:
        w, h = base, int(base / ar)
    else:
        w, h = int(base * ar), base
    return {'id': t.get('id'), 'src': src, 'type': t.get('type', 'photo'),
            'w': max(w, 60), 'h': max(h, 60),
            'caption': t.get('cap', 'Ste. Madeleine Métis Days 2026'),
            'title': t.get('title', '')}

def pack_organic(tiles, start_x, start_y, rng):
    """Pack tiles left-to-right in staggered rows, edges touching.
    Organic: each row starts at a slight random offset and tiles have small
    vertical jitter so it's not a strict grid."""
    placed = []
    x, y = start_x, start_y
    row_h = 0
    first = True
    for i, t in enumerate(tiles):
        if x - start_x > 1250:
            y += row_h + 2
            x = start_x + (rng.randint(-8, 8) if not first else 0)
            row_h = 0
        jitter_y = rng.randint(-3, 3) if i > 0 else 0
        placed.append((t, x, y + jitter_y))
        x += t['w'] + rng.randint(0, 2)
        row_h = max(row_h, t['h'])
        first = False
    return placed

def build():
    aspect = probe_aspect()
    rng = random.Random(7)

    photos = [t for t in TILES if t['type'] == 'photo']
    videos = [t for t in TILES if t['type'] == 'video']
    audios = [t for t in TILES if t['type'] == 'audio']
    scans  = [t for t in TILES if t['type'] == 'sphere']
    rng.shuffle(photos)

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

    # ---- Band 1: Reclamation — photos + videos + audio packed organically ----
    pool = [('photo', p) for p in photos] + [('video', v) for v in videos] + [('audio', a) for a in audios]
    rng.shuffle(pool)
    seq_tiles = [tile_from_manifest(m, aspect) for _, m in pool]
    # annotate video/audio types
    for (kind, m), t in zip(pool, seq_tiles):
        if kind == 'video': t['type'] = 'video'
        elif kind == 'audio': t['type'] = 'audio'; t['cover'] = 'media/ste-madeleine-sign-tile.png'
    placed = pack_organic(seq_tiles, 60, 60, rng)
    reclam_tiles = []
    for t, px, py in placed:
        t['x']=px; t['y']=py
        t['rotate']=rng.choice([-1,0,0,1])
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
        'note': 'Free-pan 2D quilt. Tiles packed interconnected at original aspect ratios. Rearrange + mark land tiles in the editor.'
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
