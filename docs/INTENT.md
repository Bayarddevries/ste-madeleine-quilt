# Ste. Madeleine Quilt — Intent

> Status: **CONFIRMED** by Bayard — 2026-08-25
> This is the source of truth. Re-read before any build decision.

## The one-sentence vision
One endlessly-scrolling, deliberately-composed page that tells the Ste. Madeleine
story — loss → resistance → reclamation — as a quilted collage of the weekend media
(photos, videos, audio, 3D scans) and the land itself, interleaving people and land.

## Outcome
A single continuous scroll. From top to bottom it carries the history of the location
and the story of its reclamation. Media is positioned quilt-style, next to one another,
using images of the land and texture images Bayard captured to space the pieces out.

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
