// 成片：只渲指定的镜头到 1080p 24 帧（build/shots/ID.mp4），逐帧 PNG 压好后删掉。用低优先级跑，不挡预览。
// 用法：node tools/render_final.mjs S27,S15,S16 [--force]
import { SHOTS } from '../js/film/edl.js';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
const ids = (process.argv[2] || '').split(',').filter(Boolean), force = process.argv.includes('--force');
fs.mkdirSync('build/shots', { recursive: true });
for (const id of ids) {
  const s = SHOTS.find((x) => x.id === id);
  if (!s || !s.mod) { console.log(`${id}：剪辑表里没有模块，跳过`); continue; }
  const out = `build/shots/${id}.mp4`;
  if (!force && fs.existsSync(out) && fs.statSync(out).mtimeMs > fs.statSync(s.mod).mtimeMs) { console.log(`${id}：已有，跳过`); continue; }
  const t0 = Date.now();
  const r = spawnSync('nice', ['-n', '19', 'node', 'tools/js/frames.cjs', s.mod, `build/frames/${id}`, '--fps', '24', '--w', '1920', '--h', '1080', '--to', String(s.dur), '--workers', '3', '--mp4', out, '--clean', '1'], { stdio: ['ignore', 'ignore', 'inherit'] });
  console.log(`${id}：${r.status === 0 ? '完成' : '失败'}，${s.dur} 秒，用时 ${((Date.now() - t0) / 60000).toFixed(1)} 分钟`);
}
