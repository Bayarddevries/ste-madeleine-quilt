# HANDOFF — Ste. Madeleine timeline (2026-09-01)

> **Read this FIRST when resuming.** Current state, geometry constants, and next
> steps. Companion files: `README.md` (layout), `timeline-plan.md` (content/sources),
> `references/pattern-library.md` (typography), `scripts/penpot_mcp.py` (MCP client).

## Where the project stands

- **Design surface:** Penpot board (browser, free) at `https://design.penpot.app`.
  Timeline board: 1440×4119, light parchment `#f0e9db`, true-scale 10-entry timeline.
- **Design is DONE through the timeline phase.** Entries laid out, photos placed,
  pull quotes / ghost year / era banners in the empty bands, years aligned.
- **HTML build has NOT started.** `timeline2.html` is an early Figma-era build —
  it is NOT the current design. Next work item is building the real HTML from Penpot.
- Old quilt viewer (`index.html` / `layout.json` / editor) is superseded; kept as reference.

## Penpot MCP access — IMPORTANT

- Client: `scripts/penpot_mcp.py` (reads token from `~/.hermes/config.yaml` → `mcp_servers.penpot.url`).
- **KNOWN ISSUE:** token in config was reported stale today ("No Penpot instance
  connected for user token"). Bayard must have the Penpot tab open with the MCP
  plugin connected; if the error persists, regenerate the MCP key in Penpot
  (Integrations → MCP) and update `mcp_servers.penpot.url` in config.yaml.
- Commands: `python3 scripts/penpot_mcp.py shapes|timeline|exec '<js>'|export <id> <out.png>`
- Plugin JS runs inside the Penpot editor context (`penpot`, `penpot.currentPage.root`).
- The board is found by heuristic: a board with a thin tall rectangle (spine) AND
  ≥5 child boards named like "Component". If that changes, adapt FIND_TIMELINE.

## Timeline geometry constants (VERIFIED)

```
Board:           1440 × 4119, fill #f0e9db (parchment)
True scale:      23px / year, 1870 @ y=220 → 2026 @ y=3808
Spine:           dots at x=-2024 (centerline); spine rect ~22px wide centered x=-1997
Left cards:      x=-2502 (card left edge), right edge toward spine
Right cards:     x=-1976 (card left edge at spine gap)
Card-spine gap:  48px both sides
Card width:      430px
Card padding:    34px L/R, 22px top, 14px year↔caption gap, 26px bottom
Years:           140px box, pinned 74px from spine BOTH sides
                 (left year right-edge -2090, right year left-edge -1950)
                 font Barlow Semi Condensed SemiBold, 44px, weight 700
Photos:          left inner edge -2072, right inner edge -1976, max height 640px,
                 aspect preserved
```

## Timeline entries (10, top→bottom)

| Year | Side | Caption (abbrev.) |
|------|------|--------------------|
| 1870 | left | Métis families pushed out of Red River settle at Ste. Madeleine |
| 1885 | ?    | Resistance / Red River Métis context |
| 1913 | ?    | Community builds a log chapel |
| 1922 | ?    | One-room school opens |
| 1935 | ?    | Devastation begins (PFRA / drought era) |
| 1938 | ?    | Displacement, homes burned, church saved by Joe Venne |
| 1958 | ?    | Census / the long wait begins |
| 2016 | ?    | Land returned to MMF, bell return |
| 2024 | ?    | MOU July 2024 |
| 2026 | ?    | CCAP / reclamation weekend |

(Side alternation confirmed; exact per-entry side in the Penpot board — re-read before building.)

## Typography elements placed in the Wait band & gaps (Option A)

```
Pull quotes:      EB Garamond, rust #a83c32, 34px; attribution #6b4a2a, 22px
                  placed on cards' outer rail (right x=SPINE+48, left x=SPINE-48-430)
  - Elders quote   right, y≈640/930    "They always considered Ste. Madeleine, with its log cabins..."
  - Joe Venne      right, y≈4700/5050  "Well then, in 1938, we were asked by the municipality to move out..."
  - Gail Welburn   left,  y≈6900/7260  "My grandfather was 27 when his dog was shot and his home was burnt..."
  - Chartrand      right, y≈9380/9530  "We have been working toward this for a long time."

Ghost year:       1958, Barlow Semi Condensed 560px weight 700, #3a2c1c,
                  opacity 0.07, centered on spine, y=6900
Era banners:      "GENERATIONS OF WAITING" 46px weight 700 #b3362a, y≈7260
                  "1958 – 2016" 30px weight 600 #6b4a2a, y≈7350 (both centered on spine)
```

## Woodgrain / grave-wood texture

- The wood texture is the photo of a grave at Ste. Madeleine — currently the board
  fill was swapped OUT (to parchment) so black line/dots read on screen.
- **Do NOT stretch it** in HTML — it blurs. Tile it: CSS `background-repeat: repeat`
  (seamless repeat every ~2220px source tile).
- To recover the original texture bytes: read board fill `fillImage.data()` via
  `scripts/penpot_mcp.py exec` (returns Uint8Array → base64) and save to `media/`.
  Alternatively the user re-uploads the original grave-wood photo.

## Fonts

- Vendored in repo: ONLY `media/barlow-condensed-regular.ttf`.
- HTML build needs: **Barlow Regular** (sign-matched wordmark), **Barlow Semi
  Condensed SemiBold** (years), **Georgia** (body — free system font, no vendoring).
  Download Barlow family from Google Fonts (free) into `media/` before building.
- EB Garamond exists in Penpot but is not needed in HTML if Georgia is the body face.

## Known API quirks (from today's sessions)

- `fontWeight: 800` is rejected — only 200/300/400/600/700/900.
- `growType: 'auto-height'` does NOT auto-grow created text; `resize(w, h)` explicitly.
- Text `width` reads as ~1px right after create with auto-width — set x/y, then
  RE-READ in a second call for the real width (async reflow).
- Cloudflare blocks urllib's default UA — the client sends a browser UA.
- Vision tool can't read /tmp paths — copy exports into `~/.hermes/cache/images/` first.
- Browser tool refuses localhost — validate HTML via headless Chrome `--dump-dom`.

## Next steps (pickup order)

1. **Reconnect Penpot MCP** (see above) — verify with `python3 scripts/penpot_mcp.py timeline`.
2. **Read the live board** via exec: dump entries (year/caption/dot/card coords),
   photos (x/y/w/h), texts (quotes/banners/ghost), and the board fill image bytes.
3. **Recover the woodgrain** bytes → `media/woodgrain.jpg`.
4. **Vendor Barlow Regular + Semi Condensed SemiBold** (Google Fonts, free).
5. **Build `timeline3.html`** — faithful rendering: true scale 23px/yr,
   1870@220→2026@3808, alternating cards, woodgrain tiled sharp behind (CSS repeat),
   quotes/banners/ghost at their real y positions, sign wordmark header.
   Serve via `serve.py`, verify with headless Chrome, view via Tailscale URL.
6. **Landing page** next (design in Penpot, build like `figma_landing_to_html.py` pattern).
7. Ask Bayard about git remote for backup (repo has none).

## Lessons learned (do not repeat)

- **/tmp scripts vanish.** All one-off `penpot_*.py` in /tmp were wiped. Reusable
  logic now lives in `scripts/penpot_mcp.py`. Keep everything in the repo.
- Don't stretch the wood texture in HTML; tile it.
- Don't judge aesthetics — Bayard is the visual authority; implement what he decides.
- English only. NEVER reply in Chinese (repeated hard correction).
- Real tested output over proposals; verify before reporting.
