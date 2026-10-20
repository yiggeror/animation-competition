// 床单戏镜头的公共部分：镜头模块只要写 sheet(t, env)（床单上的皮影）、可选的 cam(t) 和 cards
import { renderShot, DEBUG } from '../s06_key.js';
export function makeShot(def) {
  const shot = (t) => ({ ...def, cam: typeof def.cam === 'function' ? def.cam(t) : def.cam, cards: def.cards ?? null });
  return {
    render: async (ctx, arg, W, H) => {
      let t = +arg || 0;
      if (arg && arg.startsWith('{')) { const o = JSON.parse(arg); Object.assign(DEBUG, o); t = o.t ?? 0; }
      return renderShot(ctx, t, W, H, shot(t));
    },
    renderFrame: async (ctx, t, W, H) => renderShot(ctx, t, W, H, shot(t)),
  };
}
// 床单正面、只看床单（不带小满）
export const CAM_B = { pos: [1.32, -2.35, 0.78], target: [1.32, 0, 0.86], hfov: 52 };
