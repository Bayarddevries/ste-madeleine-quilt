/* Ste. Madeleine Quilt — Free-pan 2D canvas viewer.
   The whole quilt is laid out on ONE large surface. Drag to pan in any
   direction, wheel/pinch to zoom. Videos autoplay when scrolled into view.
   Uses the shared renderer (WYSIWYG with the editor).
*/
(function () {
  'use strict';

  const viewport = document.getElementById('viewport');
  const surface = document.getElementById('surface');
  const loadMsg = document.getElementById('load-msg');

  let scale = 1;
  let tx = 0, ty = 0;          // camera translation
  let dragging = false;
  let lastX = 0, lastY = 0;
  let pinchDist = null;

  function setTransform() {
    surface.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')';
  }

  function centerView() {
    const vw = viewport.clientWidth, vh = viewport.clientHeight;
    tx = vw / 2 - (surface.dataset.sw || 1600) / 2;
    ty = vh / 2 - (surface.dataset.sh || 1200) / 2;
    setTransform();
  }

  // ---- Pan ----
  function startPan(e) {
    if (!enabled) return;
    dragging = true;
    lastX = e.clientX; lastY = e.clientY;
    viewport.classList.add('panning');
  }
  function movePan(e) {
    if (!dragging) return;
    tx += e.clientX - lastX;
    ty += e.clientY - lastY;
    lastX = e.clientX; lastY = e.clientY;
    setTransform();
  }
  function endPan() {
    dragging = false;
    viewport.classList.remove('panning');
  }

  // ---- Zoom (wheel) ----
  function onWheel(e) {
    if (!enabled) return;
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 1 / 1.1;
    zoomAt(e.clientX, e.clientY, factor);
  }

  function zoomAt(cx, cy, factor) {
    const rect = viewport.getBoundingClientRect();
    const px = (cx - rect.left - tx) / scale;
    const py = (cy - rect.top - ty) / scale;
    scale = Math.max(0.15, Math.min(4, scale * factor));
    tx = cx - rect.left - px * scale;
    ty = cy - rect.top - py * scale;
    setTransform();
    updateVisibleVideos();
  }

  // ---- Video autoplay when scrolled into view ----
  let lastCheck = 0;
  function updateVisibleVideos() {
    // throttle to ~4Hz
    const now = Date.now();
    if (now - lastCheck < 250) return;
    lastCheck = now;
    const rect = viewport.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const pad = Math.max(rect.width, rect.height);
    surface.querySelectorAll('video').forEach((v) => {
      const r = v.getBoundingClientRect();
      const inView = r.right > rect.left - pad && r.left < rect.right + pad &&
                     r.bottom > rect.top - pad && r.top < rect.bottom + pad;
      if (inView) {
        const p = v.play();
        if (p) p.catch(() => {});
      } else {
        v.pause();
      }
    });
  }

  // ---- Lightbox (photo / video / audio / scan) ----
  function showLightbox(node) {
    const existing = document.querySelector('.q-lightbox');
    if (existing) existing.remove();
    const lb = document.createElement('div');
    lb.className = 'q-lightbox';
    const close = document.createElement('button');
    close.className = 'q-lb-close';
    close.textContent = '\u00D7';
    close.setAttribute('aria-label', 'Close');
    close.onclick = () => lb.remove();
    const src = node.dataset.src || node.src;

    if (node.dataset.type === 'scan') {
      const mv = document.createElement('model-viewer');
      mv.setAttribute('src', src);
      mv.setAttribute('camera-controls', '');
      mv.setAttribute('auto-rotate', '');
      mv.setAttribute('ar', '');
      lb.appendChild(mv);
    } else if (node.dataset.type === 'video') {
      const v = document.createElement('video');
      v.src = src; v.controls = true; v.autoplay = true;
      lb.appendChild(v);
    } else if (node.dataset.type === 'audio') {
      const a = document.createElement('audio');
      a.src = src; a.controls = true; a.autoplay = true;
      lb.appendChild(a);
    } else {
      const img = document.createElement('img');
      img.src = src; lb.appendChild(img);
    }
    const cap = node.dataset.caption;
    if (cap) { const c = document.createElement('div'); c.className = 'q-lb-caption'; c.textContent = cap; lb.appendChild(c); }
    lb.appendChild(close);
    lb.onclick = (e) => { if (e.target === lb) lb.remove(); };
    document.body.appendChild(lb);
  }

  // ---- Build surface from layout ----
  async function build() {
    const res = await fetch('layout.json');
    const data = await res.json();
    // Compute bounding box of all tiles across all sections
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    data.sections.forEach((s) => {
      (s.tiles || []).forEach((t) => {
        minX = Math.min(minX, t.x); minY = Math.min(minY, t.y);
        maxX = Math.max(maxX, t.x + t.w); maxY = Math.max(maxY, t.y + t.h);
      });
    });
    if (!isFinite(minX)) { minX = 0; minY = 0; maxX = 1600; maxY = 1200; }
    const pad = 200;
    surface.style.width = (maxX - minX + pad * 2) + 'px';
    surface.style.height = (maxY - minY + pad * 2) + 'px';
    surface.dataset.sw = maxX - minX + pad * 2;
    surface.dataset.sh = maxY - minY + pad * 2;

    // Place each section's tiles translated so bbox starts at pad
    data.sections.forEach((s) => {
      (s.tiles || []).forEach((t) => {
        const tile = window.QuiltRenderer.renderTile(t);
        tile.style.left = (t.x - minX + pad) + 'px';
        tile.style.top = (t.y - minY + pad) + 'px';
        // tag for lightbox
        tile.dataset.caption = t.caption || t.title || '';
        tile.dataset.src = t.src || '';
        tile.dataset.type = t.type || 'photo';
        surface.appendChild(tile);
      });
    });

    // Wire clicks
    surface.addEventListener('click', (e) => {
      const tile = e.target.closest('.q-tile');
      if (!tile) return;
      const type = tile.dataset.type;
      if (type === 'scan' || type === 'video' || type === 'audio' || type === 'photo') {
        showLightbox(tile);
      }
    });

    loadMsg.style.display = 'none';
    centerView();
    setTransform();
    updateVisibleVideos();
  }

  // ---- Wire viewport events ----
  const intro = document.getElementById('intro');
  let enabled = false;
  function enable() {
    enabled = true;
    intro.classList.add('hidden');
    centerView();
    updateVisibleVideos();
  }
  document.getElementById('enter-btn')?.addEventListener('click', enable);

  // gate pan/zoom until entered
  viewport.addEventListener('pointerdown', startPan);
  viewport.addEventListener('pointermove', movePan);
  window.addEventListener('pointerup', endPan);
  window.addEventListener('pointercancel', endPan);
  viewport.addEventListener('wheel', onWheel, { passive: false });

  // touch pinch zoom
  let pointers = new Map();
  viewport.addEventListener('pointerdown', (e) => {
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size === 2) {
      const [a, b] = [...pointers.values()];
      pinchDist = Math.hypot(a.x - b.x, a.y - b.y);
    }
  });
  viewport.addEventListener('pointermove', (e) => {
    if (pointers.has(e.pointerId)) {
      pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (pointers.size === 2) {
        const [a, b] = [...pointers.values()];
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        if (pinchDist) {
          const midX = (a.x + b.x) / 2, midY = (a.y + b.y) / 2;
          zoomAt(midX, midY, d / pinchDist);
        }
        pinchDist = d;
      }
    }
  });
  viewport.addEventListener('pointerup', (e) => {
    pointers.delete(e.pointerId);
    if (pointers.size < 2) pinchDist = null;
  });

  // keyboard arrows to nudge
  window.addEventListener('keydown', (e) => {
    const step = 60;
    if (e.key === 'ArrowLeft') { tx += step; setTransform(); updateVisibleVideos(); }
    if (e.key === 'ArrowRight') { tx -= step; setTransform(); updateVisibleVideos(); }
    if (e.key === 'ArrowUp') { ty += step; setTransform(); updateVisibleVideos(); }
    if (e.key === 'ArrowDown') { ty -= step; setTransform(); updateVisibleVideos(); }
  });

  // Escape closes lightbox
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') document.querySelector('.q-lightbox')?.remove(); });

  build().catch((err) => { loadMsg.textContent = 'Could not load quilt: ' + err.message; });
})();
