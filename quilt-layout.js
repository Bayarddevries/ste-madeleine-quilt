/* Ste Madeleine — Quilt Layout Designer
   Drag/drop media onto canvas, position freely, save layout
*/

// ---- Canvas setup ----
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const container = document.getElementById('canvas-container');
const scaleSlider = document.getElementById('scale-slider');

let scale = 1;
let offset = { x: 0, y: 0 };
let isDragging = false;
let dragStart = { x: 0, y: 0 };
let dragOffset = { x: 0, y: 0 };

function resizeCanvas() {
  const rect = container.getBoundingClientRect();
  canvas.width = Math.max(rect.width, 3000 * scale);
  canvas.height = Math.max(rect.height, 3000 * scale);
  // Start centered
  if (offset.x === 0 && offset.y === 0) {
    offset.x = canvas.width / 2 - 1500 * scale;
    offset.y = canvas.height / 2 - 1500 * scale;
  }
  redraw();
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// ---- Layout data ----
const layout = {
  width: 3000,
  height: 3000,
  tiles: []
};

let selectedTile = null;
let draggedFromLibrary = null;

// ---- Media library ----
let mediaFiles = {
  images: [],
  videos: [],
  gifs: [],
  audio: [],
  timeline: []
};

async function buildMediaLibrary() {
  try {
    // Load media-manifest.json for timeline images
    const manifestResp = await fetch('media/timeline/media-manifest.json');
    if (manifestResp.ok) {
      const manifest = await manifestResp.json();
      for (const stageId of Object.keys(manifest.stages)) {
        const stage = manifest.stages[stageId];
        if (stage.current_image) {
          mediaFiles.timeline.push({
            name: stage.current_image,
            path: 'media/timeline/' + stage.current_image,
            label: stage.label,
            type: 'image'
          });
        }
      }
      // Add GIFs
      mediaFiles.gifs.push({ name: 'metis-infinity-flag.gif', path: 'media/timeline/metis-infinity-flag.gif', label: 'Métis Flag (GIF)', type: 'gif' });
    }

    // Load quilt-tiles.json for weekend media
    const quiltResp = await fetch('quilt-tiles.json');
    if (quiltResp.ok) {
      const quiltTiles = await quiltResp.json();
      let imgCount = 0, vidCount = 0, audCount = 0;
      for (const t of quiltTiles) {
        if (t.src) {
          const name = t.src.split('/').pop();
          const label = t.title || name;
          if (t.type === 'photo' && name.match(/\.(jpe?g|png|webp)$/i) && imgCount < 40) {
            mediaFiles.images.push({ name, path: t.src, label, type: 'image' });
            imgCount++;
          } else if (t.type === 'video' && name.match(/\.mp4$/i) && vidCount < 12) {
            mediaFiles.videos.push({ name, path: t.src, label, type: 'video' });
            vidCount++;
          } else if (t.type === 'audio' && name.match(/\.m4a$/i) && audCount < 6) {
            mediaFiles.audio.push({ name, path: t.src, label, type: 'audio' });
            audCount++;
          }
        }
      }
    }

    renderMediaLibrary();
  } catch(e) {
    console.error('Media library load error:', e);
  }
}

function renderMediaLibrary() {
  const list = document.getElementById('media-list');
  list.innerHTML = '';
  
  function addSection(title, items, icon) {
    if (items.length === 0) return;
    const h = document.createElement('h4');
    h.textContent = `${icon} ${title} (${items.length})`;
    h.style.cssText = 'font-size:12px;color:#9a8a70;margin:12px 0 6px;text-transform:uppercase;letter-spacing:.5px';
    list.appendChild(h);
    
    items.forEach(item => {
      const thumb = document.createElement('img');
      thumb.className = 'media-thumb';
      thumb.src = item.path;
      thumb.alt = item.label;
      thumb.title = item.label;
      thumb.dataset.media = JSON.stringify(item);
      thumb.onclick = () => {
        document.querySelectorAll('.media-thumb').forEach(t => t.classList.remove('selected'));
        thumb.classList.add('selected');
        draggedFromLibrary = item;
      };
      
      if (item.type === 'video' || item.type === 'gif' || item.type === 'audio') {
        thumb.classList.add(item.type);
      }
      list.appendChild(thumb);
    });
  }
  
  addSection('Timeline Images', mediaFiles.timeline, '📷');
  addSection('GIFs', mediaFiles.gifs, '🎬');
  addSection('Weekend Photos', mediaFiles.images, '📷');
  addSection('Weekend Videos', mediaFiles.videos, '🎥');
  addSection('Audio', mediaFiles.audio, '🎵');
}

// ---- Canvas drawing ----
function redraw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // Draw grid
  ctx.strokeStyle = 'rgba(255,255,255,0.03)';
  ctx.lineWidth = 1;
  const gridSize = 50 * scale;
  for (let x = -offset.x; x < canvas.width; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();
  }
  for (let y = -offset.y; y < canvas.height; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
    ctx.stroke();
  }
  
  // Draw center origin lines
  ctx.strokeStyle = 'rgba(144, 104, 62, 0.2)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(-offset.x, 0);
  ctx.lineTo(-offset.x, canvas.height);
  ctx.moveTo(0, -offset.y);
  ctx.lineTo(canvas.width, -offset.y);
  ctx.stroke();
  
  // Draw tiles
  for (const tile of layout.tiles) {
    const tx = tile.x * scale + offset.x;
    const ty = tile.y * scale + offset.y;
    const tw = tile.w * scale;
    const th = tile.h * scale;
    
    // Tile border
    ctx.save();
    ctx.strokeStyle = selectedTile === tile ? '#c9a227' : '#4a3a26';
    ctx.lineWidth = selectedTile === tile ? 3 : 1;
    ctx.strokeRect(tx, ty, tw, th);
    
    // Draw media content
    if (tile.media) {
      const img = tile.media;
      if (img instanceof HTMLImageElement) {
        ctx.drawImage(img, tx, ty, tw, th);
      } else if (img instanceof HTMLCanvasElement) {
        ctx.drawImage(img, tx, ty, tw, th);
      }
    } else {
      // Placeholder
      ctx.fillStyle = 'rgba(31,92,91,0.3)';
      ctx.fillRect(tx, ty, tw, th);
      ctx.fillStyle = '#e8dcc0';
      ctx.font = '12px Georgia';
      ctx.textAlign = 'center';
      ctx.fillText(tile.title || 'Untitled', tx + tw/2, ty + th/2);
    }
    
    ctx.restore();
  }
}

// ---- Event handlers ----
container.addEventListener('pointerdown', e => {
  const rect = container.getBoundingClientRect();
  const cx = (e.clientX - rect.left) / scale - offset.x / scale;
  const cy = (e.clientY - rect.top) / scale - offset.y / scale;
  
  if (draggedFromLibrary && !isDragging) {
    // Drop media from library
    const item = draggedFromLibrary;
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      const size = Math.min(300, Math.max(img.width, img.height) * 0.5);
      const tile = {
        id: 't' + Date.now(),
        x: cx, y: cy,
        w: size, h: size,
        title: item.label || item.name,
        media: img,
        src: item.path,
        type: item.type
      };
      layout.tiles.push(tile);
      updateTileCount();
      redraw();
    };
    img.src = item.path;
    draggedFromLibrary = null;
    document.querySelectorAll('.media-thumb').forEach(t => t.classList.remove('selected'));
    return;
  }
  
  // Check if clicking a tile
  for (let i = layout.tiles.length - 1; i >= 0; i--) {
    const t = layout.tiles[i];
    if (cx >= t.x && cx <= t.x + t.w && cy >= t.y && cy <= t.y + t.h) {
      selectedTile = t;
      isDragging = true;
      dragStart = { x: cx, y: cy };
      dragOffset = { x: t.x - cx, y: t.y - cy };
      redraw();
      return;
    }
  }
  selectedTile = null;
  redraw();
});

container.addEventListener('pointermove', e => {
  if (!isDragging || !selectedTile) return;
  const rect = container.getBoundingClientRect();
  const cx = (e.clientX - rect.left) / scale - offset.x / scale;
  const cy = (e.clientY - rect.top) / scale - offset.y / scale;
  selectedTile.x = cx + dragOffset.x;
  selectedTile.y = cy + dragOffset.y;
  redraw();
});

container.addEventListener('pointerup', () => {
  isDragging = false;
  selectedTile = null;
});

// ---- Zoom ----
scaleSlider.addEventListener('input', e => {
  scale = parseFloat(e.target.value);
  document.getElementById('zoom-level').textContent = Math.round(scale * 100) + '%';
  redraw();
});

document.getElementById('zoom-in').addEventListener('click', () => {
  scale = Math.min(3, scale * 1.2);
  scaleSlider.value = scale;
  document.getElementById('zoom-level').textContent = Math.round(scale * 100) + '%';
  redraw();
});

document.getElementById('zoom-out').addEventListener('click', () => {
  scale = Math.max(0.3, scale / 1.2);
  scaleSlider.value = scale;
  document.getElementById('zoom-level').textContent = Math.round(scale * 100) + '%';
  redraw();
});

document.getElementById('zoom-reset').addEventListener('click', () => {
  scale = 1;
  scaleSlider.value = 1;
  document.getElementById('zoom-level').textContent = '100%';
  redraw();
});

// ---- Save / Load ----
document.getElementById('save-btn').addEventListener('click', () => {
  const out = {
    width: layout.width,
    height: layout.height,
    tiles: layout.tiles.map(t => ({
      id: t.id,
      x: Math.round(t.x),
      y: Math.round(t.y),
      w: Math.round(t.w),
      h: Math.round(t.h),
      title: t.title,
      src: t.src,
      type: t.type
    }))
  };
  const json = JSON.stringify(out, null, 1);
  const blob = new Blob([json], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'quilt-layout.json';
  a.click();
  URL.revokeObjectURL(url);
});

document.getElementById('clear-btn').addEventListener('click', () => {
  layout.tiles = [];
  selectedTile = null;
  updateTileCount();
  redraw();
});

// ---- Media panel toggle ----
document.getElementById('add-media-btn').addEventListener('click', () => {
  document.getElementById('media-panel').classList.toggle('open');
});

function updateTileCount() {
  document.getElementById('tile-count').textContent = layout.tiles.length + ' tiles';
}

// ---- Init ----
buildMediaLibrary();
