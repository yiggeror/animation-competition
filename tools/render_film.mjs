// 成片：按 js/film/edl.js 把每个镜头做成 1080p24 的中间片 build/final/<id>.mp4（高码率，最后统一压一次）。
// 有 video 的镜头直接用已交付的成片（逐帧对齐到镜头格数），其余用 tools/js/frames.cjs 渲模块，逐帧 PNG 压好后删掉。
// 用法：node tools/render_film.mjs [S12,S20,...] [--force]   不给镜头号就做全部；已有且比模块新的跳过
import { SHOTS } from '../js/film/edl.js';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
const args = process.argv.slice(2), force = args.includes('--force');
const ids = (args.find((a) => !a.startsWith('--')) || '').split(',').filter(Boolean);
fs.mkdirSync('build/final', { recursive: true });
for (const s of SHOTS) {
  if (ids.length && !ids.includes(s.id)) continue;
  const out = `build/final/${s.id}.mp4`, n = Math.round(s.dur * 24), src = s.video || s.mod;
  if (!force && fs.existsSync(out) && fs.statSync(out).mtimeMs > fs.statSync(src).mtimeMs) { console.log(`${s.id}：已有，跳过`); continue; }
  const t0 = Date.now();
  let r;
  if (s.video) {
    r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', s.video, '-an', '-vf', 'scale=1920:1080:flags=lanczos,fps=24,setsar=1', '-frames:v', String(n),
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '12', '-pix_fmt', 'yuv420p', '-tune', 'animation', out], { stdio: 'inherit' });
  } else {
    r = spawnSync('nice', ['-n', '10', 'node', 'tools/js/frames.cjs', s.mod, `build/frames_final/${s.id}`, '--fps', '24', '--w', '1920', '--h', '1080',
      '--to', String(s.dur), '--workers', '3', '--crf', '12', '--mp4', out, '--clean', '1'], { stdio: ['ignore', 'ignore', 'inherit'] });
  }
  const got = r.status === 0 ? +spawnSync('ffprobe', ['-v', 'error', '-count_frames', '-select_streams', 'v', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', out]).stdout.toString().trim() : 0;
  console.log(`${s.id}：${r.status === 0 && got === n ? '完成' : '失败'}，${got}/${n} 帧，用时 ${((Date.now() - t0) / 60000).toFixed(1)} 分钟`);
}
