#!/usr/bin/env python3
"""Build timeline3.html from Penpot HTML export + photo assets."""
import os, re, json

ROOT = '/home/bayarddevries/ste-madeleine-quilt'
PENPOT_PATH = '/home/bayarddevries/.hermes/cache/documents/doc_292fb9b7a276_html timeline'
SHIFT_X = 2700

with open(PENPOT_PATH) as f:
    penpot_html = f.read()

# Extract board content
board_match = re.search(r'<div class="frame board[^"]*">(.+)</div>\s*$', penpot_html, re.DOTALL)
inner = board_match.group(1).strip() if board_match else penpot_html

# Photo map: rect class suffix -> local file path
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

# Inject background-image into photo rect divs
for cls_suffix, img_path in photo_map.items():
    full_path = os.path.join(ROOT, img_path)
    if os.path.exists(full_path):
        # Find the empty div: <div class="shape rect <cls>">\n  </div>
        old = f'<div class="shape rect {cls_suffix}">\n  </div>'
        new = f'<div class="shape rect {cls_suffix}" style="background-image:url(\'{img_path}\');background-size:cover;background-position:center;background-repeat:no-repeat;">\n  </div>'
        inner = inner.replace(old, new)

# Load rect positions from shapes.json
with open('/tmp/shapes.json') as f:
    shapes = json.load(f)

# Inject left/top/width/height into photo rect divs
for s in shapes:
    if s['type'] != 'rectangle' or s['w'] < 100:
        continue
    name = s['name'] or ''
    sid = s['id'][:8]
    x = s['x'] + SHIFT_X
    y = s['y']
    w = s['w']
    h = s['h']
    # Find the rect div by class pattern
    for cls_suffix in photo_map:
        pat = rf'(<div class="shape rect {re.escape(cls_suffix)})"'
        m = re.search(pat, inner)
        if m:
            replacement = m.group(1) + f'" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;"'
            inner = re.sub(pat, replacement, inner, count=1)
            break

# Inject spine position (Rectangle 22x9547)
spine_match = re.search(r'(<div class="shape rect rectangle-92e4684d40bb)">', inner)
if spine_match:
    spine_x = -2008 + SHIFT_X
    replacement = spine_match.group(1) + f'" style="left:{spine_x}px;top:363px;width:22px;height:9547px;background:#2a1f17;"'
    inner = inner.replace(spine_match.group(0), replacement)

# Inject Layer 1 (fog/background strip)
layer_match = re.search(r'(<div class="shape rect layer-1-92d9afe309c1)">', inner)
if layer_match:
    replacement = layer_match.group(1) + f'" style="left:27px;top:-68px;width:1353px;height:129px;background:rgba(200,190,170,0.5);"'
    inner = inner.replace(layer_match.group(0), replacement)

# Shift all data-x values by SHIFT_X
def shift_data_x(html, shift):
    def repl(m):
        x = float(m.group(1))
        y = float(m.group(2))
        return f'data-x="{x + shift}" data-y="{y}"'
    return re.sub(r'data-x="([^"]+)"\s+data-y="([^"]+)"', repl, html)

inner = shift_data_x(inner, SHIFT_X)

# The full HTML
full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Ste. Madeleine — Timeline of a Métis Community</title>
<style>
  :root {{
    --board-w: 1569;
    --board-h: 11000;
    --parchment: #f0e9db;
    --text-dark: #2a1f17;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html {{ background: var(--parchment); }}
  body {{
    background: var(--parchment);
    background-image: url('media/woodgrain-tile.jpg');
    background-repeat: repeat;
    font-family: 'EB Garamond', Georgia, serif;
    color: var(--text-dark);
    min-height: 100vh;
  }}
  body.no-woodgrain {{ background-image: none; }}
  .stage {{
    position: relative;
    width: {1569}px;
    height: {11000}px;
    margin: 0 auto;
    background: transparent;
    overflow: visible;
  }}
  /* All shapes absolutely positioned */
  .shape {{ position: absolute; box-sizing: border-box; }}
  /* Text nodes: absolute positioned by data-x/data-y */
  .text-node-html {{
    position: absolute;
    width: 430px;
  }}
  .text-node-html .rich-text p {{
    margin: 0;
    color: var(--text-dark);
  }}
  /* Card circles */
  .shape.circle {{ border-radius: 50%; background: #2a1f17; }}
  /* Ghost year 1958-2024: semi-transparent, breathing */
  .ghost-year-text {{
    opacity: 0.07;
    font-family: 'Barlow Semi Condensed', 'Barlow Condensed', Arial, sans-serif !important;
    font-weight: 400 !important;
    font-size: 340px !important;
    line-height: 1 !important;
    text-align: center;
    animation: breathe 14s ease-in-out infinite;
  }}
  @keyframes breathe {{
    0%, 100% {{ opacity: 0.07; }}
    50% {{ opacity: 0.13; }}
  }}
  /* Parallax on spine */
  .spine {{ background: #2a1f17 !important; }}
  @media (prefers-reduced-motion: reduce) {{
    .ghost-year-text {{ animation: none !important; opacity: 0.1 !important; }}
  }}
  @media (max-width: 1600px) {{
    .stage {{
      transform: scale(calc(100vw / 1600));
      transform-origin: top center;
    }}
  }}
</style>
</head>
<body>
<div class="stage">
{inner}
</div>
<script>
  (function() {{
    // Woodgrain fallback
    var test = new Image();
    test.onerror = function() {{ document.body.classList.add('no-woodgrain'); }};
    test.src = 'media/woodgrain-tile.jpg';
  }})();
  // Position all .text-node-html by data-x/data-y
  document.querySelectorAll('.text-node-html').forEach(function(el) {{
    var x = parseFloat(el.dataset.x);
    var y = parseFloat(el.dataset.y);
    if (!isNaN(x) && !isNaN(y)) {{
      el.style.left = x + 'px';
      el.style.top = y + 'px';
    }}
  }});
  // Tag ghost year text with animation class
  var ghostEls = document.querySelectorAll('.text-node-html');
  ghostEls.forEach(function(el) {{
    if (el.textContent.trim() === '1958-2024') {{
      el.classList.add('ghost-year-text');
    }}
  }});
  // Spine parallax
  var spine = document.querySelector('.spine');
  if (spine) {{
    var ticking = false;
    window.addEventListener('scroll', function() {{
      if (!ticking) {{
        requestAnimationFrame(function() {{
          spine.style.transform = 'translateY(' + (window.scrollY * -0.04) + 'px)';
          ticking = false;
        }});
        ticking = true;
      }}
    }});
  }}
</script>
</body>
</html>'''

with open(os.path.join(ROOT, 'timeline3.html'), 'w') as f:
    f.write(full_html)
print('Wrote timeline3.html')
print(f'Size: {len(full_html)} bytes')
