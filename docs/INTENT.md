# Ste. Madeleine Quilt — Intent

> Status: **CONFIRMED** by Bayard — 2026-08-25
> This is the source of truth. Re-read before any build decision.

## The one-sentence vision
A single continuous, free-panning 2D canvas that tells the Ste. Madeleine story —
loss → resistance → reclamation — as an interconnected quilt of the weekend media
and the land itself, preserving original aspect ratios.

## The form (corrected 2026-08-25)
- **One continuous 2D canvas, NOT a vertical scroll page.** Drag/pan in ALL
  directions (mouse + touch), with wheel/pinch zoom.
- **Tiles packed interconnected** — edges touching/overlapping into a contiguous
  quilt surface. Organic and staggered, NOT a grid.
- **Original aspect ratios preserved** — no square crops, no mobile "reflow" columns.
- **Videos autoplay on loop** as they scroll into view, pause when out of view.
- **Land/texture images are the stitching** — they space and separate people-clusters.
- **Gentle narrative flow, no rigid order.** The story (history → reclamation) pulls
  the viewer across the surface, but they are free to wander. There is a beginning and
  an end, not a strict left-to-right.

## Outcome
A single continuous, free-panning 2D canvas. Dragging in any direction walks the
history of the location and the story of its reclamation. Media is packed
interconnected (edges touching/overlapping), quilt-style, using images of the land
and texture images Bayard captured to space and separate the pieces.

## User
- The public — a memorial they scroll through and feel the weight of.
- RRMNHC / museum context — an exhibit-grade artifact.
- This is a **living-history** piece, not a scrapbook. Reclamation is the throughline.

## Why now
The Ste. Madeleine Métis Days 2026 weekend (Aug 21–23) generated real media — living
proof of reclamation. That media is the capstone the story was always building toward.

## Success
A museum-quality page, **designed by Bayard**. AI proposes the first layout; he
rearranges, reshapes, resizes, collages; we iterate section by section until the
composition is his. Viewers scroll the whole arc and it *feels* designed, not
auto-generated.

## Workflow — the joint venture
1. AI proposes a starting composition for a section.
2. Bayard rearranges / reshapes / gives feedback in a **working editor**.
3. Iterate until the section is his, then move to the next.
4. Sections chain into the continuous scroll.

The editor is the point, not a bolt-on. Bayard is the collagist.

## Binding constraints
- **Free tools only.**
- **The editor must work** — it is how Bayard authors the artifact.
- 200+ tiles is the known content set (photos, video, audio, **3D scans**).
- **Land/texture tiles are already in the set** — photos of plants, the cemetery,
  and the landscape captured during the weekend. They are not external assets.
- **Composition language:** interleave **people photos** and **land photos** — land
  images separate and give breathing room between people, like quilt blocks between
  stitches. This rhythm is core to the design and the AI seed must follow it.

## Out of scope
- Auto-generating a "finished" layout and calling it done.
- Infinite-torus random scatter as the end state.
- Reusing the last build's broken editors as-is — anything kept is rebuilt properly.

## Non-negotiables for the rebuild
- ONE editor + ONE viewer + ONE layout file. No divergent fragments.
- A written spec before any code (this is what the previous build lacked).
