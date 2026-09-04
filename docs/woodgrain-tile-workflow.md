# Seamless Woodgrain Tile — Photoshop Workflow

## Source
- Path: `~/ste-madeleine-quilt/media/raw/woodgrain-source.tif`
- Size: **1440 × 2220** (true 2:3 — grave wood mark proportions)
- Format: TIFF (Photoshop reads natively)

## Goal
Produce `media/woodgrain-tile.jpg` at **1440 × 2220**, seamlessly tileable, ~2-4MB, ready for `background-repeat: repeat` in CSS.

## Workflow (8 steps)

1. **Open the source** in Photoshop: `File → Open → woodgrain-source.tif`
2. **Duplicate the layer** (`Cmd+J`) so you can A/B the original vs tiled
3. **Canvas size 2×** via `Image → Canvas Size`
   - Width: 200% → 2880px
   - Height: 200% → 4440px
   - Anchor: center (so existing image stays in middle of new canvas)
   - Check: "Relative"
4. **Tile the source into all 4 quadrants** — `Cmd+A` (select all on the source) → `Cmd+C` → paste into each of the 4 quadrants of the expanded canvas. Position so the original sits in the top-left; paste copies offset by 1440, 2220, and 1440+2220 for the other 3 quadrants.
5. **Heal the seams** using `Healing Brush Tool (J)` or `Content-Aware Fill (Edit → Content-Aware Fill)`:
   - **Vertical seams** (where left/right halves meet at x=1440) — most visible because horizontal grain repeats
   - **Horizontal seams** (where top/bottom halves meet at y=2220) — less visible but heal them too
   - **Center cross** (where 4 quadrants meet) — heal where all 4 corners converge
   - Sample from nearby grain texture; don't blur. Use small brush for fine grain, larger for knots/cracks.
6. **Optional: tone it** — heritage timeline is parchment-warm, not raw wood. Add a `Hue/Saturation` adjustment layer:
   - Saturation: -15 to -25 (desaturate the wood)
   - Hue: +5 to +10 (warm toward sepia)
   - Lightness: -5 (slightly darker)
   - Or use `Color Lookup` with a "Foggy Night" or "Sepia" preset at low opacity (15-25%)
7. **Crop to single tile**:
   - `Image → Canvas Size` → reset to **1440 × 2220** (no relative, set absolute)
   - Use `Crop Tool (C)` and drag from the center of the healed 4-quadrant canvas, **1440 × 2220** aspect ratio
   - **Pro tip**: pick a quadrant (any of the 4) that looks cleanest after healing. All 4 are identical tile segments, so any works.
8. **Save as JPG**:
   - `File → Save As → woodgrain-tile.jpg` (in `media/`)
   - Quality: 80-90 (file size ~2-4MB)
   - Embed color profile: sRGB

## Quick verification

After saving, test the tile in browser preview:
1. Open `http://localhost:8090/timeline3.html`
2. If you can see hard lines where the tile repeats → **not seamless yet**, re-do steps 5-7
3. If it just looks like one continuous woodgrain → **done**

## Common pitfalls

- **Saving at the wrong step** — if you save the 2× canvas instead of cropping back down, the file is 4× too big
- **Mismatched aspect** — 1440:2220 = ~0.649 ratio. If your crop is different, the tile won't tile cleanly
- **Hard seam in center** — usually means the original image had a hard edge. Go back to step 5 and zoom to 200% on the seam.

## If you don't have Photoshop

**GIMP** (free) does the same thing:
- `Filters → Map → Tile` to make 2×2 tiles
- `Filters → Enhance → Heal Transparency` or `Clone Tool` for seams
- Crop, export as JPG

**Or** I can do it in Python with PIL — but Photoshop gives you visual control over the seam-healing. Python seam-healing produces visible artifacts in woodgrain texture. Photoshop is the right tool for this one.
