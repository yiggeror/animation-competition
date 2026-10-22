# 真实录音（assets/sfx/*.mp3，Freesound CC0，来源见 assets/sfx/manifest.json）的读取和切分。
# hits(名字)：按能量包络找出录音里每一个独立的声音（脚步、咔哒、衣夹……），每段从起音前 4 毫秒开始，放到时间点上起音就对齐画面。
import os, subprocess
import numpy as np
from inst import SR, hp
ROOT = os.path.join(os.path.dirname(__file__), '..')
_cache = {}


def load(name):
    if name not in _cache:
        raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', os.path.join(ROOT, 'assets', 'sfx', name + '.mp3'), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                             capture_output=True, check=True).stdout
        _cache[name] = hp(np.frombuffer(raw, np.float32).copy(), 30).astype(np.float32)
    return _cache[name]


def _env(x, win=0.005):
    n = max(1, int(win * SR)); e = np.sqrt(np.convolve(x ** 2, np.ones(n) / n, 'same') + 1e-12)
    return 20 * np.log10(e)


def _fade(y, a=0.002, r=0.03):
    y = y.copy(); na, nr = min(len(y), int(a * SR)), min(len(y), int(r * SR))
    if na: y[:na] *= np.linspace(0, 1, na)
    if nr: y[-nr:] *= np.linspace(1, 0, nr)
    return y


def hits(name, rel=-24, gap=0.06, maxlen=1.2, pre=0.004):
    """[(起音秒数, 片段)]：包络从低于(峰值+rel-6)升到高于(峰值+rel)算一次起音，降到峰值+rel-18 以下 40 毫秒算结束"""
    x = load(name); e = _env(x); top = e.max(); on_t, off_t = top + rel, top + rel - 18
    out, i, n = [], 0, len(x)
    armed = True
    while i < n:
        if armed and e[i] > on_t:
            s = max(0, i - int(pre * SR)); j = i; quiet = 0
            while j < n and j - s < maxlen * SR:
                quiet = quiet + 1 if e[j] < off_t else 0
                if quiet > 0.04 * SR: break
                j += 1
            seg = x[s:j]; out.append((s / SR, _fade(seg / (np.abs(seg).max() + 1e-9))))
            i = max(j, i + int(gap * SR)); armed = False
        else:
            if e[i] < on_t - 6: armed = True
            i += 1
    return out


def one(name, i=0, maxlen=None, **kw):
    h = hits(name, **kw); y = h[i % len(h)][1]
    return _fade(y[:int(maxlen * SR)]) if maxlen else y


def seg(name, t0, t1, r=0.03):
    x = load(name); y = x[int(t0 * SR):int(t1 * SR)]
    return _fade(y / (np.abs(y).max() + 1e-9), 0.003, r)


def whole(name):
    return seg(name, 0, len(load(name)) / SR)


def loop(name, dur, xf=1.5, t0=0.0, t1=None):
    """把录音（可截一段）首尾交叉淡化循环成 dur 秒，按 RMS 归一到 0.1"""
    x = load(name); x = x[int(t0 * SR):int((t1 or len(x) / SR) * SR)]
    n, k = int(dur * SR), int(xf * SR); out = np.zeros(n, np.float32); pos = 0
    w = np.linspace(0, 1, k, dtype=np.float32)
    while pos < n:
        y = x.copy(); y[:k] *= w; y[-k:] *= w[::-1]
        e = min(n, pos + len(y)); out[pos:e] += y[:e - pos]; pos += len(y) - k
    return out / (np.sqrt(np.mean(out ** 2)) + 1e-9) * 0.1


def pitch(y, semis):
    """整体变调（同时变速），用来把成年女声的笑压低一点"""
    r = 2 ** (semis / 12); idx = np.arange(0, len(y) - 1, r)
    return np.interp(idx, np.arange(len(y)), y).astype(np.float32)
