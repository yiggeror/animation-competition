// 鹤皮影检查：左 = 床单上的透光效果（暖光底上正片叠底），右 = 后台看到的皮面
import { makeCrane } from './crane.js';
import { drawPuppet } from '../puppet.js';
export async function render(ctx, arg, W, H) {
  const pup = makeCrane();
  const NECK_UP = [1.25, 0.10, 0.08, 0.06, 0.03, 0.0, -0.04, -0.07, -0.09, -0.10, -0.09, -0.07, -0.55];
  const angles = {}; NECK_UP.slice(0, 12).forEach((a, i) => (angles['neck' + i] = a));
  Object.assign(angles, { head: NECK_UP[12], tibia_near: 0.55, tarsus_near: -1.25, foot_near: 0.55, tibia_far: -0.05, tarsus_far: 0.02, foot_far: 0.03 });
  const pose = { angles, rootAngle: 0.04, facing: 1 };
  const g = ctx.createRadialGradient(W * 0.3, H * 0.35, 0, W * 0.3, H * 0.35, W * 0.4);
  g.addColorStop(0, '#fff6dc'); g.addColorStop(1, '#e8b870');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W / 2, H);
  ctx.fillStyle = '#2a2420'; ctx.fillRect(W / 2, 0, W / 2, H);
  for (const [k, mode] of [[0, 't'], [1, 'r']]) {
    ctx.save();
    ctx.translate(W * (0.27 + k * 0.5), H * 0.62);
    const sc = H / 900;
    ctx.scale(sc, -sc);
    if (mode === 't') ctx.globalCompositeOperation = 'multiply';
    drawPuppet(ctx, pup, pose, mode);
    ctx.restore();
  }
  ctx.font = `${Math.round(H * 0.028)}px "Noto Sans SC"`;
  ctx.fillStyle = '#5a3a1c'; ctx.fillText('床单上：马灯透过染色牛皮，镂空处最亮', W * 0.02, H * 0.96);
  ctx.fillStyle = '#d9c7a8'; ctx.fillText('后台看到的皮面', W * 0.52, H * 0.96);
}
