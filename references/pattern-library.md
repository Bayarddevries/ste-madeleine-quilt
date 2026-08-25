# Ste. Madeleine Quilt — Pattern Library

> Hand these to any future agent/session instead of letting it reinvent the wheel.
> Source: the working P1 build + ideas lifted from beautifului.dev (2026-08-25).
> The goal (per the tweet that started this): a "lego of components" so designs
> stop looking like slop and never regress.

## Principles
- **One renderer, two surfaces.** `assets/js/renderer.js` is THE renderer for both
  viewer and editor. If it looks right in the editor, it looks right in the viewer.
  Never fork rendering per surface.
- **One source of truth:** `layout.json`. Editor writes it (POST /save-layout);
  viewer reads it. No divergent manifests.
- **WYSIWYG guarantee:** the editor passes `{noScale:true}` to render tiles at full
  design scale; the viewer scales/reflows but never changes tile data.

## Component patterns

### 1. Responsive section (mobile-first)
- Each section carries a `designWidth` (the canvas you compose on) and `height`.
- **Desktop (≥700px):** section renders at designWidth, scales down proportionally
  if needed (Figma-style) — `scale(availW/designW)` with `transform-origin: top left`.
- **Mobile (<700px):** `renderReflow()` switches to a centered masonry —
  2 columns ≥480px, 1 column below. Media tiles (photo/video/scan/audio) reflow at
  readable sizes; land/text become dividers. This REPLACES naive scale-down, which
  made a 200px tile render at 88px (unreadable).
- Resize handler in the viewer re-renders on orientation change.
- **Key fix:** tile `type` must be a real render type (`photo`, `video`, `scan`,
  `audio`, `land`, `text`). The seed's `people` classifier is a CURATION TAG — map it
  to `photo` before saving, or the reflow filter silently drops 197 tiles.

### 2. Tile inspector (inspired by Beautiful UI's "Fine-tune Card")
- The editor's right panel edits the selected tile: X/Y, W/H, Rotation, Radius,
  object-fit, caption, plus layering (front/back/up/down), duplicate, delete.
- This is exactly Beautiful UI's **Fine-tune Card** (W/H/Radius/Opacity on a selected
  element). Ours is the memory-memorial version of that primitive.

### 3. 3D scan tile (first-class, not an afterthought)
- GLB tiles render as a poster frame with a "3D" tag (`renderer` detects `.glb` by
  src). Click opens an inline `<model-viewer>` (local vendored `media/vendor/`, free)
  with camera-controls + auto-rotate.
- model-viewer is served as `<script type="module">` from the local vendor file — no CDN.

### 4. Audio tile + shared player
- Audio tiles render a cover with a play button. One shared `<audio>` bar at the
  bottom of the page; clicking a tile's play loads and plays, toggles off on re-click.
- Lightbox handles photo (img), video (controls), and scan (model-viewer).

### 5. Land/texture as quilt backing
- Sections can have a `background` land image the tiles sit on (the "quilt backing").
- Land/text tiles get a soft radial vignette (`::after`) so they read as backing, not
  as plain photos.

### 6. Loading polish (inspired by Beautiful UI's "Loading State")
- Not yet implemented. Idea: a pixel-grid shimmer / lazy-load placeholder for the 200
  tiles so the scroll doesn't pop empty. Low priority.

## Styling tokens
- Palette (RRMNHC heritage): bg `#1a120b`, parchment `#e8dcc0`, gold `#c9a227`,
  crimson `#b3362a`. See `:root` in `assets/css/quilt.css`.
- Serif (Georgia) for narrative body, Barlow Condensed for labels/titles.
- No purple gradients, no rounded-everything, no generic AI look.

## Anti-patterns (what the previous build got wrong — do not repeat)
- Naive scale-down of a huge collage on mobile (unreadable 88px tiles).
- Three divergent editors. One real editor only.
- Tile types that don't map to a render branch (`people` ≠ a type).
- Broken `object-fit:cover` forcing everything square — tiles must support non-square
  shapes via W/H + rotate.
