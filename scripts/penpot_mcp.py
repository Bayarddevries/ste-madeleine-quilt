#!/usr/bin/env python3
"""Penpot MCP client — reusable for the Ste. Madeleine timeline project.

Reads the Penpot MCP userToken from ~/.hermes/config.yaml (mcp_servers.penpot.url),
so no secret lives in this repo. Holds the MCP session (initialize -> initialized
notification -> tools/call) and adds a browser User-Agent to defeat Cloudflare.

Usage:
  python3 penpot_mcp.py exec "JS code..."     # run plugin JS, prints returned JSON
  python3 penpot_mcp.py export <shapeId> <out.png>   # export shape as PNG
  python3 penpot_mcp.py shapes                 # list board ids + top-level shapes

The plugin JS runs inside the Penpot editor context (design.penpot.app), so it has
access to `penpot`, `penpot.currentPage`, `penpot.currentPage.root`, etc.
Return a value from the JS via `return {...}` — it is serialized back.

Known API quirks (learned the hard way, 2026-09-01):
- fontWeight only accepts 200/300/400/600/700/900 — 800 silently fails.
- growType 'auto-height' does NOT grow a created text; resize(w, h) explicitly.
- EB Garamond is the available serif; Georgia is NOT in Penpot's font list.
- text.width reads as ~1px right after createText with auto-width; set x/y and
  re-read in a SECOND call to get real width (reflow happens asynchronously).
- The cloudflare block only bites the default urllib UA — use the Mozilla header.
- export returns base64 PNG inside the SSE result (type "image").
"""
import base64
import json
import re
import sys
import urllib.error
import urllib.request
import yaml

TOKEN_SOURCE = "~/.hermes/config.yaml -> mcp_servers.penpot.url (userToken=...)"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"


def get_url():
    with open("/home/bayarddevries/.hermes/config.yaml") as f:
        cfg = yaml.safe_load(f)
    url = cfg.get("mcp_servers", {}).get("penpot", {}).get("url", "")
    if not url:
        raise SystemExit("penpot MCP not found in config.yaml")
    return url


class PenpotMCP:
    def __init__(self, url):
        self.url = url
        self.session = None
        self._handshake()

    def _post(self, payload):
        req = urllib.request.Request(
            self.url, data=json.dumps(payload).encode(), method="POST"
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json, text/event-stream")
        req.add_header("User-Agent", UA)
        if self.session:
            req.add_header("Mcp-Session-Id", self.session)
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                body = r.read().decode()
                sid = r.headers.get("mcp-session-id")
                if sid:
                    self.session = sid
                return body
        except urllib.error.HTTPError as e:
            raise SystemExit(f"HTTP {e.code}: {e.read().decode()[:400]}")

    def _handshake(self):
        self._post(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "hermes-penpot", "version": "1.0"},
                },
            }
        )
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

    @staticmethod
    def _parse_sse(resp):
        data = None
        for line in resp.splitlines():
            if line.startswith("data:"):
                try:
                    data = json.loads(line[5:].strip())
                except Exception:
                    continue
        return data or {}

    def exec_code(self, code, timeout_note=""):
        resp = self._post(
            {
                "jsonrpc": "2.0",
                "id": 9,
                "method": "tools/call",
                "params": {"name": "execute_code", "arguments": {"code": code}},
            }
        )
        data = self._parse_sse(resp)
        content = data.get("result", {}).get("content", [])
        for c in content:
            if c.get("type") == "text":
                # strip outer JSON string wrapper if the plugin returned a string
                txt = c.get("text", "")
                try:
                    return json.loads(txt)
                except Exception:
                    return txt
        return data

    def export_png(self, shape_id):
        resp = self._post(
            {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {"name": "export_shape", "arguments": {"shapeId": shape_id, "format": "png"}},
            }
        )
        data = self._parse_sse(resp)
        for c in data.get("result", {}).get("content", []):
            if c.get("type") == "image":
                return base64.b64decode(c["data"])
        raise SystemExit("no image in export response: " + resp[:300])


FIND_TIMELINE = r"""
const page = penpot.currentPage;
const root = page.root;
let timeline = null;
for (const b of root.children) {
  if (b.type === 'board' && b.children) {
    const hasSpine = b.children.some(c => c.type === 'rectangle' && c.width < 60 && c.height > 500);
    const hasComponents = b.children.filter(c => c.type === 'board' && c.name.includes('Component')).length >= 5;
    if (hasSpine && hasComponents) { timeline = b; break; }
  }
}
if (!timeline) return { error: 'timeline board not found' };
return { timelineId: timeline.id, name: timeline.name };
"""


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    mcp = PenpotMCP(get_url())
    cmd = sys.argv[1]
    if cmd == "exec":
        code = sys.argv[2]
        result = mcp.exec_code(code)
        print(json.dumps(result, indent=2, ensure_ascii=False) if not isinstance(result, str) else result)
    elif cmd == "export":
        shape_id, out = sys.argv[2], sys.argv[3]
        png = mcp.export_png(shape_id)
        with open(out, "wb") as f:
            f.write(png)
        print(f"saved {len(png)} bytes -> {out}")
    elif cmd == "shapes":
        code = r"""
const page = penpot.currentPage;
const root = page.root;
return root.children.map(c => ({ type: c.type, name: c.name, id: c.id, w: Math.round(c.width), h: Math.round(c.height) }));
"""
        result = mcp.exec_code(code)
        print(json.dumps(result, indent=2, ensure_ascii=False) if not isinstance(result, str) else result)
    elif cmd == "timeline":
        result = mcp.exec_code(FIND_TIMELINE)
        print(json.dumps(result, indent=2, ensure_ascii=False) if not isinstance(result, str) else result)
    else:
        print(f"unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
