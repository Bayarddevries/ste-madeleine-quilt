# Ste. Madeleine Quilt — Project Definition

> Built from confirmed INTENT.md (2026-08-25). Read INTENT.md first.

## Project
- **Dir:** `~/ste-madeleine-quilt/`
- **What:** One endlessly-scrolling, hand-designed narrative quilt page.
- **Story:** Loss → Resistance → Reclamation. The 2026 weekend media is living proof of reclamation.
- **Current repo:** `master`, NO remote. Committed work exists but the build is fragmented.

## Content inventory (local, on disk)
`media/weekend-2026/` — **201 files**:
- 176 `.jpg` photos
- 12 `.mp4` videos
- 6 `.m4a` audio recordings
- 2 `.glb` 3D scans
- 3 `.heic` photos — **need conversion to JPG (won't render in browsers)**
- 1 `.png`, 1 `.json` (drift)

`media/` other:
- `memory-wall/` (3 files), `timeline/` (10 incl. flag GIF), flag loops, wordmark/sign assets, Barlow font.

## The 5 narrative chapters (from existing timeline research)
1. **Thriving Community** (1870s–1938) — Métis homesteaders settle Ste. Madeleine
2. **Devastation** (1935–1938) — PFRA displaces the community, church burned
3. **Resistance** (1938) — Joe Venne saves the church from dismantling
4. **Remembrance** (1938–2024) — only foundations and cemetery remain
5. **Reclamation** (2016–2026) — land returned to MMF, new cross raised, **the living 2026 weekend**

## Architecture decision (ONE pipeline, no fragments)
```
ONE editor  →  layout.json  →  ONE viewer (the scroll)
```
- **Editor** = composition studio: drag, scale, reshape (non-square crops), layer/z-order, overlap. Operates on a **section/chapter canvas** at a time. AI seeds a starting layout; Bayard rearranges.
- **layout.json** = single source of truth for every tile's position/size/shape/layer per section.
- **Viewer** = the endless scroll. Stitches sections together in order, renders layout.json faithfully (editor WYSIWYG = viewer).

## Workflow per section (joint venture)
1. AI proposes a starting composition.
2. Bayard rearranges/reshapes in the editor.
3. Iterate → save layout.json → viewer reflects it.
4. Commit, move to next section.

## Files (proposed)
- `docs/INTENT.md` — confirmed intent (done)
- `docs/PROJECT.md` — this file
- `docs/SPEC.md` — editor + viewer + layout schema spec (next step)
- `editor.html` — rebuilt composition studio (REPLACES broken editor.html + layout.html + quilt-layout.js)
- `viewer.html` — the endless scroll (replaces index.html)
- `layout.json` — the single source of truth
- `scripts/convert_heic.sh` — HEIC → JPG for browser display

## Known pain points to fix
- 3 HEIC photos won't render → convert.
- `object-fit:cover` forces everything square → editor must support non-square shapes/crops.
- Three broken editors → consolidate to one real one.
- No spec existed → SPEC.md now mandated.
- No git remote → consider pushing for backup (ask Bayard).

## Out of scope (from INTENT)
- No auto-finished layouts. No torus scatter as end state. No patched legacy editors.

## Decision log
- 2026-08-25 — Intent confirmed. Project formally defined.
