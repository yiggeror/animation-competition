// 给预览短片配上全片混音里对应的那一段（256k AAC，低码率会让高频噪声的峰值冲过满幅）：node tools/clip_audio.mjs ID 输出.mp4
import { SHOTS } from '../js/film/edl.js';
import { execFileSync } from 'node:child_process';
const [id, out] = process.argv.slice(2);
let t0 = 0; for (const s of SHOTS) { if (s.id === id) break; t0 += s.dur; }
const s = SHOTS.find((x) => x.id === id);
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', `build/preview_shots/${id}.mp4`, '-ss', String(t0), '-t', String(s.dur), '-i', 'build/audio/film_mix_norm.wav',
  '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', out]);
console.log(id, 'start', t0, 'dur', s.dur, '→', out);
