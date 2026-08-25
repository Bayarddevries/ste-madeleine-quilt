/* Ste. Madeleine Quilt — Editor (composition studio)
   Drag / resize / rotate / layer / round / fit. Renders via the SAME renderer
   as the viewer, so WYSIWYG is guaranteed. Writes layout.json.
*/
(function () {
  'use strict';

  // ---- State ----
  const state = {
    layout: { sections: [] },
    currentIdx: 0,
    selectedId: null,
    dirty: false,
    allMedia: []       // full tile list for the media drawer (from quilt-tiles.json)
  };

  // ---- DOM refs ----
  const stage = document.getElementById('stage');
  const stageWrap = document.getElementById('stage-wrap');
  const sectionNav = document.getElementById('section-nav');
  const inspectorBody = document.getElementById('inspector-body');
  const saveState = document.getElementById('save-state');
  const mediaDrawer = document.getElementById('media-drawer');
  const drawerGrid = document.getElementById('drawer-grid');
  const stageBgLabel = document.getElementById('stage-bg-label');

  const currentSection = () => state.layout.sections[state.currentIdx];
  const tileById = (id) => (currentSection()?.tiles || []).find(t => t.id === id);

  function setDirty(d) {
    state.dirty = d;
    saveState.textContent = d ? 'unsaved changes' : 'saved';
    saveState.className = 'badge' + (d ? ' dirty' : '');
  }

  function selEl() {
    const el = document.querySelector('#stage .q-tile.selected');
    return el && el.dataset.id === state.selectedId ? el : null;
  }

  // ---- Render current section (via shared renderer) ----
  function renderCurrentSection() {
    const section = currentSection();
    stageWrap.scrollTop = 0;
    stage.innerHTML = '';
    if (!section) {
      stageBgLabel.style.display = 'flex';
      stage.style.height = '600px';
      renderSectionNav();
      inspectorBody.innerHTML = '<p class="muted">No sections yet. Add one below.</p>';
      return;
    }
    stageBgLabel.style.display = 'none';
    stage.style.height = section.height + 'px';
    stage.style.backgroundImage = section.background ? "url('" + section.background + "')" : '';
    stage.style.backgroundSize = 'cover';
    stage.style.backgroundPosition = 'center';
    // clear any leftover bg label / reuse renderer
    window.QuiltRenderer.renderSection(stage, section);
    // make tiles selectable
    stage.querySelectorAll('.q-tile').forEach((el) => {
      el.dataset.id = el.dataset.id || '';
    });
    renderSectionNav();
    if (state.selectedId) selectTile(state.selectedId, false);
  }

  function renderSectionNav() {
    sectionNav.innerHTML = '';
    state.layout.sections.forEach((s, i) => {
      const b = document.createElement('button');
      b.textContent = s.chapter + '. ' + s.title;
      b.title = 'Section ' + (i + 1) + ': ' + s.title;
      if (i === state.currentIdx) b.className = 'active';
      b.onclick = () => { state.currentIdx = i; state.selectedId = null; renderCurrentSection(); };
      sectionNav.appendChild(b);
    });
  }

  // ---- Selection + handles ----
  function selectTile(id, updateInspector) {
    if (updateInspector !== false) updateInspector = true;
    state.selectedId = id;
    stage.querySelectorAll('.q-tile').forEach((el) => {
      el.classList.toggle('selected', el.dataset.id === id);
    });
    clearHandles();
    const el = selEl();
    if (!el) { if (updateInspector) showInspectorEmpty(); return; }
    addHandles(el);
    if (updateInspector) renderInspector(tileById(id));
  }

  function clearHandles() {
    stage.querySelectorAll('.q-handle').forEach(h => h.remove());
  }

  function addHandles(el) {
    const types = [
      'tl','tr','bl','br',     // corners (resize both axes)
      'n','e','s','w',         // edges (resize one axis)
      'rotate'
    ];
    types.forEach((k) => {
      const h = document.createElement('div');
      h.className = 'q-handle ' + (k === 'rotate' ? 'rotate' : (['tl','tr','bl','br'].includes(k) ? 'corner' : 'edge') + ' ' + k);
      h.dataset.action = k;
      el.appendChild(h);
    });
  }

  function showInspectorEmpty() {
    inspectorBody.innerHTML = '<p class="muted">Select a tile to edit its position, size, shape, rotation, and layering.</p>';
  }

  // ---- Inspector ----
  function renderInspector(tile) {
    if (!tile) { showInspectorEmpty(); return; }
    const num = (v) => '<input type="number" value="' + (v ?? 0) + '" data-k="' + '">';
    const typeLabel = { photo:'Photo', land:'Land', texture:'Texture', video:'Video', audio:'Audio', scan:'3D Scan', text:'Text' }[tile.type] || tile.type;
    inspectorBody.innerHTML =
      '<div class="field"><label>Tile</label><div class="muted">' + (tile.title || tile.id) + ' · ' + typeLabel + '</div></div>' +
      '<div class="row">' +
        '<div class="field"><label>X</label><input type="number" value="' + Math.round(tile.x||0) + '" data-k="x"></div>' +
        '<div class="field"><label>Y</label><input type="number" value="' + Math.round(tile.y||0) + '" data-k="y"></div>' +
      '</div>' +
      '<div class="row">' +
        '<div class="field"><label>Width</label><input type="number" value="' + Math.round(tile.w||200) + '" data-k="w"></div>' +
        '<div class="field"><label>Height</label><input type="number" value="' + Math.round(tile.h||200) + '" data-k="h"></div>' +
      '</div>' +
      '<div class="row">' +
        '<div class="field"><label>Rotation°</label><input type="number" value="' + (tile.rotate||0) + '" data-k="rotate"></div>' +
        '<div class="field"><label>Radius</label><input type="number" value="' + (tile.rx||0) + '" data-k="rx"></div>' +
      '</div>' +
      '<div class="field"><label>Object fit</label><select data-k="objectFit">' +
        '<option value="cover"' + (tile.objectFit!=='contain'?' selected':'') + '>Cover (fill, crop)</option>' +
        '<option value="contain"' + (tile.objectFit==='contain'?' selected':'') + '>Contain (whole)</option>' +
      '</select></div>' +
      '<div class="field"><label>Caption</label><input type="text" value="' + (tile.caption||'') + '" data-k="caption"></div>' +
      '<hr>' +
      '<div class="row">' +
        '<div class="field"><button class="tool" data-act="front">Bring to front</button></div>' +
        '<div class="field"><button class="tool" data-act="back">Send to back</button></div>' +
      '</div>' +
      '<div class="field"><button class="tool" data-act="up">Raise one layer ▲</button></div>' +
      '<div class="field"><button class="tool" data-act="down">Lower one layer ▼</button></div>' +
      '<div class="field"><button class="tool" data-act="duplicate">Duplicate</button></div>' +
      '<div class="field"><button class="tool danger" data-act="delete">Delete tile</button></div>';

    inspectorBody.querySelectorAll('[data-k]').forEach((input) => {
      input.addEventListener('change', () => {
        const k = input.dataset.k;
        let v = input.value;
        if (['x','y','w','h','rotate','rx'].includes(k)) v = parseFloat(v) || 0;
        tile[k] = v;
        applyTileToDom(tile);
        setDirty(true);
      });
    });
    inspectorBody.querySelectorAll('[data-act]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const act = btn.dataset.act;
        if (act === 'delete') deleteTile(tile.id);
        else if (act === 'duplicate') duplicateTile(tile.id);
        else reorderTile(tile.id, act);
      });
    });
  }

  // ---- Apply tile props to its DOM element (live update) ----
  function applyTileToDom(tile) {
    const el = stage.querySelector('.q-tile[data-id="' + CSS.escape(tile.id) + '"]');
    if (!el) return;
    el.style.left = tile.x + 'px';
    el.style.top = tile.y + 'px';
    el.style.width = tile.w + 'px';
    el.style.height = tile.h + 'px';
    el.style.transform = tile.rotate ? 'rotate(' + tile.rotate + 'deg)' : '';
    el.style.zIndex = tile.z || 1;
    el.style.borderRadius = tile.rx ? tile.rx + 'px' : '';
    const inner = el.querySelector('.q-inner');
    if (inner && tile.objectFit) inner.style.objectFit = tile.objectFit;
    const cap = el.querySelector('.q-caption');
    if (cap) cap.textContent = tile.caption || '';
  }

  // ---- Tile actions ----
  function deleteTile(id) {
    const section = currentSection();
    section.tiles = section.tiles.filter(t => t.id !== id);
    state.selectedId = null;
    renderCurrentSection();
    setDirty(true);
  }

  function duplicateTile(id) {
    const section = currentSection();
    const src = tileById(id);
    if (!src) return;
    const copy = JSON.parse(JSON.stringify(src));
    copy.id = src.id + '-copy-' + Math.floor(Math.random() * 1000);
    copy.x = (src.x || 0) + 24;
    copy.y = (src.y || 0) + 24;
    section.tiles.push(copy);
    renderCurrentSection();
    selectTile(copy.id, true);
    setDirty(true);
  }

  function reorderTile(id, act) {
    const section = currentSection();
    const t = tileById(id);
    if (!t) return;
    const zs = section.tiles.map(x => x.z != null ? x.z : 1);
    let z = t.z != null ? t.z : 1;
    if (act === 'front') z = Math.max(...zs, 1) + 1;
    else if (act === 'back') z = Math.min(...zs, 1) - 1;
    else if (act === 'up') z = z + 1;
    else if (act === 'down') z = z - 1;
    t.z = z;
    applyTileToDom(t);
    renderInspector(t);
    setDirty(true);
  }

  // ---- Drag interaction (move + resize + rotate) ----
  let drag = null;

  function onPointerDown(e, tileEl, action) {
    if (e.button !== 0) return;
    e.preventDefault();
    e.stopPropagation();
    const tile = tileById(tileEl.dataset.id);
    if (!tile) return;
    const rect = stage.getBoundingClientRect();
    const sx = e.clientX - rect.left + stageWrap.scrollLeft;
    const sy = e.clientY - rect.top + stageWrap.scrollTop;
    drag = { action, tile, sx, sy, ox: tile.x || 0, oy: tile.y || 0, ow: tile.w, oh: tile.h, oang: tile.rotate || 0, moved: false };
    if (action === 'move') selectTile(tile.id, true);
    window.addEventListener('pointermove', onPointerMove);
    window.addEventListener('pointerup', onPointerUp);
  }

  function onPointerMove(e) {
    if (!drag) return;
    const rect = stage.getBoundingClientRect();
    const x = e.clientX - rect.left + stageWrap.scrollLeft;
    const y = e.clientY - rect.top + stageWrap.scrollTop;
    const dx = x - drag.sx, dy = y - drag.sy;
    if (!drag.moved && (Math.abs(dx) + Math.abs(dy)) < 3) return;
    drag.moved = true;
    const t = drag.tile;
    if (drag.action === 'move') {
      t.x = Math.round(drag.ox + dx);
      t.y = Math.round(drag.oy + dy);
    } else if (drag.action === 'rotate') {
      const cx = drag.ox + drag.ow / 2, cy = drag.oy + drag.oh / 2;
      t.rotate = Math.round(drag.oang + ((Math.atan2(y - cy, x - cx) * 180 / Math.PI) - (drag.oang || 0)));
    } else {
      // resize by handle
      let nx = drag.ox, ny = drag.oy, nw = drag.ow, nh = drag.oh;
      if (drag.action.includes('e')) nw = Math.max(24, drag.ow + dx);
      if (drag.action.includes('s')) nh = Math.max(24, drag.oh + dy);
      if (drag.action.includes('w')) { nw = Math.max(24, drag.ow - dx); nx = drag.ox + (drag.ow - nw); }
      if (drag.action.includes('n')) { nh = Math.max(24, drag.oh - dy); ny = drag.oy + (drag.oh - nh); }
      t.x = Math.round(nx); t.y = Math.round(ny); t.w = Math.round(nw); t.h = Math.round(nh);
    }
    applyTileToDom(t);
  }

  function onPointerUp() {
    if (!drag) return;
    if (drag.moved) {
      renderInspector(drag.tile);
      setDirty(true);
    }
    drag = null;
    window.removeEventListener('pointermove', onPointerMove);
    window.removeEventListener('pointerup', onPointerUp);
  }

  // ---- Event wiring ----
  function wireStage() {
    // tile move / select
    stage.addEventListener('pointerdown', (e) => {
      const tileEl = e.target.closest('.q-tile');
      if (tileEl) {
        // handle drag (if a handle started it, don't move the tile)
        const handle = e.target.closest('.q-handle');
        if (handle) return; // handles have their own listeners
        onPointerDown(e, tileEl, 'move');
        return;
      }
      // clicked empty stage → deselect
      if (e.target === stage || e.target.closest('#stage-bg-label')) {
        state.selectedId = null;
        clearHandles();
        showInspectorEmpty();
      }
    });

    // handle drags (delegated)
    stage.addEventListener('pointerdown', (e) => {
      const handle = e.target.closest('.q-handle');
      if (!handle) return;
      const tileEl = handle.closest('.q-tile');
      if (!tileEl) return;
      onPointerDown(e, tileEl, handle.dataset.action);
    });
  }

  function bindToolbar() {
    document.getElementById('add-media-btn').addEventListener('click', () => {
      mediaDrawer.classList.toggle('open');
      if (mediaDrawer.classList.contains('open') && !drawerGrid.children.length) buildMediaDrawer();
    });
    document.getElementById('drawer-close').addEventListener('click', () => mediaDrawer.classList.remove('open'));
    document.getElementById('reseed-btn').addEventListener('click', () => {
      alert('AI seed: use scripts/seed_layout.py then reload. (In-browser seeding coming next.)');
    });
    document.getElementById('save-btn').addEventListener('click', saveLayout);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Delete' && state.selectedId) { deleteTile(state.selectedId); }
    });
  }

  // ---- Media drawer ----
  function buildMediaDrawer() {
    drawerGrid.innerHTML = '';
    state.allMedia.forEach((m) => {
      const isImg = m.type === 'photo' || m.type === 'land' || m.type === 'texture';
      const item = document.createElement('div');
      item.className = 'm-item ' + m.type;
      if (isImg) {
        const img = document.createElement('img');
        img.loading = 'lazy';
        img.src = m.src;
        img.alt = m.title || m.id;
        item.appendChild(img);
      } else {
        const badge = document.createElement('div');
        badge.className = 'm-badge';
        badge.textContent = m.type === 'video' ? '▶' : m.type === 'audio' ? '♪' : '3D';
        item.appendChild(badge);
      }
      const label = document.createElement('div');
      label.className = 'm-label';
      label.textContent = m.title || m.id;
      item.appendChild(label);
      item.title = m.title || m.id;
      item.addEventListener('click', () => addTileToSection(m));
      drawerGrid.appendChild(item);
    });
  }

  function addTileToSection(m) {
    const section = currentSection();
    if (!section) return;
    const id = m.id + '-t' + Date.now();
    const tile = {
      id, type: m.type, src: m.src,
      title: m.title, caption: m.caption || m.title || '',
      x: 120 + Math.random() * 200, y: 120 + Math.random() * 200,
      w: 240, h: 240, z: 1, objectFit: 'cover'
    };
    section.tiles.push(tile);
    renderCurrentSection();
    selectTile(id, true);
    setDirty(true);
  }

  // ---- Save / load ----
  async function saveLayout() {
    // normalize z-ints, round floats
    state.layout.sections.forEach(s => s.tiles.forEach(t => {
      t.x = Math.round(t.x||0); t.y = Math.round(t.y||0);
      t.w = Math.round(t.w||200); t.h = Math.round(t.h||200);
      if (t.rotate) t.rotate = Math.round(t.rotate);
    }));
    try {
      const res = await fetch('save-layout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(state.layout)
      });
      if (res.ok) { setDirty(false); saveState.textContent = 'saved ✓'; }
      else { saveState.textContent = 'save failed (' + res.status + ')'; saveState.className = 'badge dirty'; }
    } catch (err) {
      saveState.textContent = 'save failed: ' + err.message;
      saveState.className = 'badge dirty';
    }
  }

  async function loadLayout() {
    const res = await fetch('layout.json');
    state.layout = await res.json();
  }

  async function loadMedia() {
    const res = await fetch('quilt-tiles.json');
    const raw = await res.json();
    // normalize types: keep glb as scan
    state.allMedia = raw.map((m) => {
      const src = m.src || '';
      let type = m.type || 'photo';
      if (/\.glb$/i.test(src)) type = 'scan';
      if (/\.(mp4|mov|webm)$/i.test(src)) type = 'video';
      if (/\.(m4a|mp3|wav|ogg)$/i.test(src)) type = 'audio';
      return { ...m, type };
    });
  }

  async function init() {
    await loadLayout();
    await loadMedia();
    renderCurrentSection();
    wireStage();
    bindToolbar();
    setDirty(false);
    if (currentSection()) selectTile(currentSection().tiles[0]?.id, true);
  }

  init().catch((err) => {
    inspectorBody.innerHTML = '<p class="muted">Init error: ' + err.message + '</p>';
  });
})();






