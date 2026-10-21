// 成片合成：按 js/film/edl.js 把 build/final/<镜头>.mp4 接起来，配上母带 build/audio/film_mix_norm.wav，压成一条 1080p24 成片。
// 用法：node tools/master_film.mjs [--out renders/final/nainai-de-piying_1080p24.mp4] [--crf 17]
import { SHOTS } from '../js/film/edl.js';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const a = process.argv.slice(2), opt = {};
for (let i = 0; i < a.length; i++) if (a[i].startsWith('--')) opt[a[i].slice(2)] = a[++i];
const out = opt.out || 'renders/final/nainai-de-piying_1080p24.mp4', crf = opt.crf || '17';
const list = SHOTS.map((s) => path.resolve(`build/final/${s.id}.mp4`));
const missing = list.filter((f) => !fs.existsSync(f));
if (missing.length) { console.error('缺镜头：', missing.join(' ')); process.exit(1); }
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync('build/final/list.txt', list.map((f) => `file '${f}'`).join('\n'));
const frames = SHOTS.reduce((t, s) => t + Math.round(s.dur * 24), 0);
const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'build/final/list.txt', '-i', 'build/audio/film_mix_norm.wav',
  '-map', '0:v', '-map', '1:a', '-frames:v', String(frames), '-c:v', 'libx264', '-preset', 'slow', '-crf', crf, '-tune', 'animation', '-pix_fmt', 'yuv420p',
  '-profile:v', 'high', '-r', '24', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-t', String(frames / 24), '-movflags', '+faststart',
  '-metadata', 'title=奶奶的皮影', out], { stdio: 'inherit' });
if (r.status !== 0) process.exit(r.status);
console.log(out, `${frames} 帧，${(frames / 24).toFixed(3)} 秒，${(fs.statSync(out).size / 1e6).toFixed(1)} MB`);
