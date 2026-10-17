// 常用的角色动作（骨架姿势随时间变化），各镜头直接调用
import { blinkAt } from './warp.js';
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
// 奶奶剥毛豆（g01_beans）：每 1.2 秒剥一颗——两手一捏一掰，头跟着手低一下；looks 给的时刻抬眼看一下前面（小满）；
// 身子随呼吸起伏；不定时眨眼。o.stop：从这个时刻起停下手里的活（停电、被手电照）
export function grandmaBeans(t, o = {}) {
  const work = o.stop != null ? 1 - sstep(o.stop, o.stop + 0.4, t) : 1;
  const ph = (t % 1.2) / 1.2, pinch = Math.sin(ph * Math.PI * 2) * work, snap = Math.exp(-Math.pow((ph - 0.55) * 9, 2)) * work;
  const look = Math.max(0, ...(o.looks || []).map((a) => sstep(a, a + 0.3, t) * (1 - sstep(a + 0.9, a + 1.3, t))), o.up ? sstep(o.up, o.up + 0.5, t) : 0);
  const br = Math.sin(t / 3.6 * 2 * Math.PI);
  return {
    spine: { rot: 0.008 * br - 0.02 * look, sy: 1 + 0.005 * br },
    neck: { rot: 0.02 * snap - 0.05 * look },
    head: { rot: 0.025 * pinch * (1 - look) - 0.08 * look },
    upperarm_near: { rot: 0.02 * pinch }, forearm_near: { rot: 0.05 * pinch + 0.04 * snap }, hand_near: { rot: 0.08 * snap },
    upperarm_far: { rot: -0.015 * pinch }, forearm_far: { rot: -0.04 * pinch - 0.05 * snap }, hand_far: { rot: -0.1 * snap },
    __blink: blinkAt(t, o.blinks || [0.9, 3.7, 6.1, 9.4, 11.2]),
  };
}
