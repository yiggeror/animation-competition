// Adopted F000–089. F072–089 use the delivered complete sleeve repair sources.
export const FPS = 24;
export const SHOT_DURATION = 12;
export const SHOT_TOTAL_FRAMES = 288;
export const STATES = Object.freeze([
  {
    "state": 0,
    "start": 0,
    "end": 23,
    "count": 24,
    "url": "/assets/chars/s29/F000.png",
    "sha256": "d9652a3c78e1a5eb348bb33eb7a1ebf4e1b5293734937ddd7a6381214ddc1a21"
  },
  {
    "state": 24,
    "start": 24,
    "end": 29,
    "count": 6,
    "url": "/assets/chars/s29/F024.png",
    "sha256": "b7201bbe59ad1b083bd0458c74ccb2a817154b64ee42b764962cce009c9ab4e8"
  },
  {
    "state": 30,
    "start": 30,
    "end": 35,
    "count": 6,
    "url": "/assets/chars/s29/F030.png",
    "sha256": "72242b30bce5a044257b18089b44f2440dab72c8f256bc28393775ee0602f1e9"
  },
  {
    "state": 36,
    "start": 36,
    "end": 41,
    "count": 6,
    "url": "/assets/chars/s29/F036.png",
    "sha256": "ae89f0737e6b9e2a4c340db4526403a96c186750332fba9ebdd2aff6fe75fef0"
  },
  {
    "state": 42,
    "start": 42,
    "end": 47,
    "count": 6,
    "url": "/assets/chars/s29/F042.png",
    "sha256": "63842e69701a7a8efef2fe39767788cb84875cf70c2b26027b982848e03e9e9b"
  },
  {
    "state": 48,
    "start": 48,
    "end": 53,
    "count": 6,
    "url": "/assets/chars/s29/F048.png",
    "sha256": "5a38d69ec46b267476c1ddc9b39be6857bf84c65db50902b6823f920a9e2dab5"
  },
  {
    "state": 54,
    "start": 54,
    "end": 56,
    "count": 3,
    "url": "/assets/chars/s29/F054.png",
    "sha256": "4ea68fb924f0411a34572ab634cd3c94d7281bec9330786f0f36c57a780bb370"
  },
  {"state":57,"start":57,"end":59,"count":3,"url":"/assets/chars/s29/F057.png","sha256":"ba397acc056ab402bb9ff4f99e5a1122e3e76f10a74086199493ed1f5081da09"},
  {
    "state": 60,
    "start": 60,
    "end": 65,
    "count": 6,
    "url": "/assets/chars/s29/F060.png",
    "sha256": "0ef97e8fd184b42fdc3ff18c817869fd0fe73e208bb5117526c62ba399221c8e"
  },
  {
    "state": 66,
    "start": 66,
    "end": 71,
    "count": 6,
    "url": "/assets/chars/s29/F066.png",
    "sha256": "bd6e5d950fa8db7ab805a491203e9d175fb56e7ead11aa00bd48dc6f3e9c2661"
  },
  {"state":72,"start":72,"end":74,"count":3,"url":"/assets/chars/s29/F072.png","sha256":"ebcbe9497dc7091fde207f99bf837ad6614a58deaaff1566b686e70c108c4a29"},
  {"state":75,"start":75,"end":77,"count":3,"url":"/assets/chars/s29/F075.png","sha256":"6a3343f0480daa3cc363af40326f1dc686d79f42335d1df5a2be31fede473f8e"},
  {"state":78,"start":78,"end":80,"count":3,"url":"/assets/chars/s29/F078.png","sha256":"07afbebd6adddb10ced36de42bf5d3ec4a5b74eb100f554b57c0a3f3bdfea470"},
  {"state":81,"start":81,"end":83,"count":3,"url":"/assets/chars/s29/F081.png","sha256":"dc2d422124e2b2c742825062281c58729731ab296d5427a32ad6943c131fd6ea"},
  {"state":84,"start":84,"end":89,"count":6,"url":"/assets/chars/s29/F084.png","sha256":"677f5c3f951bf8e9f206252be7ae666046a96eae3aa9962418d2b64d0fe9f9ff"}
].map(Object.freeze));
export const VERIFIED_RANGE = Object.freeze([Math.min(...STATES.map(s => s.start)), Math.max(...STATES.map(s => s.end))]);
export function resolveFrame(f) {
  if (!Number.isInteger(f) || f < 0 || f >= SHOT_TOTAL_FRAMES) throw new RangeError("S29 frame must be an integer from 0 through 287");
  const row = STATES.find(s => f >= s.start && f <= s.end);
  if (!row) throw new RangeError("S29 F" + String(f).padStart(3, "0") + " is not covered by this bounded review module; no fallback or inferred hold");
  return row;
}
export function frameAtTime(t) {
  if (!Number.isFinite(t)) throw new TypeError("S29 time must be finite");
  return resolveFrame(Math.floor(t * FPS + 1e-7));
}
