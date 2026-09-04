#!/usr/bin/env python3
"""Update Z&Z attributions to use proper full title."""
import json, subprocess

UPDATE_JS = """
const board = penpot.currentPage.root.children[0];
const item = board.children.find(c => c.id === 'TARGET_ID');
if (!item) return {err: 'not found'};
item.characters = 'NEW_TEXT';
return {ok: true, chars: item.characters};
"""

edits = [
    # Stage 1 homeland bond attribution
    ('932649fd1ee3', '\u2014 K. & V. Zeilig, Ste. Madeleine: Community Without a Town \u2014 M\u00e9tis Elders in Interview, 1987, p. 7'),
    # Stage 2 homes burned attribution (Yvon Dumont voice)
    ('93264a1b97e1', '\u2014 Y. Dumont, recounted in K. & V. Zeilig, Ste. Madeleine: Community Without a Town \u2014 M\u00e9tis Elders in Interview, 1987, p. 4'),
    # Stage 3 cemetery/mound attribution
    ('93264a355ac7', '\u2014 K. & V. Zeilig, Ste. Madeleine: Community Without a Town \u2014 M\u00e9tis Elders in Interview, 1987, p. 4'),
    # Quote A settlement roots attribution
    ('94043492a0fa', '\u2014 K. & V. Zeilig, Ste. Madeleine: Community Without a Town \u2014 M\u00e9tis Elders in Interview, 1987, p. 3'),
    # Quote E log houses attribution
    ('941085bceb9e', '\u2014 Joe Venne (b. 1906), in K. & V. Zeilig, Ste. Madeleine: Community Without a Town \u2014 M\u00e9tis Elders in Interview, 1987, p. 22'),
    # Quote C chapel letter attribution
    ('9404349c69cf', '\u2014 Ste. Madeleine residents, Feb 2 1913, in K. & V. Zeilig, Ste. Madeleine: Community Without a Town \u2014 M\u00e9tis Elders in Interview, 1987, p. 184'),
    # Quote H Fouillard attribution
    ('941085c8f501', '\u2014 Lazare Fouillard, in K. & V. Zeilig, Ste. Madeleine: Community Without a Town \u2014 M\u00e9tis Elders in Interview, 1987, p. 190'),
]

for sid, new_text in edits:
    full_id = f'6b66d2d1-b9cd-8073-8008-{sid}'
    js = UPDATE_JS.replace('TARGET_ID', full_id).replace('NEW_TEXT', new_text)
    r = subprocess.run(['python3','scripts/penpot_mcp.py','exec', js], capture_output=True, text=True, cwd='/home/bayarddevries/ste-madeleine-quilt')
    res = json.loads(r.stdout).get('result', {})
    if 'err' in res:
        print(f'  FAIL ...{sid}: {res}')
    else:
        print(f'  OK   ...{sid[-12:]}: {res["chars"][:100]}...')