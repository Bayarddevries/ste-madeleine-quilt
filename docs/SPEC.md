# Ste. Madeleine Quilt — SPEC

> Confirmed 2026-08-25. Read INTENT.md + PROJECT.md first.
> Editor tech: **DOM/HTML** (confirmed). One editor → layout.json → one scroll viewer.

## 1. The two surfaces
1. **Editor** — Bayard's composition studio. WYSIWYG with the viewer.
2. **Viewer** — the endless scroll, public-facing. Renders layout.json faithfully.

Both render the same tile model. If it looks right in the editor, it looks right in the viewer.

## 2. Content model (layout.json)

```jsonc
{
  "sections": [
    {
      "id": "ch1-thriving",
      "title": "Thriving Community",
      "chapter": 1,
      "height": 1800,            // section height in px (vertical scroll unit)
      "background": "land-01.jpg",  // optional land/texture bg image
      "tiles": [
        {
          "id": "w0",
          "type": "photo",       // photo | video | audio | scan | land | texture | text
          "src": "media/weekend-2026/1787451815986.png",
          "x": 120, "y": 300,    // top-left within section
          "w": 300, "h": 420,    // actual rendered size (NOT forced square)
          "rx": 18,              // corner radius (softens hard edges)
          "rotate": 0,           // degrees, for collage tilt
          "z": 3,                // z-order / layer
          "objectFit": "cover",  // cover | contain | fill — how src fills the box
          "caption": "Ste. Madeleine Métis Days 2026",
          "link": null           // e.g. opens 3D viewer / detail overlay
        }
      ]
    }
  ]
}
```

**Key properties:** every tile can be resized to any `w`/`h` (non-square), rotated, layered, and rounded. That's what makes it a collage, not a contact sheet.

## 3. Editor behavior
- **Section canvas** — one chapter at a time. Height is the section height; tiles position within it.
- **Tools:** select, drag-move, resize (handles + corners), rotate, z-order (bring forward/send back), corner radius, object-fit toggle, delete, duplicate.
- **Add media:** drag from a media drawer (thumbnails of all 200 + land/texture) onto the canvas.
- **Land/texture as background:** a section can have a bg image the tiles sit on — the "quilt backing."
- **Layers panel:** list tiles in z-order, select/rename/hide.
- **AI seed:** button generates a proposed starting layout for the current section; Bayard rearranges.
- **Save:** writes section back to layout.json. Draft state auto-saved in localStorage so no work is lost.
- **Multiple sections:** a section navigator (ch1…ch5 + any Bayard adds) to move between chapters.

## 4. Viewer behavior
- **Endless vertical scroll**, sections stitched top-to-bottom in chapter order.
- **Tiles render exactly as authored:** size, shape, rotation, layer, radius, fit.
- **Photo:** click → lightbox with caption.
- **Video:** inline play, muted-autoplay optional (tile is a video player).
- **Audio:** click → audio player (inline waveform/play button), tile shows a cover image + play control.
- **Scan (GLB):** tile shows a poster frame; click → inline interactive 3D viewer (drag-orbit) — **first-class**, not a separate tab.
- **Scroll feel:** gentle parallax / fade on land-texture backgrounds, tiles settle into place. Must feel designed, not like a page of images.

## 5. Tech stack (free, local)
- Plain HTML/CSS/JS, no build step (consistent with this repo's serving model).
- `layout.json` served alongside; editor fetches + writes it.
- **3D viewer:** use a local, vendored GLB loader (model-viewer static bundle already downloaded — the `excalidraw-0.18.1.tgz` was the wrong experiment; vendor `@google/model-viewer` or a small Three.js loader locally, free).
- Serving: local Python http server (existing 8090 pattern) — no framework needed.

## 6. File layout (replaces fragmented legacy)
```
docs/INTENT.md, PROJECT.md, SPEC.md
index.html          -> THE VIEWER (endless scroll) [replaces legacy index.html torus]
editor.html         -> THE EDITOR (composition studio)
layout.json         -> single source of truth
media/              -> content (unchanged)
assets/js/viewer.js, assets/js/editor.js, assets/js/glb.js
assets/css/
vendor/model-viewer/ (or three.min.js + GLTFLoader)  [local, free]
```

## 7. Acceptance criteria
- [ ] Editor: place, drag, resize non-square, rotate, layer, round corners, set object-fit, add land/texture bg. All save to layout.json.
- [ ] Viewer: renders layout.json EXACTLY (editor WYSIWYG).
- [ ] All 5 chapters + the 2026 weekend section present in order.
- [ ] 200 tiles available in the editor's media drawer; 3D scans open interactive inline viewer.
- [ ] Land/texture images available as backgrounds + spacing tiles.
- [ ] Loads 200 tiles without crash on a normal laptop (perf).
- [ ] Serving locally on 8090.

## 8. Phased build order
- **P1 (editor core):** viewer.html shell + layout.json loader + DOM renderer. Editor loads section, drag/resize/rotate/layer/round/fit, save.
- **P2 (media & 3D):** media drawer (200 tiles), land/texture integration, GLB interactive viewer.
- **P3 (narrative):** 5 chapters + weekend section, background/parallax, scroll polish.
- **P4 (joint venture):** AI seed → Bayard rearranges each section → finalize.
