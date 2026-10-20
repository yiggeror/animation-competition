// S29 wide continuation; final F120 delivered at 072f598 and read at d7f6a64.
// Tail motion repair read against f8ada6a, on the complete color-corrected copy.
// Full-shot repair: F123/F126 add the real lift between F120 and the existing lift key.
// Original tail PNGs remain available; all later approved tail actions are retained.
// Complete painted poses only: no mesh, limb warp or image dissolve.
export const WRAP_TAIL_EXPOSURE = Object.freeze([
  { first:116, last:119, url:'/assets/chars/s29/F108.png', label:'wide cut on locked gathering pose' },
  { first:120, last:122, url:'/assets/chars/s29/F120.png', label:'final continued gathering with repaired complete left arm' },
  { first:123, last:125, url:'/assets/chars/s29/F123.png', label:'same pinch lifts the near cloth edge; original puppets still visible' },
  { first:126, last:128, url:'/assets/chars/s29/F126.png', label:'front cloth passes over the original puppets and progressively hides rods' },
  { first:129, last:131, file:'lift', label:'lifted cloth lands over the puppets without changing grips' },
  { first:132, last:135, file:'tailfix_sweep_start', label:'continue the original pinch; far cloth edge begins travelling' },
  { first:136, last:138, file:'tailfix_edge_out_a', label:'far grip carries cloth outward' },
  { first:139, last:141, file:'tailfix_edge_out_b', label:'far grip continues outward without releasing' },
  { first:142, last:144, file:'tailfix_grip_roll', label:'near wrist rolls through a three-quarter grip' },
  { first:145, last:148, file:'tailfix_cover_low', label:'cloth spreads over the covered bundle' },
  { first:149, last:153, file:'lowering', label:'existing controlled lowering key' },
  { first:154, last:156, file:'tailfix_lower_end', label:'last controlled lowering before release' },
  { first:157, last:159, file:'tailfix_thumb_release', label:'thumb leaves the pinch while fingertips support cloth' },
  { first:160, last:162, file:'tailfix_finger_open', label:'fingers unfurl without reversing wrist' },
  { first:163, last:166, file:'tailfix_fingertip_touch', label:'curved fingertips arrive on cloth' },
  { first:167, last:171, file:'tailfix_palm_approach', label:'palm heel approaches the bundle' },
  { first:172, last:178, file:'contact', label:'existing palm contact key' },
  { first:179, last:187, file:'tailfix_settle_ease', label:'hands soften into the supported rest' },
  { first:188, last:239, file:'settled', label:'existing final bundle position; completed rest while Xiaoman turns' },
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
