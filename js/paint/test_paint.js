// 测试"背景图 + 程序打光"：占位背景 + 小满的图，三种光（arg：fluor 日光灯 / moon 停电月光 / lamp 马灯 / torch 手电）
import { renderPaint } from './paintshot.js';
export async function render(ctx, arg, W, H) {
  const mode = arg || 'lamp';
  const shot = {
    bg: 'bg_01_room_wide', size: [2048, 1152],
    layers: () => [{ img: '/assets/chars/x16_arms_loose.png', x: 900, y: 420, sc: 0.62 }],
    light: () => ({
      fluor: { ambient: [0.95, 0.98, 1.0], exposure: 1.0, vignette: 0.2 },
      moon: { ambient: [0.012, 0.016, 0.03], shafts: [{ poly: [[170, 210], [500, 210], [1150, 1152], [520, 1152]], color: [0.25, 0.32, 0.55], i: 1.0, soft: 30 }], vignette: 0.5 },
      lamp: { ambient: [0.015, 0.012, 0.012], lights: [{ x: 1400, y: 380, r: 1500, color: [1.0, 0.62, 0.3], i: 2.4 }], vignette: 0.45 },
      torch: { ambient: [0.01, 0.012, 0.02], cone: { x: 700, y: 900, ang: -0.7, spread: 0.18, len: 1500, color: [0.95, 0.95, 0.85], i: 1.6 } },
    }[mode]),
    glow: () => (mode === 'lamp' ? [{ x: 1400, y: 380, r: 90, color: [255, 200, 120], a: 0.9 }] : []),
    cam: () => ({ x: 1024, y: 576, zoom: W / 2048 }),
  };
  return renderPaint(ctx, 0, W, H, shot);
}
