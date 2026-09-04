#!/usr/bin/env python3
"""Export every shape from the Penpot board as a PNG.

Usage: python3 export_all.py
"""
import json, subprocess, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
js = '''const board = penpot.currentPage.root.children[0];
return board.children.map(c => ({id: c.id, type: c.type, name: c.name}));'''
r = subprocess.run(['python3','scripts/penpot_mcp.py','exec', js], capture_output=True, text=True, cwd=ROOT)
shapes = json.loads(r.stdout)['result']

EXPORTS = os.path.join(ROOT, 'media/exports')
os.makedirs(EXPORTS, exist_ok=True)
print(f'Exporting {len(shapes)} shapes...', flush=True)
exported, failed = [], []
for i, s in enumerate(shapes):
    name = (s['name'] or f"unnamed_{i}").replace(' ', '_').replace('/', '_').replace('\n','_')
    out = os.path.join(EXPORTS, f"{name}_{s['id'][:8]}.png")
    if os.path.exists(out) and os.path.getsize(out) > 100:
        exported.append((s['id'], s['type'], s['name'], out, os.path.getsize(out)))
        print(f"  [skip] {s['name'][:35]:35s} -> {os.path.getsize(out)//1024}KB (exists)", flush=True)
        continue
    r2 = subprocess.run(['python3','scripts/penpot_mcp.py','export', s['id'], out],
                       capture_output=True, text=True, cwd=ROOT)
    if os.path.exists(out) and os.path.getsize(out) > 100:
        size = os.path.getsize(out)
        exported.append((s['id'], s['type'], s['name'], out, size))
        print(f"  [{i+1:2d}]  OK  {s['type']:10s} {s['name'][:30]:30s} -> {size//1024}KB", flush=True)
    else:
        failed.append(s['name'])
        print(f"  [{i+1:2d}]  FAIL {s['name']}: {(r2.stderr or r2.stdout)[:80].strip()}", flush=True)

print(f"\nExported: {len(exported)}/{len(shapes)}, Failed: {len(failed)}", flush=True)
print(f"Files in media/exports: {len([f for f in os.listdir(EXPORTS) if f.endswith('.png')])}", flush=True)
