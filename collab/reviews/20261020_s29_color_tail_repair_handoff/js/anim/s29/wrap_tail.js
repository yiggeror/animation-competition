// S29 wide continuation; final F120 delivered at 072f598 and read at d7f6a64.
// Keep the previously delivered five covering / settling drawings unchanged.
// Complete painted poses only: no mesh, limb warp or image dissolve.
export const WRAP_TAIL_EXPOSURE = Object.freeze([
  { first:116, last:119, url:'/assets/chars/s29/F108.png', label:'wide cut on locked gathering pose' },
  { first:120, last:125, url:'/assets/chars/s29/F120.png', label:'final continued gathering' },
  { first:126, last:131, file:'lift', label:'lift and spread the same cloth flap' },
  { first:132, last:137, file:'cover', label:'cloth over both puppets' },
  { first:138, last:143, file:'lowering', label:'early fold lowering' },
  { first:144, last:155, file:'release', label:'release grip and lower fold' },
  { first:156, last:167, file:'contact', label:'palm heel contacts bundle' },
  { first:168, last:239, file:'settled', label:'bundle settled; completed-action hold' },
]);

export async function loadWrapTail(t, loadImg) {
  const frame = Math.floor(t * 24 + 1e-7);
  if (frame < 116 || frame > 239) return null;
  const row = WRAP_TAIL_EXPOSURE.find(r => frame >= r.first && frame <= r.last);
  const girl = await loadImg('/assets/chars/s29_tail/x29_empty_hand.png');
  const mother = row ? await loadImg(row.url || `/assets/chars/s29_tail/${row.file}.png`) : null;
  if (!girl || (row && !mother)) throw Error('Missing S29 wrapping-tail drawing.');
  return { girl, mother };
}
