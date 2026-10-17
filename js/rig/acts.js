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

// 小满趴着打手机（x01_prone_phone）：按骨头名字里的关键词套动作（绑骨数据的命名细节不同也能用）——
// 拇指一下下点（游戏里跳的时刻 presses），手机和两手作为一整块随游戏微晃，头跟着游戏小幅点，两条小腿交替晃，呼吸，眨眼
export function xiaomanPhone(t, B, o = {}) {
  const presses = o.presses || [1.5, 4.1, 6.7, 9.3, 11.9];
  const press = presses.reduce((a, p) => { const u = t - p; return Math.max(a, u > -0.05 && u < 0.2 ? (u < 0 ? 1 + u / 0.05 : 1 - u / 0.2) : 0); }, 0);
  const tap = 0.5 + 0.5 * Math.sin(t * 2 * Math.PI * 2.2);                 // 另一只拇指在方向键上来回搓
  const br = Math.sin(t / 3.0 * 2 * Math.PI), urg = o.urgent ? sstep(o.urgent, o.urgent + 0.3, t) : 0;
  const P = {};
  for (const b of B.rig.bones) {
    const n = b.name;
    if (/spine|chest|torso/.test(n)) P[n] = { rot: 0.006 * br, sy: 1 + 0.006 * br };
    else if (/neck/.test(n)) P[n] = { rot: 0.015 * press + 0.01 * Math.sin(t * 1.1) };
    else if (/head/.test(n)) P[n] = { rot: 0.02 * press + 0.015 * Math.sin(t * 0.7) + 0.01 * urg * Math.sin(t * 17) };
    else if (/phone/.test(n)) P[n] = { rot: 0.012 * press + 0.006 * Math.sin(t * 1.9) + 0.01 * urg * Math.sin(t * 23) };
    else if (/thumb/.test(n)) P[n] = { rot: /far/.test(n) ? -0.08 * tap * (1 + urg) : -0.12 * press - 0.12 * urg * Math.abs(Math.sin(t * 19)) };
    else if (/shin|calf|lower_leg/.test(n)) P[n] = { rot: (/far/.test(n) ? 1 : -1) * 0.08 * Math.sin(t * 2.4 + (/far/.test(n) ? 1.5 : 0)) };
    else if (/foot/.test(n)) P[n] = { rot: 0.06 * Math.sin(t * 2.4 + 0.6) };
  }
  P.__blink = blinkAt(t, o.blinks || [0.6, 3.3, 5.8, 8.6, 10.7]);
  return P;
}
