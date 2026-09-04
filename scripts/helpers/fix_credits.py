import json, subprocess

NEW_BODY = (
    "BOOK \u2014 Ken & Victoria Zeilig, Ste. Madeleine: Community Without a Town \u2014 "
    "M\u00e9tis Elders in Interview (Winnipeg: Pemmican Publications, 1987). ISBN 0-919143-45-8.\n\n"
    "PRIMARY SOURCE \u2014 Letter from Ste. Madeleine residents to Archbishop Langevin, "
    "February 2, 1913. Reproduced in Zeilig & Zeilig, Chapter 5.\n\n"
    "MODERN SOURCES \u2014 Manitoba M\u00e9tis Federation press release, "
    "\"Government of Manitoba to return Ste. Madeleine land to the MMF,\" July 19, 2024. "
    "MMF Spotlight, \"From ashes to honour,\" July 25, 2024 (Gail Welburn, Minister John Fleury). "
    "MMF Spotlight, \"Ste. Madeleine M\u00e9tis Days,\" July 18, 2023 (Minister Will Goodon)."
)

js = """
const board = penpot.currentPage.root.children[0];
const item = board.children.find(c => c.id === '6b66d2d1-b9cd-8073-8008-941336e2a09d');
if (!item) return {err: 'not found'};
item.characters = BODY_PLACEHOLDER;
return {ok: true, chars: item.characters};
"""

js = js.replace('BODY_PLACEHOLDER', json.dumps(NEW_BODY))

r = subprocess.run(['python3','scripts/penpot_mcp.py','exec', js], capture_output=True, text=True, cwd='/home/bayarddevries/ste-madeleine-quilt')
print(r.stdout[:500])