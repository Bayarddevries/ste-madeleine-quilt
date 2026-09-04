#!/usr/bin/env python3
"""Update Z&Z attributions to include section + page context, and add a credits block."""
import json, subprocess

# Map: short ID -> new attribution text
EDITS = {
    # Stage 1 — homeland bond (Preface, p. 7)
    '932649fd1ee3': '\u2014 Zeilig & Zeilig, Ste. Madeleine, 1987 (Preface, p. 7)',
    # Quote A — settlement roots (Introduction, p. 3)
    '94043492a0fa': '\u2014 Zeilig & Zeilig, Ste. Madeleine, 1987 (Introduction, p. 3)',
    # Stage 2 — homes burned (Preface, p. 4) — original speaker Yvon Dumont
    '93264a1b97e1': '\u2014 Yvon Dumont, recounted in Zeilig & Zeilig, Ste. Madeleine, 1987 (Preface, p. 4)',
    # Stage 3 — cemetery/mound (Preface, p. 4)
    '93264a355ac7': '\u2014 Zeilig & Zeilig, Ste. Madeleine, 1987 (Preface, p. 4)',
    # Quote E — Joe Venne log houses (Ch. 1, p. 22)
    '941085bceb9e': '\u2014 Joe Venne, b. 1906, in Zeilig & Zeilig, Ste. Madeleine, 1987 (Ch. 1, p. 22)',
    # Quote H — Lazare Fouillard burial (Ch. 6, p. 190)
    '941085c8f501': '\u2014 Lazare Fouillard, in Zeilig & Zeilig, Ste. Madeleine, 1987 (Ch. 6, p. 190)',
    # Quote C — Ste. Madeleine residents 1913 chapel petition (Ch. 5, p. 184)
    '9404349c69cf': '\u2014 Ste. Madeleine residents, Feb 2 1913, in Zeilig & Zeilig, Ste. Madeleine, 1987 (Ch. 5, p. 184)',
}

UPDATE_JS = '''
const board = penpot.currentPage.root.children[0];
const item = board.children.find(c => c.id === 'TARGET_ID');
if (!item) return {err: 'not found', id: 'TARGET_ID'};
item.characters = 'NEW_TEXT';
return {ok: true, chars: item.characters};
'''

for short_id, new_text in EDITS.items():
    full_id = f'6b66d2d1-b9cd-8073-8008-{short_id}'
    js = UPDATE_JS.replace('TARGET_ID', full_id).replace('NEW_TEXT', new_text)
    r = subprocess.run(['python3','scripts/penpot_mcp.py','exec', js], capture_output=True, text=True, cwd='/home/bayarddevries/ste-madeleine-quilt')
    res = json.loads(r.stdout).get('result', {})
    if 'err' in res:
        print(f'  FAIL ...{short_id}: {res}')
    else:
        print(f'  OK   ...{short_id}: {res["chars"]!r}')

# Now create a credits block at the bottom of the board
print()
print('Adding credits block...')

CREDITS_JS = '''
const board = penpot.currentPage.root.children[0];
const out = [];

// Credits header (small, italic-ish feel via lowercase)
const hdr = penpot.createText('CREDITS_HDR');
hdr.fontFamily = 'EB Garamond';
hdr.fontSize = 20;
hdr.fontWeight = 600;
hdr.fills = [{fillColor: '#6b4a2a', fillOpacity: 1}];
hdr.x = -2502;
hdr.y = 10600;
hdr.resize(1000, 30);
board.appendChild(hdr);
out.push({name:'hdr', id:hdr.id, y:hdr.y});

// Credits body — full book citation + modern sources
const body = penpot.createText('CREDITS_BODY');
body.fontFamily = 'EB Garamond';
body.fontSize = 18;
body.fontWeight = 400;
body.fills = [{fillColor: '#3a2c1c', fillOpacity: 1}];
body.x = -2502;
body.y = 10630;
body.resize(1000, 200);
board.appendChild(body);
out.push({name:'body', id:body.id, y:body.y});

return out;
'''

CREDITS_HDR = 'Sources & Credits'
CREDITS_BODY = (
    'BOOK — Ken & Victoria Zeilig, Ste. Madeleine: Community Without a Town — '
    'Métis Elders in Interview (Winnipeg: Pemmican Publications, 1987). ISBN 0-919143-45-8.\n\n'
    'PRIMARY SOURCE — Letter from Ste. Madeleine residents to Archbishop Langevin, '
    'February 2, 1913. Reproduced in Zeilig & Zeilig, Chapter 5.\n\n'
    'MODERN SOURCES — Manitoba Métis Federation press release, "Government of Manitoba '
    'to return Ste. Madeleine land to the MMF," July 19, 2024. MMF Spotlight, '
    '"From ashes to honour," July 25, 2024 (Gail Welburn, Minister John Fleury). '
    'MMF Spotlight, "Ste. Madeleine Métis Days," July 18, 2023 (Minister Will Goodon).'
)

js = CREDITS_JS.replace("'CREDITS_HDR'", "'" + CREDITS_HDR + "'")
js = js.replace("'CREDITS_BODY'", "'" + CREDITS_BODY + "'")

r = subprocess.run(['python3','scripts/penpot_mcp.py','exec', js], capture_output=True, text=True, cwd='/home/bayarddevries/ste-madeleine-quilt')
print(r.stdout[:1500])