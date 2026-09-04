#!/usr/bin/env python3
"""Rebuild timeline3.html from Penpot HTML export - clean version."""
import os, re, json

ROOT = '/home/bayarddevries/ste-madeleine-quilt'
PENPOT_PATH = '/home/bayarddevries/.hermes/cache/documents/doc_292fb9b7a276_html timeline'
SHIFT_X = 2700  # shift everything into positive x

with open(PENPOT_PATH) as f:
    penpot_html = f.read()

# Photo map: rect class suffix -> local file path (verified exist)
photo_map = {
    'screenshot-931de716b095': 'media/timeline/manitoba_museum_beliveau.jpg',
    'm-g3177-932077e58989': 'media/thumbs/_MG_3177.jpg',
    'm-g2904-9320c794f093': 'media/thumbs/_MG_2904.jpg',
    'm-g2869-9321e18ff538': 'media/thumbs/_MG_2869.jpg',
    'm-g3140-932218ff9f84': 'media/thumbs/_MG_3140.jpg',
    'm-g2850-932248cbe2d2': 'media/thumbs/_MG_2850.jpg',
    'm-g3132-932295567126': 'media/thumbs/_MG_3132.jpg',
    'm-g2828-9320e4f3d099': 'media/thumbs/_MG_2828.jpg',
    'm-g3138-9401f59567e5': 'media/thumbs/_MG_3138.jpg',
    'm-g3171-94027a7fe453': 'media/thumbs/_MG_3171.jpg',
    'm-g2878-9409b1715d61': 'media/thumbs/_MG_2878.jpg',
    'm-g29422-940b88394005': 'media/thumbs/_MG_2942.jpg',
    'm-g2929-941137a2dda2': 'media/thumbs/_MG_2929.jpg',
    'm-g3175-9411eba52c65': 'media/thumbs/_MG_3175.jpg',
}

# Add background-image to photo divs
for cls, img in photo_map.items():
    full = os.path.join(ROOT, img)
    if os.path.exists(full):
        old = f'<div class="shape rect {cls}">\n  </div>'
        new = f'<div class="shape rect photo {cls}" data-photo="{img}">\n  </div>'
        if old in penpot_html:
            penpot_html = penpot_html.replace(old, new)

# Inject spine position
penpot_html = penpot_html.replace(
    '<div class="shape rect rectangle-92e4684d40bb">\n  </div>',
    '<div class="shape rect spine" data-x="-2008" data-y="363" data-w="22" data-h="9547">\n  </div>'
)

# Inject Layer 1 strip
penpot_html = penpot_html.replace(
    '<div class="shape rect layer-1-92d9afe309c1">\n  </div>',
    '<div class="shape rect layer-1" data-x="27" data-y="-68" data-w="1353" data-h="129">\n  </div>'
)

# Shift all data-x values by SHIFT_X
def shift_x(html, shift):
    def repl(m):
        x = float(m.group(1))
        y = float(m.group(2))
        return f'data-x="{x + shift}" data-y="{y}"'
    return re.sub(r'data-x="([^"]+)"\s+data-y="([^"]+)"', repl, html)

penpot_html = shift_x(penpot_html, SHIFT_X)

# Build final HTML - clean and simple
output = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Ste. Madeleine — Timeline of a Métis Community</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    background: #f0e9db;
    background-image: url('media/woodgrain-tile.jpg');
    background-repeat: repeat;
    font-family: 'EB Garamond', Georgia, serif;
    color: #2a1f17;
  }}
  body.no-woodgrain {{ background-image: none; }}
  .stage {{
    position: relative;
    width: 1569px;
    height: 11000px;
    margin: 0 auto;
  }}
  /* Spine */
  .spine {{
    position: absolute;
    background: #2a1f17;
  }}
  /* Layer 1 strip (the gray fog/header band) */
  .layer-1 {{
    position: absolute;
    background: rgba(200, 190, 170, 0.5);
  }}
  /* Photo rects - get background images via [data-photo] */
  .photo {{
    position: absolute;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
  }}
  /* All text nodes positioned absolutely by data-x/data-y */
  .text-node-html {{
    position: absolute;
    width: 430px;
  }}
  .text-node-html .paragraph {{
    margin: 0 0 0.5em 0;
  }}
  /* Cards (component frames) - the quote text boards */
  .frame.component {{
    position: absolute;
  }}
  .frame.component .frame.board {{
    position: relative;
  }}
  .frame.component .shape.circle {{
    position: absolute;
    width: 54px;
    height: 54px;
    border-radius: 50%;
    background: #2a1f17;
  }}
  /* Year text - bigger, serif */
  .shape.text[class*="-1870"] .text-node,
  .shape.text[class*="-1885"] .text-node,
  .shape.text[class*="-1913"] .text-node,
  .shape.text[class*="-1922"] .text-node,
  .shape.text[class*="-1935"] .text-node,
  .shape.text[class*="-1938"] .text-node,
  .shape.text[class*="-1958"] .text-node,
  .shape.text[class*="-2024"] .text-node,
  .shape.text[class*="-2026"] .text-node {{
    font-family: 'Barlow Semi Condensed', 'Barlow Condensed', Arial, sans-serif;
    font-weight: 600;
    font-size: 80px;
    line-height: 1;
  }}
  /* Ghost year: very large, low opacity, breathing */
  .shape.text.ghost-year .text-node {{
    font-family: 'Barlow Semi Condensed', 'Barlow Condensed', Arial, sans-serif;
    font-weight: 400;
    font-size: 320px;
    line-height: 1;
    opacity: 0.08;
    animation: breathe 14s ease-in-out infinite;
    text-align: center;
  }}
  @keyframes breathe {{
    0%, 100% {{ opacity: 0.08; }}
    50% {{ opacity: 0.14; }}
  }}
  /* Banner text - large title */
  .shape.text.banner .text-node {{
    font-family: 'Barlow Semi Condensed', 'Barlow Condensed', Arial, sans-serif;
    font-weight: 700;
    font-size: 64px;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  @media (prefers-reduced-motion: reduce) {{
    .shape.text.ghost-year .text-node {{
      animation: none;
      opacity: 0.1;
    }}
  }}
  /* Mobile/tablet: scroll-friendly scale */
  @media (max-width: 1600px) {{
    .stage {{
      transform: scale(calc(100vw / 1600));
      transform-origin: top left;
    }}
  }}
</style>
</head>
<body>
<div class="stage">
{penpot_html}
</div>
<script>
  // Woodgrain fallback
  (function() {{
    var test = new Image();
    test.onerror = function() {{ document.body.classList.add('no-woodgrain'); }};
    test.onload = function() {{ /* loaded OK */ }};
    test.src = 'media/woodgrain-tile.jpg';
  }})();

  // Position text by data-x/data-y
  document.querySelectorAll('.text-node-html').forEach(function(el) {{
    var x = parseFloat(el.dataset.x);
    var y = parseFloat(el.dataset.y);
    if (!isNaN(x) && !isNaN(y)) {{
      el.style.left = x + 'px';
      el.style.top = y + 'px';
    }}
  }});

  // Position cards (component frames) - need to find their position from inner text
  document.querySelectorAll('.frame.component').forEach(function(card) {{
    // Find the text inside, use its data-x/data-y to position the card
    var inner = card.querySelector('.text-node-html');
    if (inner) {{
      var tx = parseFloat(inner.dataset.x);
      var ty = parseFloat(inner.dataset.y);
      if (!isNaN(tx) && !isNaN(ty)) {{
        card.style.left = (tx - 30) + 'px';
        card.style.top = (ty - 30) + 'px';
      }}
    }}
  }});

  // Position cards' circles - relative to card
  document.querySelectorAll('.frame.component .shape.circle').forEach(function(c) {{
    c.style.left = '0px';
    c.style.top = '0px';
  }});

  // Position rect with data-x/data-y (spine, layer-1)
  document.querySelectorAll('.shape.rect[data-x]').forEach(function(el) {{
    el.style.left = parseFloat(el.dataset.x) + 'px';
    el.style.top = parseFloat(el.dataset.y) + 'px';
    el.style.width = el.dataset.w + 'px';
    el.style.height = el.dataset.h + 'px';
  }});

  // Position photos with background images (load positions from shapes.json via data-attrs)
  document.querySelectorAll('.shape.rect.photo').forEach(function(el) {{
    // The photo positions need to be injected - see below
  }});
</script>
</body>
</html>'''

with open(os.path.join(ROOT, 'timeline3.html'), 'w') as f:
    f.write(output)
print(f'Wrote {len(output)} bytes')
