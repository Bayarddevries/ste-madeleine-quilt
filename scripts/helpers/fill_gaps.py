import json, subprocess

CREATE = """
const board = penpot.currentPage.root.children[0];
const out = [];

// Quote E — Joe Venne, log houses (1885→1913 R side, y=1100)
const e = penpot.createText('E_TEXT');
e.fontFamily = 'EB Garamond'; e.fontSize = 34; e.fontWeight = 400;
e.fills = [{fillColor: '#a83c32', fillOpacity: 1}];
e.x = -1976; e.y = 1100; e.resize(430, 120);
board.appendChild(e);
out.push({name:'e', id:e.id, w:e.width, h:e.height});

const eAttr = penpot.createText('E_ATTR');
eAttr.fontFamily = 'EB Garamond'; eAttr.fontSize = 22; eAttr.fontWeight = 400;
eAttr.fills = [{fillColor: '#6b4a2a', fillOpacity: 1}];
eAttr.x = -1976; eAttr.y = 1220; eAttr.resize(430, 76);
board.appendChild(eAttr);
out.push({name:'eAttr', id:eAttr.id, w:eAttr.width, h:eAttr.height});

// Quote H — Lazare Fouillard, "when they die" (1958→2000s L side, y=3300)
const h = penpot.createText('H_TEXT');
h.fontFamily = 'EB Garamond'; h.fontSize = 34; h.fontWeight = 400;
h.fills = [{fillColor: '#a83c32', fillOpacity: 1}];
h.x = -2502; h.y = 3300; h.resize(430, 160);
board.appendChild(h);
out.push({name:'h', id:h.id, w:h.width, h:h.height});

const hAttr = penpot.createText('H_ATTR');
hAttr.fontFamily = 'EB Garamond'; hAttr.fontSize = 22; hAttr.fontWeight = 400;
hAttr.fills = [{fillColor: '#6b4a2a', fillOpacity: 1}];
hAttr.x = -2502; hAttr.y = 3460; hAttr.resize(430, 76);
board.appendChild(hAttr);
out.push({name:'hAttr', id:hAttr.id, w:hAttr.width, h:hAttr.height});

// Fact caption — "Ste. Madeleine (1902 – 1940)" (1958→2000s R side, y=3300)
const cap = penpot.createText('CAP_TEXT');
cap.fontFamily = 'Barlow Semi Condensed'; cap.fontSize = 48; cap.fontWeight = 700;
cap.fills = [{fillColor: '#3a2c1c', fillOpacity: 1}];
cap.x = -1976; cap.y = 3300; cap.resize(430, 60);
board.appendChild(cap);
out.push({name:'cap', id:cap.id, w:cap.width, h:cap.height});

const capSub = penpot.createText('CAP_SUB');
capSub.fontFamily = 'EB Garamond'; capSub.fontSize = 22; capSub.fontWeight = 400;
capSub.fills = [{fillColor: '#6b4a2a', fillOpacity: 1}];
capSub.x = -1976; capSub.y = 3360; capSub.resize(430, 38);
board.appendChild(capSub);
out.push({name:'capSub', id:capSub.id, w:capSub.width, h:capSub.height});

return out;
"""

E_TEXT = '"They built log houses on the homesteads—and log barns—and moved in there."'
E_ATTR = '— Joe Venne, in Zeilig & Zeilig, Ste. Madeleine: Community Without a Town, 1987'
H_TEXT = '...They would have been home. When they die, they still come and get buried there.'
H_ATTR = '— Lazare Fouillard, in Zeilig & Zeilig, Ste. Madeleine: Community Without a Town, 1987'
CAP_TEXT = 'Ste. Madeleine (1902 – 1940)'
CAP_SUB = '— Fleury homestead, Section 10, Township 18, Range 29'

js = CREATE
js = js.replace("'E_TEXT'", "'" + E_TEXT + "'")
js = js.replace("'E_ATTR'", "'" + E_ATTR + "'")
js = js.replace("'H_TEXT'", "'" + H_TEXT + "'")
js = js.replace("'H_ATTR'", "'" + H_ATTR + "'")
js = js.replace("'CAP_TEXT'", "'" + CAP_TEXT + "'")
js = js.replace("'CAP_SUB'", "'" + CAP_SUB + "'")

r = subprocess.run(['python3','scripts/penpot_mcp.py','exec', js], capture_output=True, text=True, cwd='/home/bayarddevries/ste-madeleine-quilt')
print('exit:', r.returncode)
print(r.stdout[:2000])
print('ERR:', r.stderr[:500])
