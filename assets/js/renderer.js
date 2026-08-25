/* Ste. Madeleine Quilt — Shared renderer
   The SINGLE renderer used by BOTH the viewer (endless scroll) and the editor
   (composition studio). If it looks right in one, it looks right in the other.

   Exposes window.QuiltRenderer.render(sectionEl, section, opts)
*/
(function () {
  'use strict';

  function makeEl(tag, cls, attrs) {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    if (attrs) Object.keys(attrs).forEach((k) => el.setAttribute(k, attrs[k]));
    return el;
  }

  function videoThumb(path) {
    // Best-effort poster: look for a same-basename .jpg next to the video.
    const base = path.replace(/\.[^.]+$/, '');
    return base + '.jpg';
  }

  /* Render one tile into a positioned, absolutely-located element.
     The tile's box: x, y, w, h (px) inside the section. */
  function renderTile(tile) {
    const t = makeEl('div', 'q-tile type-' + tile.type);
    t.dataset.id = tile.id;
    t.style.transform = tile.rotate ? 'rotate(' + tile.rotate + 'deg)' : '';
    t.style.zIndex = tile.z != null ? tile.z : 1;
    t.style.left = (tile.x || 0) + 'px';
    t.style.top = (tile.y || 0) + 'px';
    t.style.width = (tile.w || 200) + 'px';
    t.style.height = (tile.h || 200) + 'px';

    if (tile.rx) t.style.borderRadius = tile.rx + 'px';

    // Background (land/texture as spacing tile)
    if (tile.background) {
      t.style.backgroundImage = "url('" + tile.background + "')";
      t.style.backgroundSize = 'cover';
      t.style.backgroundPosition = 'center';
    }

    const fit = tile.objectFit || 'cover';
    const inner = makeEl('div', 'q-inner');
    inner.style.objectFit = fit;

    const src = tile.src;
    const isGlb = src && /\.glb$/i.test(src);

    if (tile.type === 'video') {
      const vid = makeEl('video', 'q-media q-video');
      vid.src = src;
      vid.muted = true;
      vid.loop = true;
      vid.playsInline = true;
      vid.preload = 'metadata';
      if (tile.poster) vid.poster = tile.poster;
      else if (tile.posterFallback !== false) vid.poster = videoThumb(src);
      inner.appendChild(vid);
      if (tile.autoPlay) vid.play().catch(() => {});
    } else if (tile.type === 'audio') {
      const cover = makeEl('div', 'q-audio-cover');
      if (tile.cover) cover.style.backgroundImage = "url('" + tile.cover + "')";
      const btn = makeEl('div', 'q-audio-play', { 'data-audio': src });
      btn.textContent = '\u25B6';
      cover.appendChild(btn);
      inner.appendChild(cover);
    } else if (tile.type === 'scan' || isGlb) {
      const poster = makeEl('div', 'q-scan');
      if (tile.poster) poster.style.backgroundImage = "url('" + tile.poster + "')";
      const tag = makeEl('div', 'q-scan-tag');
      tag.textContent = '\u{1F4F7} 3D';
      poster.appendChild(tag);
      inner.appendChild(poster);
      inner.dataset.scanSrc = src;
    } else if (tile.type === 'text') {
      inner.textContent = tile.text || '';
      inner.className += ' q-text';
      if (tile.fontSize) inner.style.fontSize = tile.fontSize + 'px';
      if (tile.align) inner.style.textAlign = tile.align;
      if (tile.color) inner.style.color = tile.color;
    } else {
      // photo / land / texture — all plain images
      const img = makeEl('img', 'q-media', { src: src, alt: tile.caption || tile.title || '', loading: 'lazy' });
      inner.appendChild(img);
    }

    t.appendChild(inner);

    if (tile.caption) {
      const cap = makeEl('div', 'q-caption');
      cap.textContent = tile.caption;
      t.appendChild(cap);
    }

    return t;
  }

  /* Render a full section (a chapter) into a container.
     section.height sets the scroll block height. */
  function renderSection(container, section) {
    const wrap = makeEl('section', 'q-section chapter-' + (section.chapter || 0));
    wrap.id = 'sec-' + section.id;
    wrap.style.height = (section.height || 1200) + 'px';

    if (section.background) {
      wrap.style.backgroundImage = "url('" + section.background + "')";
      wrap.classList.add('has-bg');
    }

    if (section.title) {
      const header = makeEl('div', 'q-chapter-title');
      header.textContent = section.title;
      if (section.chapter) header.innerHTML = '<span class="q-chapter-num">' + section.chapter + '</span>' + header.textContent;
      wrap.appendChild(header);
    }

    const inner = makeEl('div', 'q-inner-canvas');
    (section.tiles || []).forEach((tile) => inner.appendChild(renderTile(tile)));
    wrap.appendChild(inner);

    container.appendChild(wrap);
  }

  window.QuiltRenderer = { renderSection, renderTile };
})();
