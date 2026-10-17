// 给用户看的试片：只拼有画面的镜头（剪辑表里有 mod 的），每个镜头下方标"镜头号 · 剧本这一段"，声音按每个镜头在全片里的位置从母带里切。
// 用法：node tools/review_film.mjs [--src build/preview_shots] [--audio build/audio/film_mix_norm.wav] [--out build/film_review.mp4] [--only S01,S02]
// 镜头视频先用 tools/film.mjs --preview（或 render_final.mjs）渲好；这里只做标注和拼接。
import { SHOTS } from '../js/film/edl.js';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const opt = {}; const a = process.argv.slice(2);
for (let i = 0; i < a.length; i += 2) opt[a[i].replace(/^--/, '')] = a[i + 1];
const src = opt.src || 'build/preview_shots', audio = opt.audio || 'build/audio/film_mix_norm.wav', out = opt.out || 'build/film_review.mp4';
const only = opt.only ? new Set(opt.only.split(',')) : null;
const FONT = path.resolve('assets/fonts/NotoSansSC-VF.ttf');
const tmp = 'build/review_tmp'; fs.rmSync(tmp, { recursive: true, force: true }); fs.mkdirSync(tmp, { recursive: true });
const run = (args) => { const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', ...args], { stdio: 'inherit' }); if (r.status !== 0) process.exit(1); };
// 剧本文字按宽度折行（中文按字数）
const wrap = (s, n) => { const lines = []; for (let i = 0; i < s.length; i += n) lines.push(s.slice(i, i + n)); return lines.join('\n'); };
let t0 = 0; const list = [];
for (const s of SHOTS) {
  const start = t0; t0 += s.dur;
  if (!s.mod || (only && !only.has(s.id))) continue;
  const v = path.join(src, `${s.id}.mp4`); if (!fs.existsSync(v)) { console.log(`${s.id}：没有渲好的视频，跳过`); continue; }
  const txt = path.join(tmp, `${s.id}.txt`); fs.writeFileSync(txt, wrap(`${s.id}  ${s.text}`, 34));
  const o = path.join(tmp, `${s.id}.mp4`);
  // 画面下方一条半透明黑底，白字；声音取母带里这个镜头的那一段
  const vf = `scale=960:540,drawbox=x=0:y=ih-92:w=iw:h=92:color=black@0.55:t=fill,drawtext=fontfile='${FONT}':textfile='${txt}':fontsize=22:fontcolor=white:line_spacing=6:x=24:y=h-82`;
  run(['-i', v, '-ss', String(start), '-t', String(s.dur), '-i', audio, '-map', '0:v', '-map', '1:a', '-vf', vf, '-r', '24', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', o]);
  list.push(o); console.log(`${s.id}：${s.dur} 秒`);
}
const lt = path.join(tmp, 'list.txt'); fs.writeFileSync(lt, list.map((f) => `file '${path.resolve(f)}'`).join('\n'));
run(['-f', 'concat', '-safe', '0', '-i', lt, '-c', 'copy', out]);
console.log(out, `共 ${list.length} 个镜头`);
