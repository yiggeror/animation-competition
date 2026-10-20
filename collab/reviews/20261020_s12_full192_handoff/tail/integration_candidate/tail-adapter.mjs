/** Candidate only. No production entrypoint changes. Scene-space layers are 1920x1080. */
export function createTailSelector(manifest) {
  if (manifest.shot !== 'S12' || manifest.fps !== 24 || manifest.frame_count !== 192 || manifest.duration_seconds !== 8) throw new Error('S12 timing contract mismatch');
  const slots = new Array(192).fill(null);
  for (const entry of manifest.timeline) {
    const [first, last] = entry.frames ?? [];
    if (!Number.isInteger(first) || !Number.isInteger(last) || first < 106 || last > 191 || first > last || !/^F\d{3}$/.test(entry.folder)) throw new Error('Invalid tail exposure');
    for (let f = first; f <= last; f++) {
      if (slots[f]) throw new Error(`Overlapping exposure at ${f}`);
      slots[f] = Object.freeze({folder: entry.folder, drawing: entry.drawing});
    }
  }
  for (let f = 106; f < 192; f++) if (!slots[f]) throw new Error(`Missing exposure at ${f}`);
  return (shot, frame) => {
    if (shot !== 'S12') return null;
    if (!Number.isInteger(frame)) throw new Error('Expected integer shot-local frame; no time rounding');
    return frame >= 106 && frame < 192 ? slots[frame] : null;
  };
}

/** Inject the application's existing image loader. Rejected/missing/wrong-size assets fail loudly. */
export async function loadTailLayers(manifest, loadImage, base = '..') {
  createTailSelector(manifest);
  const assets = new Map();
  for (const folder of new Set(manifest.timeline.map(e => e.folder))) {
    const pair = {};
    for (const side of ['BG', 'FG']) {
      const path = `${base.replace(/\/$/, '')}/${folder}/scene_${side}.png`;
      let img;
      try { img = await loadImage(path); } catch (cause) { throw new Error(`Cannot load tail image: ${path}`, {cause}); }
      if (!img || (img.naturalWidth ?? img.width) !== 1920 || (img.naturalHeight ?? img.height) !== 1080) throw new Error(`Missing or invalid 1920x1080 tail image: ${path}`);
      pair[side] = img;
    }
    assets.set(folder, Object.freeze(pair));
  }
  return assets;
}

/** Returns false without touching context/callbacks outside the tail. Caller then runs old renderer.
 * At the old character/prop insertion point, draw background and shadows first, call this,
 * then retain the caller's existing box-front/foreground passes. drawOriginalProps must use
 * the corresponding unchanged physical prop plan, original texture and optical renderer.
 */
export function drawTail({shot, frame, ctx, select, assets, drawOriginalProps}) {
  const selected = select(shot, frame);
  if (!selected) return false;
  const pair = assets.get(selected.folder);
  if (!pair?.BG || !pair?.FG) throw new Error(`Tail layers not loaded: ${selected.folder}`);
  if (typeof drawOriginalProps !== 'function') throw new Error('Original prop renderer callback required');
  const drawScene = image => {
    ctx.save();
    try {
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = 'source-over';
      ctx.drawImage(image, 0, 0); // Already registered. Never rescale/reposition.
    } finally { ctx.restore(); }
  };
  drawScene(pair.BG);
  const propResult = drawOriginalProps({frame, folder: selected.folder});
  if (propResult != null && typeof propResult.then === 'function') {
    throw new TypeError('Original prop renderer must be synchronous; thenable returned, foreground not drawn');
  }
  drawScene(pair.FG);
  return true;
}
