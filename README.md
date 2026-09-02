# Ste. Madeleine Quilt — README

A memorial website for the Métis community of Ste. Madeleine, Manitoba (destroyed 1938).
The site is a "quilt of memory & reclamation": a true-scale timeline of the community's
history plus a free-pan 2D quilt of the 2026 reclamation weekend media.

**Working model:** Bayard designs in Penpot (browser, free). Hermes reads the live
Penpot file over MCP and builds the HTML. Bayard is the visual authority; Hermes is
the implementation hand.

## Quick start

```bash
python3 serve.py            # serves repo at http://localhost:8090 (bind 0.0.0.0)
```
Reachable remotely via Tailscale: `http://100.108.183.33:8090/` or LAN `http://10.0.0.127:8090/`
(`localhost` does NOT work from phone/Surface). Server is `python3 serve.py` — it also
accepts `POST /save-layout` for the old editor pipeline.

## Repo layout

```
ste-madeleine-quilt/
├── serve.py                    # local dev server (:8090)
├── index.html                  # OLD free-pan 2D quilt viewer (superseded, keep as reference)
├── timeline.html               # first timeline from research (5 stages)
├── timeline2.html              # HTML timeline built from Figma JSON (early, pre-Penpot)
├── timeline-scroll.html        # scroll experiment (older)
├── layout.html / quilt-layout.js / layout.json   # OLD editor pipeline (superseded)
├── editor.html                 # OLD editor (superseded)
├── docs/
│   ├── INTENT.md               # confirmed project intent (2026-08-25)
│   ├── PROJECT.md              # project definition, content inventory
│   ├── SPEC.md                 # editor/viewer spec for the old pipeline
│   └── HANDOFF.md              # CURRENT STATE + where to start (read this first)
├── references/
│   └── pattern-library.md      # typography/design system
├── scripts/
│   ├── penpot_mcp.py           # reusable Penpot MCP client (token from ~/.hermes/config.yaml)
│   ├── figma_landing_to_html.py
│   ├── figma_to_layout.py
│   └── ...                     # older build scripts
├── media/
│   ├── weekend-2026/           # 204 files: photos, videos, audio, 3D scans from the 2026 weekend
│   ├── timeline/               # historical images (metis_camp_1874, metis_woman_1886, stm_*, ...)
│   ├── textures/               # wood/land textures incl. grave-wood photos
│   ├── memory-wall/            # videos
│   ├── barlow-condensed-regular.ttf   # ONLY Barlow variant vendored
│   ├── ste-madeleine-sign-clean.png   # background-removed sign wordmark (2909×276)
│   └── ...                     # flag loops, thumbs, vendor
└── timeline-plan.md            # researched history + quotes with sources
```

## Design pipeline (CURRENT)

1. **Bayard designs in Penpot** — `https://design.penpot.app` (browser, free).
   Timeline board has 10 entries on true scale, alternating sides, with photos,
   pull quotes, ghost years, era banners in the empty bands.
2. **Hermes reads the live file over MCP** — token in `~/.hermes/config.yaml`
   (`mcp_servers.penpot.url`), 4 tools registered. Use `scripts/penpot_mcp.py`
   to exec plugin JS / export shapes without the gateway restart requirement.
3. **Hermes builds HTML** — next step: `timeline3.html` (or similar) rendering
   the Penpot board faithfully, woodgrain tiled sharp via CSS, Barlow + Georgia
   (EB Garamond in Penpot) typography.

Figma was abandoned (Starter-plan API rate-limited, ~4.5-day lockout). Framer ruled
out (Code Components are Pro-only). Penpot is the design surface of record.

## Typography system (pattern-library.md + learned in Penpot)

- **Barlow Regular** — matches the Ste. Madeleine sign letters (thin stroke ~0.037 ratio)
- **Barlow Semi Condensed SemiBold** — year labels on timeline cards
- **Barlow Condensed** — small labels
- **Georgia** — narrative body in HTML (EB Garamond in Penpot — Georgia is NOT in Penpot's font list)
- **EB Garamond** — pull quotes in Penpot (rust `#a83c32`, 34px quote / 22px attribution)

## Penpot MCP access

```bash
python3 scripts/penpot_mcp.py shapes     # list top-level shapes on current page
python3 scripts/penpot_mcp.py timeline   # find the timeline board by heuristic
python3 scripts/penpot_mcp.py exec 'const page = penpot.currentPage; return page.root.children.map(c=>c.name);'
python3 scripts/penpot_mcp.py export <shapeId> /tmp/out.png
```
See script header for API quirks (fontWeight 800 unsupported, auto-height doesn't grow,
text width reads 1px until re-read, Cloudflare needs browser UA, etc.).

## Historical sources

- timeline-plan.md: researched 5-stage history (Barkwell 2016, Zeilig & Zeilig 1987,
  MMF Spotlight, CBC 2024) + key quotes (Joe Venne, elders 1986, David Chartrand 2024,
  Gail Welburn)
- Ste. Madeleine community destroyed 1938; land returned to MMF 2016; bell returned;
  MOU July 2024; CCAP summer 2026.
- **NEVER fabricate historical content.** Real quotes + provenance only.

## Git

Local repo `master`, no remote. Many uncommitted files (timeline2.html, scripts,
media, layout.html, quilt-layout.js). Consider pushing to a remote for backup (ask Bayard).
