# Timeline Animation Plan: From Ashes to Honour — Ste. Madeleine

## Source
- Historical narrative: MMF article "From ashes to honour: Red River Métis reclaim Ste. Madeleine" (July 25, 2024)
  URL: https://www.mmf.mb.ca/mmf-spotlight/from-ashes-to-honour-red-river-metis-reclaim-ste-madeleine
- Event context: Ste. Madeleine Métis Days 2026 (Aug 21–23, 2026) at the Historic Site of Ste. Madeleine, Binscarth MB
- Existing assets: ~230 photos in /home/bayarddevries/Pictures/Archive Windows/, flag animation videos in media/, TIFFs in Downloads/stemadeleine_tiffs/

## Timeline Structure (5 stages, ~6-8 seconds each)

### Stage 1: Settlement (1880s–1930s) — "A thriving Métis community"
- Visual: 1930s-era prairie homesteads, wood-sided houses with porches, sod or wood construction, Red River cart, people in period dress
- Style: sepia-toned historical photograph, slightly grainy film look
- Text overlay: "Late 1800s–1930s: Hundreds of Red River Métis settle Ste. Madeleine"
- Quote: "Families built homes, a church, and a community that thrived for decades."

### Stage 2: Devastation (1939) — "Ashes"
- Visual: Burned foundations, stove chimneys standing bare, bed frames twisted in ash, dogs' traces
- Style: stark black & white, high contrast, desaturated
- Text overlay: "1939: Under the Prairie Farm Rehabilitation Act, the government razes Ste. Madeleine"
- Quote: "When they came home, all they saw were the stove chimneys, stones, and the bedposts because the government had burned out their homes and shot their dogs." — Minister Fleury (descendant, Aug 2024)

### Stage 3: Loss (1939–2024) — "Generations of waiting"
- Visual: Empty prairie field, single weathered cross, distant figure looking toward horizon
- Style: muted, overcast, wind-swept prairie
- Text overlay: "1939–2024: Decades of displacement, oral histories, and waiting"
- Quote: "My grandfather was 27 when his dog was shot and his home was burnt... I'm here today and I'll take the message home and say, 'it's ours again.'" — Gail Welburn (descendant, 2024)

### Stage 4: Reclamation (July 2024) — "Righting a historical wrong"
- Visual: MOU signing ceremony, Premier Wab Kinew and President David Chartrand, new cross being raised, Métis cart pulled by horse, community gathering
- Style: modern photo realism, vibrant colours, crowds
- Text overlay: "July 19–21, 2024: Ste. Madeleine Métis Days — 100 acres returned"
- Quote: "One day, there will be a leader that'll come to us... and that leader is here now. His name is Wab Kinew." — President David Chartrand

### Stage 5: Continuing the reclamation (Aug 2026) — "The quilt goes on"
- Visual: CCAP community art project workshop, people gathered around tables creating art, Métis flag, hands working
- Style: warm, golden hour lighting, collaborative
- Text overlay: "August 21–23, 2026: Community art project continues the work of reclamation"
- Quote: "We never forget, and we never give up. Be proud today to be Red River Métis." — President Chartrand

## Technical approach
- Use FLUX 3 keyframe-to-video for each stage's base imagery (5 keyframes, 24fps, one pinned per ~5s)
- Overlay text + quotes via ffmpeg
- Combine into one ~30s timeline video
- Use existing flag-loop.mp4 as a transition element or intro/outro
- Final output: standalone MP4 for the quilt project, embeddable as a video tile

## Existing assets to leverage
- /home/bayarddevries/ste-madeleine-quilt/media/flag-loop.mp4 (5.4MB, 14.5s)
- /home/bayarddevries/ste-madeleine-quilt/media/flag-wave*.gif (3 animated flag elements)
- /home/bayarddevries/ste-madeleine-quilt/media/ste-madeleine-title.png (title card)
- /home/bayarddevries/ste-madeleine-quilt/media/ste-madeleine-sign-wordmark.png
