// Independent S04 candidate. Native plate1672x941; fixed72 frames.
export const FPS = 24, FRAME_COUNT = 72, DURATION = 3, CUT_FRAME = 7, CUT = CUT_FRAME / FPS;
export const REGISTRATION = Object.freeze({ G: Object.freeze({x:730,y:375,sc:.2734375}), X: Object.freeze({x:399.28,y:533,sc:.16}) });
export const PHONE = Object.freeze([651.5470192584075,623.1511698764012]); // Real visible-phone region proxy; scene light only, final Canvas check pending.
export const ASSET_INFO = Object.freeze({
  "S01_F012_grandma_rgba.png": {
    "sha256": "e1b72562a2bc96b9ffc6e5e234a93eb573a7406afcdfa536d4c3c2f56d1589d4",
    "width": 1024,
    "height": 1536
  },
  "F010_near_leg_down.png": {
    "sha256": "04696fecfc23579ebc336220a0d5d60cfeae24de73d73e105526db929f98d11c",
    "width": 1792,
    "height": 1024
  },
  "S04_F022_grandma_rgba.png": {
    "sha256": "6fc727833e49c9e0e70f9bb67d5755352b2a38b453b3678d60816ee2f41ad377",
    "width": 1024,
    "height": 1536
  },
  "S04_F028_grandma_rgba.png": {
    "sha256": "e08c927ad58a481a9cf2d3c8ec790efdf94ba0e7e080e2549673d5282c76b468",
    "width": 1024,
    "height": 1536
  },
  "S04_F034_grandma_rgba.png": {
    "sha256": "32cada22cb7094e0539913ed591bf54d4b61a2ed8c017c4cf812316849f67b43",
    "width": 1024,
    "height": 1536
  }
});
export const G_SHEET = Object.freeze([[0, "S01_F012_grandma_rgba.png"], [7, "S01_F012_grandma_rgba.png"], [22, "S04_F022_grandma_rgba.png"], [28, "S04_F028_grandma_rgba.png"], [34, "S04_F034_grandma_rgba.png"]].map(Object.freeze));
export function frameIndex(t) { if (!Number.isFinite(t) || t < 0) throw new RangeError('Invalid S04 time'); return validateFrame(Math.floor(t*FPS+1e-6)); }
export function validateFrame(f) { if (!Number.isInteger(f) || f<0 || f>=FRAME_COUNT) throw new RangeError('S04 frame outside0–71: '+f); return f; }
export function frameAssets(f) {
  validateFrame(f); let i=0;
  for(let j=1;j<G_SHEET.length;j++) if(f>=G_SHEET[j][0]) i=j;
  const [key,name]=G_SHEET[i],end=i+1<G_SHEET.length?G_SHEET[i+1][0]-1:FRAME_COUNT-1;
  if(!name) throw new Error(`S04 missing locked G F${String(key).padStart(3,'0')}; required frames ${key}–${end}. No hold substitute is permitted.`);
  return {G:name,X:'F010_near_leg_down.png'};
}
export function isDark(t) { return frameIndex(t)>=CUT_FRAME; }
