// Exact verified range only. Missing early evidence fails closed.
export const FPS = 24;
export const SHOT_DURATION = 12;
export const SHOT_TOTAL_FRAMES = 288;
export const STATES = Object.freeze([
  {
    "state": 36,
    "start": 36,
    "end": 41,
    "count": 6,
    "url": "/assets/chars/s29/F036.png",
    "sha256": "233294ffa3487f7e00fe0fce78fc3d29520cc91f54f62b70f7be789e44378978"
  },
  {
    "state": 42,
    "start": 42,
    "end": 47,
    "count": 6,
    "url": "/assets/chars/s29/F042.png",
    "sha256": "6321353572a45919c114ebab0e3c616c92bd5007afbe97ca3018b06a272b3444"
  },
  {
    "state": 48,
    "start": 48,
    "end": 53,
    "count": 6,
    "url": "/assets/chars/s29/F048.png",
    "sha256": "7cfb050414a6fde23fddf3f44bf2c83ddaae54f0be6b25d3babb874dda40b298"
  },
  {
    "state": 54,
    "start": 54,
    "end": 59,
    "count": 6,
    "url": "/assets/chars/s29/F054.png",
    "sha256": "d325fd3bc84a6a049aba27a7a07de6363b50adcb46d90132cdb3987687dffe64"
  },
  {
    "state": 60,
    "start": 60,
    "end": 65,
    "count": 6,
    "url": "/assets/chars/s29/F060.png",
    "sha256": "b58a1241dd966774e9ff68c2ae5e05fadeca523a016b6cabecc264318c9d40c5"
  },
  {
    "state": 66,
    "start": 66,
    "end": 71,
    "count": 6,
    "url": "/assets/chars/s29/F066.png",
    "sha256": "37f431300cd341dc1992380e75788f0957a7bc3ecdc81ff90fe4f587451e42f0"
  }
].map(Object.freeze));
export const VERIFIED_RANGE = Object.freeze([Math.min(...STATES.map(s => s.start)), Math.max(...STATES.map(s => s.end))]);
export function resolveFrame(f) {
  if (!Number.isInteger(f) || f < 0 || f >= SHOT_TOTAL_FRAMES) throw new RangeError("S29 frame must be an integer from 0 through 287");
  const row = STATES.find(s => f >= s.start && f <= s.end);
  if (!row) throw new RangeError("S29 F" + String(f).padStart(3, "0") + " is not covered by this verified prefix module; no fallback or inferred hold");
  return row;
}
export function frameAtTime(t) {
  if (!Number.isFinite(t)) throw new TypeError("S29 time must be finite");
  return resolveFrame(Math.floor(t * FPS + 1e-7));
}
