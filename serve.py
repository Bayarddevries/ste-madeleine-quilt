#!/usr/bin/env python3
"""Ste. Madeleine Quilt — local dev server.
Serves the static site AND accepts POST /save-layout to write layout.json
(so the editor can persist compositions that the viewer reads).

Usage:  python3 serve.py [port]   (default 8090, bind 0.0.0.0 for Tailscale)
"""
import http.server, functools, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
LAYOUT = os.path.join(ROOT, 'layout.json')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def do_POST(self):
        if self.path != '/save-layout':
            self.send_error(404, 'Not found')
            return
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except Exception:
            self.send_error(400, 'Invalid JSON')
            return
        # safety: keep a backup before overwriting
        if os.path.exists(LAYOUT):
            backup = LAYOUT + '.bak'
            try:
                with open(LAYOUT) as f: old = f.read()
                with open(backup, 'w') as f: f.write(old)
            except Exception:
                pass
        tmp = LAYOUT + '.tmp'
        with open(tmp, 'w') as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, LAYOUT)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode())

    def log_message(self, *a):
        pass  # quiet

if __name__ == '__main__':
    server = http.server.ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    print(f"Serving Ste. Madeleine Quilt on http://0.0.0.0:{PORT}/ (save-layout POST enabled)")
    server.serve_forever()
