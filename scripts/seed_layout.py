#!/usr/bin/env python3
"""Ste. Madeleine Quilt — seed layout generator.
Builds layout.json from quilt-tiles.json, splitting content into narrative sections.
This is the "AI seed" tool: it proposes a starting composition that Bayard then
rearranges in the editor. Run:  python3 scripts/seed_layout.py
"""
import json, os, random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TILES = json.load(open(ROOT / 'quilt-tiles.json'))
OUT = ROOT / 'layout.json'

# Map existing tile ids/types from the legacy manifest
def load_manifest():
    return TILES

def classify(t):
    # People vs land heuristic for the reclamation section.
    # 'land' photos are those whose src filename is a timestamp (1787...) or unknown
    # phone-shot; people photos are IMG_*. Best-effort for the seed — Bayard fixes.
    src = t.get('src','').lower()
    fname = os.path.basename(src)
    if src.endswith('.glb'):
        return 'scan'
    if fname.startswith('178') or t.get('type')=='sphere':
        return 'land'
    return 'people'

def build_sections():
    manifest = load_manifest()
    weekend = [t for t in manifest if 'weekend-2026' in t.get('src','')]
    random.Random(42).shuffle(weekend)  # deterministic

    sections = []

    # --- 1. Thriving Community (text chapter, land backdrop) ---
    sections.append({
        "id": "ch1-thriving",
        "title": "Thriving Community",
        "chapter": 1,
        "height": 1400,
        "background": "media/ste-madeleine-sign-tile.png",
        "tiles": [
            {"id":"t1a","type":"text","x":80,"y":240,"w":560,"h":300,
             "text":"From the 1870s, Métis homesteaders built a life on this land — farms, families, a church at its heart.",
             "fontSize":26,"z":2},
            {"id":"t1b","type":"land","src":"media/ste-madeleine-sign-tile.png",
             "x":700,"y":300,"w":360,"h":420,"rx":14,"rotate":-2,"z":1,
             "caption":"The land remembers"},
        ],
    })

    # --- 2. Devastation ---
    sections.append({
        "id": "ch2-devastation",
        "title": "Devastation",
        "chapter": 2,
        "height": 1400,
        "tiles": [
            {"id":"t2a","type":"text","x":120,"y":280,"w":520,"h":300,
             "text":"1935–1938. The PFRA forced the community out. Families scattered; the church was burned.",
             "fontSize":26,"z":2},
        ],
    })

    # --- 3. Resistance ---
    sections.append({
        "id": "ch3-resistance",
        "title": "Resistance",
        "chapter": 3,
        "height": 1400,
        "tiles": [
            {"id":"t3a","type":"text","x":100,"y":260,"w":560,"h":300,
             "text":"1938. Joe Venne refused to let the church be dismantled and saved it from destruction.",
             "fontSize":26,"z":2},
        ],
    })

    # --- 4. Remembrance ---
    sections.append({
        "id": "ch4-remembrance",
        "title": "Remembrance",
        "chapter": 4,
        "height": 1400,
        "tiles": [
            {"id":"t4a","type":"text","x":120,"y":280,"w":520,"h":300,
             "text":"Decades later, only the foundations and the cemetery remain — and the memory held by descendants.",
             "fontSize":26,"z":2},
        ],
    })

    # --- 5. Reclamation (the living weekend — real media) ---
    # Compose a quilt: people tiles and land tiles interleaved, varied sizes.
    sec5 = {
        "id": "ch5-reclamation",
        "title": "Reclamation",
        "chapter": 5,
        "height": 4200,
        "tiles": [],
    }
    x, y = 60, 300
    row_h = 320
    spacing = 30
    i = 0
    land_flip = True
    for t in weekend:
        kind = classify(t)
        w = random.Random(i).choice([240,280,320,360,420,260,340])
        h = random.Random(i+99).choice([220,260,300,340,280,240])
        tile = {
            "id": t.get('id', f'w{i}'),
            "type": kind,                       # 'people'|'land'|'scan'
            "src": t['src'],
            "x": x, "y": y,
            "w": w, "h": h,
            "z": 1,
            "caption": t.get('cap', 'Ste. Madeleine Métis Days 2026'),
        }
        if kind == 'land':
            tile['rotate'] = random.Random(i+5).choice([-1,1,2,-2,0])
            tile['rx'] = 10
        if kind == 'scan':
            tile['rotate'] = 0
            tile['rx'] = 12
            tile['poster'] = 'media/ste-madeleine-sign-tile.png'
        sec5['tiles'].append(tile)
        # advance; wrap row every ~4 tiles
        x += w + spacing
        if i % 4 == 3:
            x = 60
            y += row_h
        i += 1
    sections.append(sec5)

    return {"sections": sections, "meta": {
        "title": "Ste. Madeleine — A Quilt of Memory & Reclamation",
        "generated": "seed",
        "note": "Seed layout from quilt-tiles.json. Rearrange in the editor."
    }}

def main():
    layout = build_sections()
    OUT.write_text(json.dumps(layout, indent=2))
    n = sum(len(s['tiles']) for s in layout['sections'])
    print(f"Wrote {OUT} — {len(layout['sections'])} sections, {n} tiles")
    for s in layout['sections']:
        print(f"  {s['chapter']}. {s['title']} — {len(s['tiles'])} tiles, h={s['height']}")

if __name__ == '__main__':
    main()
