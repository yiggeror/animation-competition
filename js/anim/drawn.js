// 画稿镜头的公用合成：人物是 Astra 画的一张张原图，按曝光表换张；背景是虚化的屋子；场景光只乘一次（paint 管线）。
// sheet = [[图片路径(不带 .png), 从第几帧起], ...]，停到下一张开始。画稿原生约 1672×941，左上对齐、等比放到 1920 宽。
// 还没画到的态先由前一张顶着（WIP），交付时写清楚哪几帧是顶的。
import { closeShot } from './close.js';
export function pickFrom(sheet, t) { const f = Math.floor(t * 24 + 1e-6); let k = sheet[0][0]; for (const [n, f0] of sheet) if (f >= f0) k = n; return k; }
export function drawnShot({ sheet, bgKey, bgCrop, blur = 16, light, cam, emit, under }) {
  const shot = closeShot({
    bgKey, bgCrop, blur, light, emit,
    layers: async (t) => [...(under ? under(t) : []), { img: pickFrom(sheet, t) + '.png', x: 0, y: 0, sc: 1920 / 1672 }],
    cam: cam || (() => ({ x: 960, y: 540, fit: 1 })),
  });
  return (ctx, t, W, H) => shot.render(ctx, t, W, H);
}
