#!/usr/bin/env python3
"""Extract a quilt composition from a Figma file and emit layout.json.

Bayard designs the quilt in Figma. This script reads the composition via the
Figma REST API (personal access token in ~/.hermes/.env as FIGMA_ACCESS_TOKEN)
and converts it into the quilt viewer's layout.json format.

Conventions (agreed workflow):
  - Top-level frames in the Figma file = quilt sections.
    Frame name = section title. Chapter number is derived from frame order
    (Figma frames are returned top-to-bottom).
  - A frame whose name starts with "bg:" is a section background image.
  - Every other frame / rectangle / image inside a section frame = a tile.
  - Tiles named with a prefix become special tile types:
      VIDEO  -> video tile
      AUDIO  -> audio tile
      3D     -> 3D scan tile
      TEXT   -> text tile
    otherwise the tile is a photo / land / texture (determined by fill image).
  - Tile rotation, corner radius, z-order (layer order), and position/size
    all come straight from Figma's data.

Usage:
    python3 scripts/figma_to_layout.py <figma_file_key> [-o layout.json]
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


def node_type_fill(node):
    """Return the image src for a node if it has an image fill."""
    for fill in node.get("fills") or []:
        if fill.get("type") == "IMAGE" and fill.get("imageRef"):
            return fill["imageRef"]
    return None


def main():
    if not TOKEN:
        print("FIGMA_ACCESS_TOKEN not found in ~/.hermes/.env", file=sys.stderr)
        sys.exit(1)

    file_key = sys.argv[1] if len(sys.argv) > 1 else None
    if not file_key:
        print("Usage: figma_to_layout.py <file_key> [-o out.json]", file=sys.stderr)
        sys.exit(1)

    out_path = "layout.json"
    if "-o" in sys.argv:
        out_path = sys.argv[sys.argv.index("-o") + 1]

    doc = figma(f"/v1/files/{file_key}")
    # Resolve image refs to downloadable URLs in one batch
    image_refs = set()
    sections = []

    def walk(node, parent_frame_idx=None, section=None):
        ntype = node.get("type", "")
        name = node.get("name", "")
        bbox = node.get("absoluteBoundingBox") or {}

        # Top-level frames become sections
        if parent_frame_idx is None:
            if ntype == "FRAME" or ntype == "CANVAS":
                sec = {
                    "id": f"ch{len(sections) + 1}-{slug(name)}",
                    "title": name,
                    "chapter": len(sections) + 1,
                    "height": int(bbox.get("height", 1800)),
                    "width": int(bbox.get("width", 1200)),
                    "tiles": [],
                }
                sections.append(sec)
                for child in node.get("children", []):
                    walk(child, parent_frame_idx=len(sections) - 1, section=sec)
            return

        if not section:
            return

        # Section background
        if parent_frame_idx is not None and name.lower().startswith("bg:"):
            ref = node_type_fill(node)
            if ref:
                image_refs.add(ref)
                section["background"] = ref
            return

        # Tiles
        if ntype in ("FRAME", "RECTANGLE", "ELLIPSE", "IMAGE", "COMPONENT"):
            ref = node_type_fill(node)
            if ref:
                image_refs.add(ref)

            ttype = "photo"
            uname = name.upper()
            if uname.startswith("VIDEO"):
                ttype = "video"
            elif uname.startswith("AUDIO"):
                ttype = "audio"
            elif uname.startswith("3D") or uname.startswith("SCAN"):
                ttype = "scan"
            elif uname.startswith("TEXT"):
                ttype = "text"
            elif uname.startswith("LAND"):
                ttype = "land"

            tile = {
                "id": node.get("id", ""),
                "type": ttype,
                "name": name,
                "x": round(bbox.get("x", 0) - (section.get("_bx", 0))),
                "y": round(bbox.get("y", 0) - (section.get("_by", 0))),
                "w": round(bbox.get("width", 100)),
                "h": round(bbox.get("height", 100)),
                "rotate": round(node.get("rotation", 0) % 360, 1),
                "z": len(section["tiles"]),  # layer order
                "rx": round(node.get("cornerRadius", 0) or 0),
            }
            if ref:
                tile["src"] = ref
            section["tiles"].append(tile)

            for child in node.get("children", []):
                walk(child, parent_frame_idx, section)

    # First pass: walk, record absolute frame origin
    for node in doc.get("document", {}).get("children", []):
        bbox = node.get("absoluteBoundingBox") or {}
        # store origin so tile coords are relative to their section
        if node.get("type") == "FRAME" or node.get("type") == "CANVAS":
            node["_bx"] = bbox.get("x", 0)
            node["_by"] = bbox.get("y", 0)
        walk(node)

    # Batch-fetch rendered images
    image_results = {}
    if image_refs:
        ids = ",".join(image_refs)
        rendered = figma(f"/v1/images/{file_key}?ids={ids}&format=png")
        image_results = rendered.get("images", {})

    # Swap imageRef -> download URL
    for sec in sections:
        if sec.get("background"):
            sec["background"] = image_results.get(sec["background"], sec["background"])
        for tile in sec["tiles"]:
            if tile.get("src"):
                tile["src"] = image_results.get(tile["src"], tile["src"])

    # Drop internal bookkeeping
    for sec in sections:
        sec.pop("_bx", None)
        sec.pop("_by", None)

    layout = {"sections": sections}
    with open(out_path, "w") as f:
        json.dump(layout, f, indent=2)
    total = sum(len(s.get("tiles", [])) for s in sections)
    print(f"Wrote {out_path}: {len(sections)} sections, {total} tiles")
    for s in sections:
        print(f"  - {s['title']}: {len(s['tiles'])} tiles")


def slug(name):
    return "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-") or "section"


if __name__ == "__main__":
    main()
