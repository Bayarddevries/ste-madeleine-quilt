#!/usr/bin/env python3
import json, subprocess
js = '''
const board = penpot.currentPage.root.children[0];
const all = board.children;
const out = {boards: [], texts: [], rects: []};
for (const c of all) {
  const o = {type: c.type, name: c.name, id: c.id.slice(-12), x: c.x, y: c.y, w: c.width, h: c.height};
  if (c.type === 'text') o.chars = c.characters;
  if (c.type === 'board') {
    const inner = (c.children||[]).filter(x=>x&&x.type==='text').map(t=>({y:t.y,chars:t.characters}));
    o.inner = inner;
  }
  out[c.type+'s'] = out[c.type+'s'] || [];
  out[c.type+'s'].push(o);
}
return out;
'''
r = subprocess.run(['python3','scripts/penpot_mcp.py','exec', js], capture_output=True, text=True)
data = json.loads(r.stdout)['result']
print('=== BOARDS (cards) ===')
for b in sorted(data.get('boards',[]), key=lambda x:x['y']):
    side = 'L' if b['x'] < -2100 else 'R'
    inner = b.get('inner', [])
    year = inner[0]['chars'].strip() if inner else '?'
    print(f"  y={b['y']:6.0f} {side}  year={year!r}")
print()
print('=== TEXTS (all) ===')
for t in sorted(data.get('texts',[]), key=lambda x:x['y']):
    ch = t['chars'][:80]
    print(f"  y={t['y']:6.0f} x={t['x']:7.0f} h={t['h']:4.0f} | {ch}")