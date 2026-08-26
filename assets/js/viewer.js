/* Ste. Madeleine Quilt — Free-pan 2D canvas viewer.
   ENDLESS horizontal wrap (torus): the quilt's content is tiled 3× side-by-side
   on a surface of width 3W (W = one copy of the content width). The horizontal
   camera (tx) is wrapped modulo W, so panning far left or right loops back
   around seamlessly — the content repeats every W so the snap lands on
   identical pixels and there is no visible seam or gap. Vertical stays finite.
   Images are lazy-mounted via IntersectionObserver: only tiles approaching the
   viewport actually load their <img src>, so the initial page doesn't fire all
   ~200 image requests at once. Pan, zoom, video autoplay (cap 2), and the lazy
   3D-scan model-viewer are all preserved. Uses the shared renderer (WYSIWYG
   with the editor).
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
  let W = 0;                   // content width of ONE copy (the wrap period)

  function setTransform() {
    surface.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')';
  }

  // Wrap the horizontal camera into [0, W). Because the content repeats every
  // W pixels, wrapping to a whole-multiple-of-W offset shows identical pixels,
  // so the loop-back is seamless (no jump, no seam).
  function wrapTx() {
    if (W <= 0) return;
    const w = ((tx % W) + W) % W;
    if (w !== tx) { tx = w; setTransform(); }
  }

  function centerView() {
    const vw = viewport.clientWidth, vh = viewport.clientHeight;
    tx = 0;   // start at the left edge; wrap handles looping thereafter
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
    wrapTx();
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
    wrapTx();
    updateVisibleVideos();
  }

  // ---- Video autoplay when scrolled into view ----
  let lastCheck = 0;
  let playingCount = 0;
  function updateVisibleVideos() {
    // throttle to ~4Hz, cap concurrent plays to 2
    const now = Date.now();
    if (now - lastCheck < 250) return;
    lastCheck = now;
    const rect = viewport.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const pad = Math.max(rect.width, rect.height);
    playingCount = 0;
    const videos = Array.from(surface.querySelectorAll('video'));
    videos.forEach((v) => { if (!v.paused) playingCount++; });
    videos.forEach((v) => {
      const r = v.getBoundingClientRect();
      const inView = r.right > rect.left - pad && r.left < rect.right + pad &&
                     r.bottom > rect.top - pad && r.top < rect.bottom + pad;
      if (inView && playingCount < 2) {
        const p = v.play();
        if (p) p.catch(() => {});
        if (!v.paused) playingCount++;
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
      if (!window.customElements.get('model-viewer')) {
        const s = document.createElement('script');
        s.type = 'module'; s.src = 'media/vendor/model-viewer.min.js';
        document.head.appendChild(s);
      }
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

  // ---- Lazy media mounting (IntersectionObserver) ----
  // For a photo tile, move the src into data-src and DON'T set img.src yet, so
  // the browser doesn't fetch it until the tile nears the viewport.
  function deferImage(tile) {
    const img = tile.querySelector('img.q-media');
    if (img && !img.dataset.src && img.getAttribute('src')) {
      img.dataset.src = img.getAttribute('src');
      img.removeAttribute('src');
    }
  }

  // Load a tile's media. Idempotent: a photo mounts only once.
  function mountTile(tile) {
    const img = tile.querySelector('img.q-media');
    if (img && img.dataset.src && !img.src) {
      img.src = img.dataset.src;
      img.style.opacity = '0';
      img.style.transition = 'opacity .35s ease';
      img.addEventListener('load', () => { img.style.opacity = '1'; });
    }
  }

  // ---- Build surface from layout (tiled 3× horizontally) ----
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
    W = maxX - minX + pad * 2;                    // one copy's width  = wrap period
    const H = maxY - minY + pad * 2;
    surface.style.width = (W * 3) + 'px';         // 3 copies side by side
    surface.style.height = H + 'px';
    surface.dataset.sw = W * 3;
    surface.dataset.sh = H;

    // Cloth backing: single repeating patchwork background (zero DOM nodes).
    surface.style.backgroundImage = "url('assets/img/backing-patchwork.jpg')";
    surface.style.backgroundRepeat = 'repeat';
    surface.style.backgroundSize = '720px 720px';

    // IntersectionObserver: mount (start loading) tiles as they approach the
    // viewport, with a generous margin so panning feels smooth. Once mounted,
    // the tile is unobserved (stays loaded if you pan away and back).
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { mountTile(en.target); io.unobserve(en.target); }
      });
    }, { root: viewport, rootMargin: '50% 50% 50% 50%', threshold: 0 });

    data.sections.forEach((s) => {
      (s.tiles || []).forEach((t) => {
        // 'texture' tiles are the backing cloth, now drawn by the surface
        // background (assets/img/backing-patchwork.jpg) — skip to keep DOM light.
        if (t.type === 'texture') return;
        const baseLeft = t.x - minX + pad;
        const baseTop = t.y - minY + pad;
        // three copies: left, centre, right — enables seamless loop
        for (let k = 0; k < 3; k++) {
          const tile = window.QuiltRenderer.renderTile(t);
          tile.style.left = (baseLeft + k * W) + 'px';
          tile.style.top = baseTop + 'px';
          // tag for lightbox
          tile.dataset.caption = t.caption || t.title || '';
          tile.dataset.src = t.src || '';
          tile.dataset.type = t.type || 'photo';
          surface.appendChild(tile);

          if (t.type === 'photo') {
            // heavy image: defer fetch until the tile nears the viewport
            deferImage(tile);
            io.observe(tile);
          } else {
            // video / audio / scan / texture / text are few and light: mount now
            mountTile(tile);
          }
        }
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
    if (e.key === 'ArrowLeft') { tx += step; setTransform(); wrapTx(); updateVisibleVideos(); }
    if (e.key === 'ArrowRight') { tx -= step; setTransform(); wrapTx(); updateVisibleVideos(); }
    if (e.key === 'ArrowUp') { ty += step; setTransform(); updateVisibleVideos(); }
    if (e.key === 'ArrowDown') { ty -= step; setTransform(); updateVisibleVideos(); }
  });

  // Escape closes lightbox
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') document.querySelector('.q-lightbox')?.remove(); });

  build().catch((err) => { loadMsg.textContent = 'Could not load quilt: ' + err.message; });
})();
