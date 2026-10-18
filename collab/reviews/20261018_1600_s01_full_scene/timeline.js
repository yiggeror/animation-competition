// Local candidate only. All coordinates are in the original 1672 x 941 plate.
export const FPS = 24;
export const FRAME_COUNT = 84;
export const DURATION = FRAME_COUNT / FPS;
export const REGISTRATION = Object.freeze({
  G: Object.freeze({ x: 730, y: 375, sc: 0.2734375 }),
  X: Object.freeze({ x: 399.28, y: 533, sc: 0.16 }),
});
export const ASSET_INFO = Object.freeze({
  "F000_play_phone.png": {
    "sha256": "de7b4b8c2c3918a4b6f05c451fb675e56a9677d3cb94c18ae106e13c848d061c",
    "width": 1792,
    "height": 1024
  },
  "F010_near_leg_down.png": {
    "sha256": "04696fecfc23579ebc336220a0d5d60cfeae24de73d73e105526db929f98d11c",
    "width": 1792,
    "height": 1024
  },
  "F020_near_leg_highest.png": {
    "sha256": "a96a1949b464b828f0e123a4079e9cde82414def262d15ce99a4e4b290f1408d",
    "width": 1792,
    "height": 1024
  },
  "F043_far_leg_raised.png": {
    "sha256": "fd0e1015c9a7d97f89c7f1714c1a47cd3512f214961de29aea758357b61278b9",
    "width": 1792,
    "height": 1024
  },
  "F000_grandma_rgba.png": {
    "sha256": "669a5e5b7b17ecbaddb0bb6aa266125de870def74c3517cecb9fff3b5fab9720",
    "width": 1024,
    "height": 1536
  },
  "F010_grandma_rgba.png": {
    "sha256": "e16373bebbb95f92ac0bdbbb2d15d34a8c10fe252cacf3108c38318272e4e2c2",
    "width": 1024,
    "height": 1536
  },
  "F012_grandma_rgba.png": {
    "sha256": "e1b72562a2bc96b9ffc6e5e234a93eb573a7406afcdfa536d4c3c2f56d1589d4",
    "width": 1024,
    "height": 1536
  },
  "F028_grandma_rgba.png": {
    "sha256": "7e1b7d61dce421bed7398ad2424075f7a33960df76d3799b9da4b26c4a9736e1",
    "width": 1024,
    "height": 1536
  },
  "F029_grandma_rgba.png": {
    "sha256": "ae23393fef130dc63b01f717c4dd8b72a69f81575e8e459cf0bedefed36892e9",
    "width": 1024,
    "height": 1536
  },
  "F030_grandma_rgba.png": {
    "sha256": "15c58e82435e85101ad363c34ed1812b48a9e0ec8f9232acc1ec47cb5d0724d3",
    "width": 1024,
    "height": 1536
  },
  "F031_grandma_rgba.png": {
    "sha256": "0a666420f68571dd1020b6c941ffe8d7e39cae0024709e2b0d6c74c1f270a8a0",
    "width": 1024,
    "height": 1536
  },
  "F032_grandma_rgba.png": {
    "sha256": "97d7cb59ae965e9e49bb4fe95669fc916fcbd9e2f266c168c112e2b58e924dd4",
    "width": 1024,
    "height": 1536
  },
  "F033_grandma_rgba.png": {
    "sha256": "a7a5139589cc022e1899754b2e74d9aba41b7a23435b45bb7b1ec0fa805f85a4",
    "width": 1024,
    "height": 1536
  },
  "F034_grandma_rgba.png": {
    "sha256": "0e404d79c70524bde78dfb3d7b1eb6b080c33e8bd7ee959ed489717da446edf9",
    "width": 1024,
    "height": 1536
  },
  "F035_grandma_rgba.png": {
    "sha256": "9c990585a527f2d61f994f73b9e727949cb0aecfe6a260bff19fe1381d9925d6",
    "width": 1024,
    "height": 1536
  },
  "F050_grandma_rgba.png": {
    "sha256": "40576c390567a2ccf9bf7af81aeb14080daaf283e4d54e18decc1fbe8fc49303",
    "width": 1024,
    "height": 1536
  },
  "F062_grandma_rgba.png": {
    "sha256": "187d94855ad8aa73b71d8da9fffaa8681ce5eddb94cbb54ce57151a923c31a7c",
    "width": 1024,
    "height": 1536
  },
  "F070_grandma_rgba.png": {
    "sha256": "ab4744921b19448283aff27ea729ea6d2ba4b3b90dbc0d1247b981567a055eb8",
    "width": 1024,
    "height": 1536
  }
});
export const G_SHEET = Object.freeze([[0, "F000_grandma_rgba.png"], [10, "F010_grandma_rgba.png"], [12, "F012_grandma_rgba.png"], [28, "F028_grandma_rgba.png"], [29, "F029_grandma_rgba.png"], [30, "F030_grandma_rgba.png"], [31, "F031_grandma_rgba.png"], [32, "F032_grandma_rgba.png"], [33, "F033_grandma_rgba.png"], [34, "F034_grandma_rgba.png"], [35, "F035_grandma_rgba.png"], [50, "F050_grandma_rgba.png"], [62, "F062_grandma_rgba.png"], [70, "F070_grandma_rgba.png"]].map(Object.freeze));
export const X_SHEET = Object.freeze([[0, "F000_play_phone.png"], [10, "F010_near_leg_down.png"], [20, "F020_near_leg_highest.png"], [35, "F010_near_leg_down.png"], [43, "F043_far_leg_raised.png"]].map(Object.freeze));
export function frameIndex(seconds) {
  if (!Number.isFinite(seconds) || seconds < 0) throw new RangeError('Invalid S01 time: ' + seconds);
  return validateFrame(Math.floor(seconds * FPS + 1e-6));
}
export function validateFrame(frame) {
  if (!Number.isInteger(frame) || frame < 0 || frame >= FRAME_COUNT) throw new RangeError('S01 frame outside 0–83: ' + frame);
  return frame;
}
export function pickAsset(role, frame) {
  validateFrame(frame);
  if (role !== 'G' && role !== 'X') throw new RangeError('Unknown S01 role: ' + role);
  const sheet = role === 'G' ? G_SHEET : X_SHEET;
  let entry = sheet[0], index = 0;
  for (let i = 1; i < sheet.length; i++) if (frame >= sheet[i][0]) { entry = sheet[i]; index = i; }
  if (!entry[1]) {
    const end = index + 1 < sheet.length ? sheet[index + 1][0] - 1 : FRAME_COUNT - 1;
    throw new Error(`S01 missing locked ${role} F${String(entry[0]).padStart(3, '0')}; required frames ${entry[0]}–${end}. No hold substitute is permitted.`);
  }
  return entry[1];
}
export function frameAssets(frame) { return { G: pickAsset('G', frame), X: pickAsset('X', frame) }; }
