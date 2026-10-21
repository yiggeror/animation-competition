# 成片逐帧核对：build/final/<镜头>.mp4 缩到 640×360，和 Astra 完整画面工作片的同一段逐帧比 PSNR。
# 用法：python3 tools/verify_film.py [S12,S20,...]   低于 28 dB 的帧列出来（正常是压缩误差，约 33–45 dB）
import json, subprocess, sys
import numpy as np
WP = 'collab/reviews/20261021_complete_picture_handoff/preview/workprint_360p24_silent.mp4'
shots = json.loads(subprocess.check_output(['node', '-e', "import('./js/film/edl.js').then(m=>console.log(JSON.stringify(m.SHOTS)))"]))
only = set(sys.argv[1].split(',')) if len(sys.argv) > 1 else None


def frames(path, ss=None, n=None):
    cmd = ['ffmpeg', '-loglevel', 'error'] + (['-ss', f'{ss:.6f}'] if ss is not None else []) + ['-i', path]
    cmd += (['-frames:v', str(n)] if n else []) + ['-vf', 'scale=640:360:flags=area', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.uint8).reshape(-1, 360, 640, 3).astype(np.float32)


rec = 0
for s in shots:
    n = round(s['dur'] * 24)
    if s['id'] in ('TITLE', 'MAKING'):
        continue
    if only is None or s['id'] in only:
        try:
            a = frames(f"build/final/{s['id']}.mp4")
        except Exception:
            print(s['id'], '没有成片'); rec += n; continue
        b = frames(WP, rec / 24, n)
        m = min(len(a), len(b))
        p = np.array([10 * np.log10(255 ** 2 / max(1e-6, np.mean((a[i] - b[i]) ** 2))) for i in range(m)])
        bad = [i for i in range(m) if p[i] < 28]
        print(f"{s['id']:5s} {len(a)}/{n} 帧  PSNR 最低 {p.min():.1f} 平均 {p.mean():.1f}" + (f"  低于28：{bad[:12]}{'…' if len(bad) > 12 else ''}" if bad else ''))
    rec += n
