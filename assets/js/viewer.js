/* Ste. Madeleine Quilt — Viewer (endless scroll)
   Loads layout.json, renders every section in order via the shared renderer.
   Wires lightbox (photo), inline 3D (scan), and the shared audio player.
*/
(function () {
  'use strict';

  const scroll = document.getElementById('scroll');
  const player = document.getElementById('q-audio-player');
  const audioEl = player.querySelector('audio');
  const labelEl = player.querySelector('.q-audio-label');

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
      mv.setAttribute('alt', node.dataset.caption || '3D scan');
      lb.appendChild(mv);
    } else if (node.dataset.type === 'video') {
      const v = document.createElement('video');
      v.src = src;
      v.controls = true;
      v.autoplay = true;
      lb.appendChild(v);
    } else {
      const img = document.createElement('img');
      img.src = src;
      lb.appendChild(img);
    }

    const cap = node.dataset.caption;
    if (cap) {
      const c = document.createElement('div');
      c.className = 'q-lb-caption';
      c.textContent = cap;
      lb.appendChild(c);
    }

    lb.appendChild(close);
    lb.onclick = (e) => { if (e.target === lb) lb.remove(); };
    document.body.appendChild(lb);
  }

  function playAudio(src, label) {
    audioEl.src = src;
    labelEl.textContent = label || '';
    player.classList.add('active');
    audioEl.play().catch(() => {});
  }

  function bindEvents() {
    // Delegated clicks on tiles
    scroll.addEventListener('click', (e) => {
      const tile = e.target.closest('.q-tile');
      if (!tile) return;
      const inner = tile.querySelector('.q-inner');

      // audio play button
      const playBtn = e.target.closest('.q-audio-play');
      if (playBtn && playBtn.dataset.audio) {
        const src = playBtn.dataset.audio;
        const cap = tile.dataset.caption || '';
        if (audioEl.src && audioEl.src.endsWith(encodeURI(src))) { player.classList.remove('active'); audioEl.pause(); audioEl.src = ''; }
        else playAudio(src, cap);
        return;
      }

      // scan opens 3D
      if (inner && inner.dataset.scanSrc) {
        showLightbox({
          src: inner.dataset.scanSrc,
          type: 'scan',
          caption: tile.dataset.caption || '3D scan'
        });
        return;
      }

      // video opens lightbox player
      const vid = inner && inner.querySelector('video');
      if (vid) {
        showLightbox({ src: vid.src || vid.getAttribute('src'), type: 'video', caption: tile.dataset.caption });
        return;
      }

      // photo opens lightbox
      const img = inner && inner.querySelector('img.q-media');
      if (img) {
        showLightbox({ src: img.currentSrc || img.src, caption: tile.dataset.caption });
        return;
      }
    });

    // close lightbox on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { document.querySelector('.q-lightbox')?.remove(); }
    });
  }

  async function init() {
    const res = await fetch('layout.json');
    const data = await res.json();
    (data.sections || []).forEach((section) => {
      window.QuiltRenderer.renderSection(scroll, section);
    });
    bindEvents();
    // stamp tile captions for lightbox delegation
    scroll.querySelectorAll('.q-tile').forEach((t) => {
      if (t.dataset.caption == null) t.dataset.caption = t.querySelector('.q-caption')?.textContent || '';
    });
  }

  init().catch((err) => {
    scroll.innerHTML = '<p style="padding:60px;text-align:center;color:#b9a98a">Could not load quilt: ' + err.message + '</p>';
  });
})();
