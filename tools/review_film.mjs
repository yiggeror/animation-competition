// 给用户看的试片：只拼有画面的镜头（剪辑表里有 mod 的），每个镜头下方标"镜头号 · 剧本这一段"，声音按每个镜头在全片里的位置从母带里切。
// 剧本里的 % 等字符原样显示（drawtext 关掉 expansion，否则"2%"会让整条字幕不显示）。
// 用法：node tools/review_film.mjs [--src build/preview_shots] [--audio build/audio/film_mix_norm.wav] [--out build/film_review.mp4] [--only S01,S02] [--w 960]（输出宽度，16:9；1920 出 1080p，字幕等比放大）
// 镜头视频先用 tools/film.mjs --preview（或 render_final.mjs）渲好；这里只做标注和拼接。
import { SHOTS } from '../js/film/edl.js';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const opt = {}; const a = process.argv.slice(2);
for (let i = 0; i < a.length; i += 2) opt[a[i].replace(/^--/, '')] = a[i + 1];
const src = opt.src || 'build/preview_shots', audio = opt.audio || 'build/audio/film_mix_norm.wav', out = opt.out || 'build/film_review.mp4';
const only = opt.only ? new Set(opt.only.split(',')) : null;
const OW = +(opt.w || 960), OH = Math.round(OW * 9 / 16), K = OW / 960;
const FONT = path.resolve('assets/fonts/NotoSansSC-VF.ttf');
const tmp = 'build/review_tmp'; fs.rmSync(tmp, { recursive: true, force: true }); fs.mkdirSync(tmp, { recursive: true });
const run = (args) => { const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', ...args], { stdio: 'inherit' }); if (r.status !== 0) process.exit(1); };
// 剧本文字按宽度折行（中文按字数）
const wrap = (s, n) => { const lines = []; for (let i = 0; i < s.length; i += n) lines.push(s.slice(i, i + n)); return lines.join('\n'); };
let t0 = 0; const list = [], pcm = [];
for (const s of SHOTS) {
  const start = t0; t0 += s.dur;
  if (!s.mod || (only && !only.has(s.id))) continue;
  const v = path.join(src, `${s.id}.mp4`); if (!fs.existsSync(v)) { console.log(`${s.id}：没有渲好的视频，跳过`); continue; }
  const txt = path.join(tmp, `${s.id}.txt`); fs.writeFileSync(txt, wrap(`${s.id}  ${s.text}`, 34));
  const o = path.join(tmp, `${s.id}.mp4`);
  // 画面下方一条半透明黑底，白字；声音取母带里这个镜头的那一段
  const vf = `scale=${OW}:${OH},drawbox=x=0:y=ih-${92 * K}:w=iw:h=${92 * K}:color=black@0.55:t=fill,drawtext=expansion=none:fontfile='${FONT}':textfile='${txt}':fontsize=${22 * K}:fontcolor=white:line_spacing=${6 * K}:x=${24 * K}:y=h-${82 * K}`;
  // 画面每镜单独编码（不带声音）；声音先按样本切出原样 PCM，最后拼成一整段只编码一次 AAC（分段编 AAC 再拼，接缝处 priming 会叠出十几毫秒，Astra 实测）
  run(['-i', v, '-t', String(s.dur), '-an', '-vf', vf, '-r', '24', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', o]);
  const w = path.join(tmp, `${s.id}.wav`);
  run(['-i', audio, '-af', `atrim=start_sample=${Math.round(start * 48000)}:end_sample=${Math.round((start + s.dur) * 48000)},asetpts=PTS-STARTPTS`, '-ar', '48000', '-c:a', 'pcm_s16le', w]);
  list.push(o); pcm.push(w); console.log(`${s.id}：${s.dur} 秒`);
}
const lt = path.join(tmp, 'list.txt'), la = path.join(tmp, 'alist.txt');
fs.writeFileSync(lt, list.map((f) => `file '${path.resolve(f)}'`).join('\n')); fs.writeFileSync(la, pcm.map((f) => `file '${path.resolve(f)}'`).join('\n'));
run(['-f', 'concat', '-safe', '0', '-i', lt, '-f', 'concat', '-safe', '0', '-i', la, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', out]);
console.log(out, `共 ${list.length} 个镜头`);
