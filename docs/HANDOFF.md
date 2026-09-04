# Ste. Madeleine Timeline — Session Handoff

**Date:** 2026-09-04
**Session ID:** `20260902_145753_5a0100` (search Hermes: `session_search(query='ste madeleine timeline', session_id='20260902_145753_5a0100')`)

---

## Project

Build a heritage timeline webpage for the Ste. Madeleine Métis community, designed in Penpot, exported as a self-contained HTML page for an exhibit.

**Working directory:** `~/ste-madeleine-quilt/`
**Local server:** `python3 serve.py 8090` (currently running, pid logged separately)
**Public tunnel:** `https://pop-os.tail4625c0.ts.net/` proxies to `localhost:8090` (Tailscale funnel running, may need restart)

---

## Where We Are

The HTML is built (`timeline3.html`, ~40KB) using Penpot's own HTML export as the source — real text, real positions, real structure. Photos are mapped back onto the photo rectangles. Woodgrain tile is referenced as a background. Animations defined but not invasive.

**What works (verified):**
- `timeline3.html` exists with 9 timeline entry cards, 1 spine, 1 ghost year, 2 banners, 1 credits block
- All 13 photos from `media/thumbs/` are mapped to their Penpot rectangles
- 26 text elements with real content from Penpot export
- Spine (vertical line) at correct position
- Woodgrain background with fallback
- Accessibility: `prefers-reduced-motion` respected

**What's broken / not delivered:**
- User reports the page "doesn't look anything like Penpot" and "looks even worse" — multiple iterations did not satisfy
- The agent's vision tools (vision_analyze, browser_exec) cannot connect to localhost for visual QA
- Tailscale public URL does work for live viewing IF the user can reach it remotely, but user is on Telegram without remote PC access
- Woodgrain tile (`media/raw/woodgrain-tile.jpg`) is 2880×4440 TIFF mislabeled as JPG — needs Photoshop crop to 1440×2220 per `docs/woodgrain-tile-workflow.md`
- The actual `vision_analyze` and `browser_exec` tools have guardrails (private URL block, wrapper payload bug) that prevent the agent from self-verifying

---

## The Core Problem (Critical Context for New Agent)

**The agent cannot see its own work.** Vision tools fail on local dev servers, browser navigation is blocked to localhost, and headless Chrome from subprocess can take screenshots but vision analysis of those screenshots returned only wrapper payloads (not real descriptions) during this session. The Tailscale public tunnel works but vision analysis of public-URL screenshots also has been unreliable.

This means: **the user has been the only one able to verify the page renders correctly.** Every iteration was "I made changes, you check, you say it's wrong, I make more changes, you check again." The user got frustrated with the cycle and ended the session.

**Do NOT keep rebuilding without solving the visual verification problem first.** The two viable paths:
1. **Get vision/browser tools working** — vision_analyze needs to actually dispatch to vision model; browser_exec needs a localhost allowlist. Both fixes live in the parent Hermes dispatcher (not in user-editable space from this session).
2. **Send self-contained HTML to the user** — single file with all images base64-embedded. No server needed. User can open in any browser anywhere.

---

## Decisions Already Made

- **Approach 1 selected** (PNG export + absolute HTML) over Approaches B/C/D
- **No 2016 card** — removed (no source material)
- **4px spacing grid** approved
- **Attribution format:** full book title in credits block at bottom; per-quote attribution has section/page context but NO subtitle (overflow risk at 22px Garamond)
- **Sources:** Z&Z book (Zeilig & Zeilig, *Ste. Madeleine: Community Without a Town — Métis Elders in Interview*, Pemmican Publications, 1987) + MMF modern quotes with speaker/date
- **Font substitutes:** Noto Serif (not EB Garamond, not installed); Barlow Condensed for years/banners
- **Reveal animation disabled** because IntersectionObserver + headless screenshot = invisible content; animations kept as CSS only
- **Photo source:** `media/thumbs/` (Penpot rectangles have no image fills, only inner textures)

---

## Files & Locations

**Verified data sources:**
- `~/ste-madeleine-quilt/timeline3.html` — current build (40KB)
- `~/ste-madeleine-quilt/media/exports/` — 51 PNGs (15 photo + 9 year + 26 text)
- `~/ste-madeleine-quilt/media/thumbs/` — 14 original photos
- `~/ste-madeleine-quilt/media/raw/woodgrain-source.tif` — 1440×2220 woodgrain source
- `~/ste-madeleine-quilt/media/raw/woodgrain-tile.jpg` — 2880×4440 (needs crop)
- `~/ste-madeleine-quilt/scripts/export_all.py` — re-runnable Penpot export
- `~/ste-madeleine-quilt/scripts/build_timeline3.py` — current build script
- `/tmp/shapes.json` — all Penpot shape positions
- `/tmp/book-ocr/timeline_quotes.md` — 5,232 chars of pull quotes from Z&Z book
- `~/ste-madeleine-quilt/docs/HANDOFF.md` — this file
- `~/ste-madeleine-quilt/docs/woodgrain-tile-workflow.md` — 8-step Photoshop guide

**Penpot HTML export:** `/home/bayarddevries/.hermes/cache/documents/doc_292fb9b7a276_html timeline`

**Workspace fix notes:** `~/workspace/tool-fixes.md`

---

## What To Try First in a New Session

1. **Solve visual verification first** — don't repeat the loop. Either:
   - Restart Hermes with vision/loopback tools working (user action required)
   - Build a self-contained HTML with base64 images and send to user as Telegram file
2. **If verifying works:** screenshot the current `timeline3.html`, describe what you see, fix specific issues
3. **If woodgrain is missing:** the JPEG exists but is un-cropped. Either Photoshop per the workflow doc, or skip woodgrain and use parchment-only background

---

## Constraints

- **No Chinese, no em dashes** (user preference)
- **English only** (hard rule)
- **Free tools only** — no paid APIs
- **No reveal animation that hides content** in screenshots
- **Heritage tone** — no bouncing/rotating animations
- **Reduced motion respected**
- **All animatable per user request:** "I want to be able to animate these things... move them into position"
- **Display quality must "cut the mustard"** (user's words)

---

## Key User Messages (verbatim, for context)

- "I want to be able to work in penpot or some design tool. I want you to be able to export in some way. Preferably just direct code then I want you to be able to take that code rework it so that it looks like the work that we did in pinpot review the work that you did confirm that it looks the way it should and then be able to send it to me right now."
- "so how do we execute option 1" (Tailscale funnel — partial success, but vision still broken)
- "I'm not on that PC !"
- "Stop I want you to wrap this up. I don't think that you're going to be able to help out. I think that we're having context issues so I want you to document everything including the challenges we've had and give me the session number for reference so I can have a new agent pickup"

---

## Recovery

To resume this work: `session_search(query='ste madeleine timeline', session_id='20260902_145753_5a0100')` will return this session. The new agent should read `~/ste-madeleine-quilt/docs/HANDOFF.md` first.
