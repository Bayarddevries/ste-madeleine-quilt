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
     section.height sets the scroll block height. If designWidth is set, the
     section is scaled to fit the container width (responsive on mobile).
     On narrow screens (< reflowBreakpoint), tiles reflow into a readable
     column layout instead of being tiny scale-downs. */
  function renderSection(container, section, opts) {
    opts = opts || {};
    const designW = section.designWidth || 1200;
    const availW = (container.clientWidth) || window.innerWidth || 1200;
    const reflow = !opts.noScale && availW < (section.reflowBreakpoint ?? 700);

    if (reflow) {
      renderReflow(container, section, availW);
      return;
    }

    const scale = Math.min(1, availW / designW);

    const wrap = makeEl('div', 'q-section-scroll');
    wrap.style.width = '100%';
    wrap.style.height = Math.round((section.height || 1200) * scale) + 'px';

    const secEl = makeEl('section', 'q-section chapter-' + (section.chapter || 0));
    secEl.id = 'sec-' + section.id;
    secEl.style.width = designW + 'px';
    secEl.style.height = (section.height || 1200) + 'px';
    secEl.style.transformOrigin = 'top left';
    if (scale !== 1) secEl.style.transform = 'scale(' + scale + ')';

    if (section.background) {
      secEl.style.backgroundImage = "url('" + section.background + "')";
      secEl.classList.add('has-bg');
    }

    if (section.title) {
      const header = makeEl('div', 'q-chapter-title');
      header.textContent = section.title;
      if (section.chapter) header.innerHTML = '<span class="q-chapter-num">' + section.chapter + '</span>' + header.textContent;
      secEl.appendChild(header);
    }

    const inner = makeEl('div', 'q-inner-canvas');
    (section.tiles || []).forEach((tile) => inner.appendChild(renderTile(tile)));
    secEl.appendChild(inner);

    wrap.appendChild(secEl);
    container.appendChild(wrap);
  }

  window.QuiltRenderer = { renderSection, renderTile };

  /* Mobile reflow: a readable column layout for narrow screens.
     Reflows tiles into a centered masonry (1-2 columns) at readable sizes,
     keeping media in their z-order/reading sequence. Preserves the editor's
     authored composition only at desktop widths; this is the mobile fallback. */
  function renderReflow(container, section, availW) {
    const wrap = makeEl('div', 'q-section-scroll reflow');
    wrap.style.width = '100%';

    const body = makeEl('div', 'q-reflow-body');

    // title banner
    if (section.title) {
      const h = makeEl('div', 'q-chapter-title');
      h.textContent = section.title;
      if (section.chapter) h.innerHTML = '<span class="q-chapter-num">' + section.chapter + '</span>' + h.textContent;
      body.appendChild(h);
    }

    // 2 columns on ≥480px, 1 column below
    const cols = availW >= 480 ? 2 : 1;
    const gap = 10;
    const colW = (availW - gap * (cols - 1) - 24) / cols;

    const columns = [];
    for (let i = 0; i < cols; i++) columns.push(makeEl('div', 'q-reflow-col'));

    const tiles = (section.tiles || []).slice().sort((a, b) => (a.z || 1) - (b.z || 1));
    // Media tiles (photo/video/scan/audio) reflow; text/land tiles become subtle dividers
    const media = tiles.filter(t => ['photo','video','scan','audio'].includes(t.type));
    const accents = tiles.filter(t => ['land','texture','text'].includes(t.type));

    let col = 0;
    let ci = 0;
    media.forEach((tile) => {
      const tEl = renderTile(tile);
      tEl.classList.add('reflow-tile');
      // scale tile to fit column, keep aspect
      const ar = tile.w / (tile.h || tile.w);
      const w = Math.round(colW);
      const h = Math.round(w / Math.max(0.5, Math.min(2.5, ar)));
      tEl.style.left = '0';
      tEl.style.top = '0';
      tEl.style.width = w + 'px';
      tEl.style.height = h + 'px';
      tEl.style.position = 'relative';
      tEl.style.transform = '';
      tEl.style.zIndex = '';
      tEl.classList.add('reflow-stack');
      columns[col].appendChild(tEl);
      // weave an accent (land/text) tile between every few media as breathing room
      col = (col + 1) % cols;
      ci++;
    });

    // build body: header + columns side by side (or stacked)
    const grid = makeEl('div', 'q-reflow-grid');
    grid.style.display = 'flex';
    grid.style.gap = gap + 'px';
    grid.style.alignItems = 'flex-start';
    grid.style.justifyContent = 'center';
    grid.style.padding = '12px';
    columns.forEach((c) => {
      c.style.flex = '1';
      c.style.display = 'flex';
      c.style.flexDirection = 'column';
      c.style.gap = gap + 'px';
      grid.appendChild(c);
    });
    body.appendChild(grid);
    wrap.appendChild(body);
    container.appendChild(wrap);
  }

})();
