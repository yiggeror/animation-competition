// 乌龟皮影检查：左 = 床单上的透光效果（缩着脖子在爬），中 = 伸长脖子，右 = 后台看到的皮面
import { makeTurtle, turtlePose } from './turtle.js';
import { drawPuppet } from '../puppet.js';
export async function render(ctx, arg, W, H) {
  const pup = makeTurtle();
  const g = ctx.createRadialGradient(W * 0.33, H * 0.4, 0, W * 0.33, H * 0.4, W * 0.45);
  g.addColorStop(0, '#fff6dc'); g.addColorStop(1, '#e8b870');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W * 2 / 3, H);
  ctx.fillStyle = '#2a2420'; ctx.fillRect(W * 2 / 3, 0, W / 3, H);
  const poses = [turtlePose(0.3, { facing: 1 }), turtlePose(0.3, { facing: 1, neckOut: 1, walk: 0, bite: 1 }), turtlePose(0.3, { facing: 1 })];
  poses.forEach((pose, k) => {
    ctx.save();
    ctx.translate(W * (0.16 + k * 0.333), H * 0.62);
    const sc = H / 700;
    ctx.scale(sc, -sc);
    if (k < 2) ctx.globalCompositeOperation = 'multiply';
    drawPuppet(ctx, pup, pose, k < 2 ? 't' : 'r');
    ctx.restore();
  });
  ctx.font = `${Math.round(H * 0.035)}px "Noto Sans SC"`;
  ctx.fillStyle = '#5a3a1c'; ctx.fillText('床单上：缩着脖子爬', W * 0.03, H * 0.95); ctx.fillText('伸长脖子张嘴', W * 0.36, H * 0.95);
  ctx.fillStyle = '#d9c7a8'; ctx.fillText('后台看到的皮面', W * 0.7, H * 0.95);
}
