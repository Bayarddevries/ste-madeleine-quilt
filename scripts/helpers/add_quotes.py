import json, subprocess, textwrap

CREATE = """
const board = penpot.currentPage.root.children[0];
const out = [];

// Quote A — settlement roots (1885 context), R side, y=980
const root = penpot.createText('ROOT_TEXT');
root.fontFamily = 'EB Garamond'; root.fontSize = 34; root.fontWeight = 400;
root.fills = [{fillColor: '#a83c32', fillOpacity: 1}];
root.x = -1976; root.y = 980; root.resize(430, 160);
board.appendChild(root);
out.push({name:'root', id:root.id, w:root.width, h:root.height});

const rootAttr = penpot.createText('ROOT_ATTR');
rootAttr.fontFamily = 'EB Garamond'; rootAttr.fontSize = 22; rootAttr.fontWeight = 400;
rootAttr.fills = [{fillColor: '#6b4a2a', fillOpacity: 1}];
rootAttr.x = -1976; rootAttr.y = 1140; rootAttr.resize(430, 38);
board.appendChild(rootAttr);
out.push({name:'rootAttr', id:rootAttr.id, w:rootAttr.width, h:rootAttr.height});

// Quote C — chapel petition 1913 (primary source), L side near 1913 card (y=1470), y=1280
const chapel = penpot.createText('CHAPEL_TEXT');
chapel.fontFamily = 'EB Garamond'; chapel.fontSize = 34; chapel.fontWeight = 400;
chapel.fills = [{fillColor: '#a83c32', fillOpacity: 1}];
chapel.x = -2502; chapel.y = 1280; chapel.resize(430, 160);
board.appendChild(chapel);
out.push({name:'chapel', id:chapel.id, w:chapel.width, h:chapel.height});

const chapelAttr = penpot.createText('CHAPEL_ATTR');
chapelAttr.fontFamily = 'EB Garamond'; chapelAttr.fontSize = 22; chapelAttr.fontWeight = 400;
chapelAttr.fills = [{fillColor: '#6b4a2a', fillOpacity: 1}];
chapelAttr.x = -2502; chapelAttr.y = 1440; chapelAttr.resize(430, 38);
board.appendChild(chapelAttr);
out.push({name:'chapelAttr', id:chapelAttr.id, w:chapelAttr.width, h:chapelAttr.height});

return out;
"""

goodon_text = '...when the Metis of the Red River Valley were forced to abandon their settlement after 1870, it was logical they would choose a familiar area in which to make their new home. Also, many Metis who had settled in Saskatchewan, chose to return to Manitoba, following the Rebellion of 1885.'
goodon_attr = '— Zeilig & Zeilig, Ste. Madeleine: Community Without a Town, 1987'
chapel_text = '"We the undersigned residents of the Mission of Ste. Madeleine... now that we have constructed, by our own means, a small chapel... send us a missionary who is able to speak our Indian languages."'
chapel_attr = '— Ste. Madeleine residents, Feb 2 1913, in Zeilig & Zeilig, Ste. Madeleine: Community Without a Town, 1987'

js = CREATE.replace("'ROOT_TEXT'", "'" + goodon_text + "'")
js = js.replace("'ROOT_ATTR'", "'" + goodon_attr + "'")
js = js.replace("'CHAPEL_TEXT'", "'" + chapel_text + "'")
js = js.replace("'CHAPEL_ATTR'", "'" + chapel_attr + "'")

r = subprocess.run(['python3','scripts/penpot_mcp.py','exec', js], capture_output=True, text=True, cwd='/home/bayarddevries/ste-madeleine-quilt')
print('exit', r.returncode)
print(r.stdout[:1500])
print('ERR:', r.stderr[:500])
