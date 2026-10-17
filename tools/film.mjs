// 拼粗剪：按 js/film/edl.js 的顺序，做好的镜头（有 mod）逐帧渲染成视频，没做的用占位卡做成静止视频，最后接成一条。
// 用法：node tools/film.mjs [--only S15,S20] [--force] [--fps 24] [--w 1920 --h 1080] [--out build/film_rough.mp4] [--audio build/audio/film_mix.wav]
//       --preview：快速预览（960×540、12 帧/秒、床单图半分辨率，镜头放 build/preview_shots，输出 build/film_preview.mp4）
// 已经渲染过的镜头视频（build/shots/<id>.mp4）比模块新的就跳过，除非 --force。
import { spawnSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { SHOTS } from '../js/film/edl.js';
const opt = {}; const a = process.argv.slice(2);
for (let i = 0; i < a.length; i++) if (a[i].startsWith('--')) opt[a[i].slice(2)] = a[i + 1] && !a[i + 1].startsWith('--') ? a[++i] : true;
const pv = !!opt.preview;
const fps = +(opt.fps || (pv ? 12 : 24)), W = +(opt.w || (pv ? 960 : 1920)), H = +(opt.h || (pv ? 540 : 1080));
const debug = pv ? '{"sheetRes":450}' : null;
const only = opt.only ? new Set(String(opt.only).split(',')) : null;
const dir = pv ? 'build/preview_shots' : 'build/shots'; fs.mkdirSync(dir, { recursive: true });
const run = (cmd, args) => { const r = spawnSync(cmd, args, { stdio: ['ignore', 'inherit', 'inherit'] }); if (r.status !== 0) { console.error('失败：', cmd, args.join(' ')); process.exit(1); } };
const list = [];
for (const s of SHOTS) {
  const out = path.join(dir, `${s.id}.mp4`); list.push(out);
  if (only && !only.has(s.id)) { if (fs.existsSync(out)) continue; }
  const src = s.mod && fs.existsSync(s.mod) ? s.mod : null;
  const fresh = fs.existsSync(out) && (!src || fs.statSync(out).mtimeMs > fs.statSync(src).mtimeMs);
  if (fresh && !opt.force && !(only && only.has(s.id))) { console.log(`${s.id}：已有，跳过`); continue; }
  if (src) {
    console.log(`${s.id}：渲染 ${src}（${s.dur} 秒）`);
    run('node', ['tools/js/frames.cjs', src, `build/${pv ? 'preview_frames' : 'frames'}/${s.id}`, '--fps', String(fps), '--w', String(W), '--h', String(H), '--to', String(s.dur), '--workers', '3', '--mp4', out, '--clean', '1', ...(debug ? ['--debug', debug] : [])]);
  } else {
    console.log(`${s.id}：占位卡`);
    const png = path.join(dir, `${s.id}.png`);
    run('node', ['tools/js/snap.cjs', 'js/film/slate.js', png, String(W), String(H), s.id]);
    run('ffmpeg', ['-y', '-loglevel', 'error', '-loop', '1', '-i', png, '-t', String(s.dur), '-r', String(fps), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-tune', 'stillimage', out]);
  }
}
const txt = path.join(dir, 'list.txt');
fs.writeFileSync(txt, list.map((f) => `file '${path.resolve(f)}'`).join('\n'));
const outFilm = opt.out || (pv ? 'build/film_preview.mp4' : 'build/film_rough.mp4');
const aud = opt.audio && fs.existsSync(opt.audio) ? ['-i', opt.audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-shortest'] : [];
run('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', txt, ...aud, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', String(fps), '-crf', '20', outFilm]);
console.log(outFilm, `共 ${SHOTS.length} 个镜头，${SHOTS.reduce((t, s) => t + s.dur, 0)} 秒`);
