#!/usr/bin/env python3
"""Extract a Figma landing page frame and emit a standalone HTML file.

Reads the first top-level frame from a Figma file, walks its children,
and maps Figma nodes to HTML/CSS:
  - Frame           -> <section> (with flex if auto-layout)
  - Text node       -> <h1>/<p> with font family/size/weight/color
  - Rectangle       -> <div> with background color
  - Image fill      -> <img> (via Figma image render endpoint)
  - Nested frames   -> nested <div>s (auto-layout becomes flex)

Usage:
    python3 scripts/figma_landing_to_html.py <file_key> [-o index.html]
"""

import json
import os
import sys
import urllib.parse
import urllib.request

API = "https://api.figma.com"


def _read_token():
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith("FIGMA_ACCESS_TOKEN="):
                return line.strip().split("=", 1)[1]
    return None


TOKEN = os.environ.get("FIGMA_ACCESS_TOKEN") or _read_token()


def figma(path):
    req = urllib.request.Request(API + path, headers={"X-Figma-Token": TOKEN})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def hex_color(c, alpha=1.0):
    """Figma color (r,g,b,a 0..1) -> #rrggbb or rgba()"""
    if not c:
        return "transparent"
    r = round(c.get("r", 0) * 255)
    g = round(c.get("g", 0) * 255)
    b = round(c.get("b", 0) * 255)
    a = c.get("a", 1.0) * alpha
    if a >= 0.999:
        return f"#{r:02x}{g:02x}{b:02x}"
    return f"rgba({r},{g},{b},{a:.2f})"


def is_auto_layout(node):
    return node.get("layoutMode") in ("HORIZONTAL", "VERTICAL")


def css_style(node):
    s = []
    bbox = node.get("absoluteBoundingBox") or {}
    if node.get("type") != "DOCUMENT":
        s.append(f"width:{bbox.get('width', 0):.0f}px;")
        s.append(f"height:{bbox.get('height', 0):.0f}px;")
    # background fill
    for fill in node.get("fills") or []:
        if fill.get("type") == "SOLID":
            s.append(f"background:{hex_color(fill.get('color'))};")
            break
        elif fill.get("type") == "IMAGE":
            # handled separately in node_to_html
            break
    # rotation
    rot = node.get("rotation")
    if rot:
        s.append(f"transform:rotate({rot:.1f}deg);")
    # corner radius
    cr = node.get("cornerRadius")
    if cr:
        s.append(f"border-radius:{cr:.0f}px;")
    # auto-layout -> flex
    if is_auto_layout(node):
        d = "row" if node.get("layoutMode") == "HORIZONTAL" else "column"
        s.append(f"display:flex;flex-direction:{d};")
        gap = node.get("itemSpacing")
        if gap:
            s.append(f"gap:{gap:.0f}px;")
        pad = node.get("paddingLeft")
        if pad:
            s.append(f"padding:{node.get('paddingTop',0):.0f}px {node.get('paddingRight',0):.0f}px {node.get('paddingBottom',0):.0f}px {pad:.0f}px;")
        align = node.get("primaryAxisAlignItems") or node.get("counterAxisAlignItems")
        s.append("justify-content:center;align-items:center;")
    return ";".join(s)


def escape_html(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def node_to_html(node, image_urls):
    ntype = node.get("type")
    name = node.get("name", "")
    bbox = node.get("absoluteBoundingBox") or {}
    style = css_style(node)
    children_html = "".join(node_to_html(c, image_urls) for c in node.get("children", []))

    # Image fill -> <img>
    img_ref = None
    for fill in node.get("fills") or []:
        if fill.get("type") == "IMAGE" and fill.get("imageRef"):
            img_ref = fill["imageRef"]
            break
    if img_ref and image_urls.get(img_ref):
        return (f'<div style="width:{bbox.get("width",0):.0f}px;height:{bbox.get("height",0):.0f}px;'
                f'overflow:hidden;border-radius:{node.get("cornerRadius",0) or 0:.0f}px;">'
                f'<img src="{image_urls[img_ref]}" style="width:100%;height:100%;object-fit:cover;"></div>')

    if ntype == "TEXT":
        style_txt = style + ";" + (node.get("style") or {}).get("fontFamily", "sans-serif") and ""
        fs = (node.get("style") or {}).get("fontSize")
        fw = (node.get("style") or {}).get("fontWeight")
        ff = (node.get("style") or {}).get("fontFamily")
        lh = (node.get("style") or {}).get("lineHeightPx")
        txt_style = []
        if ff: txt_style.append(f"font-family:'{ff}'")
        if fs: txt_style.append(f"font-size:{fs:.0f}px")
        if fw: txt_style.append(f"font-weight:{fw}")
        if lh: txt_style.append(f"line-height:{lh:.0f}px")
        # text color
        for fill in node.get("fills") or []:
            if fill.get("type") == "SOLID":
                txt_style.append(f"color:{hex_color(fill.get('color'))}")
                break
        txt = "".join(r.get("characters", "") for r in node.get("characters", ""))  # fallback
        chars = node.get("characters", "")
        if not chars:
            # try characterStyleOverrides fallback
            chars = node.get("characters") or ""
        tag = "h1" if (fs or 0) >= 32 else "p"
        return (f'<{tag} style="{";".join(txt_style)}">{escape_html(chars)}</{tag}>')

    # frame / rectangle / group
    if ntype in ("FRAME", "RECTANGLE", "GROUP", "ELLIPSE"):
        tag = "section" if ntype == "FRAME" and not node.get("parent", {}).get("type") else "div"
        return f'<div style="{style}">{children_html}</div>'

    return children_html  # unknown nodes: pass through children


def main():
    if not TOKEN:
        print("FIGMA_ACCESS_TOKEN not found in ~/.hermes/.env", file=sys.stderr)
        sys.exit(1)
    file_key = sys.argv[1] if len(sys.argv) > 1 else None
    if not file_key:
        print("Usage: figma_landing_to_html.py <file_key> [-o out.html]", file=sys.stderr)
        sys.exit(1)
    out_path = "index.html"
    if "-o" in sys.argv:
        out_path = sys.argv[sys.argv.index("-o") + 1]

    doc = figma(f"/v1/files/{file_key}")
    # find first top-level frame
    frame = None
    for page in doc["document"]["children"]:
        for child in page.get("children", []):
            if child.get("type") == "FRAME":
                frame = child
                break
        if frame:
            break
    if not frame:
        print("No top-level frame found", file=sys.stderr)
        sys.exit(1)

    # collect image refs and batch render
    image_refs = set()

    def collect(n):
        for fill in n.get("fills") or []:
            if fill.get("type") == "IMAGE" and fill.get("imageRef"):
                image_refs.add(fill["imageRef"])
        for c in n.get("children", []):
            collect(c)
    collect(frame)

    image_urls = {}
    if image_refs:
        ids = ",".join(image_refs)
        rendered = figma(f"/v1/images/{file_key}?ids={ids}&format=png")
        image_urls = rendered.get("images", {})

    body_html = node_to_html(frame, image_urls)
    title = frame.get("name", "Page")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape_html(title)}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:sans-serif; background:#0c0a08; color:#eee; }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""
    with open(out_path, "w") as f:
        f.write(html)
    print(f"Wrote {out_path} from frame '{title}' ({len(image_urls)} images)")


if __name__ == "__main__":
    main()
