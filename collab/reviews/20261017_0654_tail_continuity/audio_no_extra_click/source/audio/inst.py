# 乐器合成（全部用代码算出来，不用任何采样）。采样率 48 kHz，单声道 float32，-1..1。
# 板胡、笛子：连续的旋律线（滑音、揉弦、换弓/吐音）用加法合成 + 琴筒/笛管共鸣滤波 + 弓噪/气声/笛膜的沙音。
# 扬琴、琵琶：Karplus-Strong 拨弦。梆子、板鼓、小锣、大锣、钹：模态合成（几组衰减的正弦 + 噪声）。
# 8-bit：手机游戏里的方波、三角波、噪声鼓（小狗出场时的"现代"声音）。
import numpy as np
from scipy import signal

SR = 48000
RNG = np.random.default_rng(20261016)


def secs(n):
    return np.arange(n) / SR


def ns(d):
    return max(1, int(round(d * SR)))


# ---------------------------------------------------------------- 滤波
def biquad_peak(f0, gain_db, q):
    A = 10 ** (gain_db / 40); w = 2 * np.pi * f0 / SR; al = np.sin(w) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w), 1 - al * A]; a = [1 + al / A, -2 * np.cos(w), 1 - al / A]
    return np.array(b) / a[0], np.array(a) / a[0]


def peq(x, bands):
    for f0, g, q in bands:
        b, a = biquad_peak(f0, g, q); x = signal.lfilter(b, a, x)
    return x


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, min(hi, SR / 2 * 0.95)], 'bandpass', fs=SR, output='sos')
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, min(f, SR / 2 * 0.95), 'lowpass', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, 'highpass', fs=SR, output='sos'), x)


def smooth_noise(n, rate, seed=None):
    """慢慢变化的随机曲线（rate 次/秒），用来做细微的抖动"""
    r = np.random.default_rng(seed) if seed is not None else RNG
    k = max(2, int(n / SR * rate) + 2)
    pts = r.standard_normal(k)
    return np.interp(np.linspace(0, k - 1, n), np.arange(k), pts)


# ---------------------------------------------------------------- 音高
# 简谱 → 频率：key 是 1 的频率（如 D5 = 587.33），deg 1..7，oct 八度偏移；五声音阶以外的 4、7 也能用
MAJOR = [0, 2, 4, 5, 7, 9, 11]


def jp(deg, oct=0, key=587.33, alt=0):
    return key * 2 ** ((MAJOR[deg - 1] + alt) / 12 + oct)


# ---------------------------------------------------------------- 旋律线（板胡、笛子共用）
# notes: [{t, d, f, slide (滑进来的时间，秒), legato (和上一个音连着，不换弓/不吐音), vib (揉弦深度倍数), acc (重音), grace (前倚音频率), trill (颤音的上方音频率)}]
def melody_curves(notes, n, vib_rate=5.8, vib_depth=0.006, attack=0.035, release=0.06):
    f = np.zeros(n); a = np.zeros(n); onset = np.zeros(n)
    prev_f = notes[0]['f']
    for i, nt in enumerate(notes):
        s0 = ns(nt['t']); s1 = min(n, ns(nt['t'] + nt['d']))
        if s1 <= s0:
            continue
        L = s1 - s0; tt = secs(L)
        fr = np.full(L, nt['f'], float)
        sl = nt.get('slide', 0.025)
        if nt.get('legato') or sl > 0.04:   # 滑音：从上一个音滑过来（带一点过冲）
            k = np.clip(tt / max(sl, 1e-3), 0, 1); k = k * k * (3 - 2 * k)
            fr = prev_f + (nt['f'] - prev_f) * k
        else:                                 # 换弓 / 吐音：从低一点的地方很快地"够"上来
            fr = fr * (1 - 0.012 * np.exp(-tt / 0.018))
        if nt.get('grace'):                   # 前倚音：先在上方音停 45 毫秒再落下来
            g = ns(0.045); fr[:g] = nt['grace']
        if nt.get('trill'):                   # 颤音：和上方音快速交替
            tr = (np.sin(2 * np.pi * 11 * tt) > 0) & (tt > 0.04) & (tt < nt['d'] - 0.06)
            fr = np.where(tr, nt['trill'], fr)
        # 揉弦 / 气息颤音：音长了才慢慢出来
        vd = vib_depth * nt.get('vib', 1.0) * np.clip((tt - 0.12) / 0.25, 0, 1)
        fr = fr * (1 + vd * np.sin(2 * np.pi * vib_rate * tt + i))
        f[s0:s1] = fr
        # 音量包络
        acc = nt.get('acc', 0.8)
        env = np.ones(L) * acc
        if not nt.get('legato'):
            env *= np.clip(tt / attack, 0, 1) ** 0.7
            onset[s0:s0 + min(L, ns(0.03))] = acc
        nxt = notes[i + 1] if i + 1 < len(notes) else None
        if not (nxt and nxt.get('legato') and abs(nxt['t'] - (nt['t'] + nt['d'])) < 0.01):
            env *= np.clip((nt['d'] - tt) / release, 0, 1)
        env *= 1 + 0.12 * np.clip(tt / max(nt['d'], 0.1), 0, 1) * nt.get('swell', 0)
        a[s0:s1] = np.maximum(a[s0:s1], env)
        prev_f = nt['f']
    # 没有音的地方频率保持上一个音（避免相位乱跳）
    idx = np.where(f > 0, np.arange(n), 0); np.maximum.accumulate(idx, out=idx)
    f = f[idx]; f[f == 0] = notes[0]['f']
    return f, a, onset


def additive(f, a, amps, jitter=0.0, seed=1):
    """按频率曲线 f、振幅曲线 a 合成谐波（自动去掉超过奈奎斯特频率的谐波）"""
    n = len(f)
    ph = 2 * np.pi * np.cumsum(f) / SR
    jit = 1 + jitter * smooth_noise(n, 8, seed)
    ph = ph * 1.0
    out = np.zeros(n)
    for h, amp in enumerate(amps, 1):
        if amp == 0:
            continue
        ok = (f * h) < SR * 0.45
        if not ok.any():
            break
        wob = 1 + jitter * 2 * smooth_noise(n, 5, seed + h) if jitter else 1
        out += amp * np.sin(h * ph + h * 0.7) * ok * wob
    return out * a * jit


def banhu(notes, dur):
    """板胡：椰壳琴筒、亮、带鼻音；滑音和揉弦很多"""
    n = ns(dur)
    f, a, on = melody_curves(notes, n, vib_rate=6.2, vib_depth=0.008, attack=0.04, release=0.07)
    # 谐波：亮（衰减慢），越响越亮
    amps = [1.0 / h ** 0.85 for h in range(1, 40)]
    x = additive(f, a, amps, jitter=0.05, seed=3)
    # 弓噪：跟着振幅、偏高频
    noise = bp(RNG.standard_normal(n), 1800, 7000) * a * 0.10
    noise += bp(RNG.standard_normal(n), 300, 3000) * on * 0.6   # 换弓时的"擦"
    x = x + noise
    # 琴筒共鸣：几处共振峰，压掉低频，高频软一点
    x = peq(x, [(650, 5, 2.0), (1450, 7, 2.5), (2900, 6, 2.2), (4600, 3, 2.0)])
    x = hp(x, 280); x = lp(x, 9000)
    return (x / (np.abs(x).max() + 1e-9) * 0.8).astype(np.float32)


def dizi(notes, dur):
    """笛子：圆润的基音 + 气声；笛膜让响的地方带一层沙沙的亮音"""
    n = ns(dur)
    f, a, on = melody_curves(notes, n, vib_rate=5.2, vib_depth=0.004, attack=0.03, release=0.05)
    amps = [1.0, 0.42, 0.24, 0.11, 0.07, 0.04, 0.025, 0.015]
    x = additive(f, a * (1 + 0.04 * np.sin(2 * np.pi * 5.2 * secs(n))), amps, jitter=0.03, seed=7)
    # 气声：一层宽带的气 + 贴着基音的窄带噪声
    wn = RNG.standard_normal(n)
    breath = bp(wn, 1500, 9000) * a * 0.035 + on * bp(wn, 800, 6000) * 0.25
    # 笛膜：振幅越大越"沙"，跟着波形的正半周调制
    ph = 2 * np.pi * np.cumsum(f) / SR
    buzz = bp(RNG.standard_normal(n), 3000, 8000) * np.maximum(0, np.sin(ph)) ** 3 * a ** 2 * 0.18
    x = x + breath + buzz
    x = peq(x, [(2500, 3, 1.5)]); x = hp(x, 250)
    return (x / (np.abs(x).max() + 1e-9) * 0.8).astype(np.float32)


# ---------------------------------------------------------------- 拨弦（Karplus-Strong）
def ks(f, dur, damp=0.996, bright=0.5, pick=0.13, seed=None):
    """一根弦拨一下：damp 越接近 1 余音越长；bright 越大越亮；pick 拨弦位置（梳状滤波）"""
    r = np.random.default_rng(seed)
    N = max(2, int(round(SR / f - 0.5)))
    f_act = SR / (N + 0.5)
    n = ns(dur * f / f_act) + N + 2
    y = np.zeros(n)
    exc = r.uniform(-1, 1, N)
    exc = lp(np.concatenate([exc, np.zeros(N)]), 1500 + 9000 * bright)[:N]   # 拨片的软硬
    p = max(1, int(N * pick)); exc = exc - np.concatenate([np.zeros(p), exc[:-p]])
    y[:N] = exc
    g = damp
    # 一次算一个周期（只依赖前一个周期）
    for k in range(1, n // N + 1):
        s = k * N; e = min(n, s + N)
        if s >= n:
            break
        prev = y[s - N:e - N]; prev1 = y[s - N - 1:e - N - 1] if s - N - 1 >= 0 else np.concatenate([[0], y[s - N:e - N - 1]])
        y[s:e] = g * (bright * 0.5 * prev + (1 - bright * 0.5) * 0.5 * (prev + prev1))
    # 重采样到准确的音高
    out_n = ns(dur)
    src = np.arange(out_n) * (f / f_act)
    y = np.interp(src, np.arange(n), y)
    return y


def yangqin(f, dur=2.5, vel=0.8):
    """扬琴：竹槌敲钢丝弦，一组两三根略有差别的弦（有点"拍"），亮、余音长"""
    x = sum(ks(f * (1 + d), dur, damp=0.9985, bright=0.9, pick=0.08, seed=int(f * 10 + i)) for i, d in enumerate([0, 0.0018, -0.0013]))
    y2 = ks(f * 2, dur * 0.5, damp=0.997, bright=0.9, pick=0.2, seed=int(f)); x[:len(y2)] += 0.4 * y2
    env = np.exp(-secs(len(x)) / (1.6 if f < 600 else 0.9))
    x = x * env
    x = peq(x, [(3200, 4, 1.5)]); x = hp(x, 150)
    return (x / (np.abs(x).max() + 1e-9) * vel).astype(np.float32)


def pipa(f, dur=1.2, vel=0.8, tremolo=0.0):
    """琵琶：拨片弹，起音脆、余音短；tremolo > 0 时轮指（快速重复弹）"""
    def one(seed):
        x = ks(f, dur, damp=0.993, bright=0.75, pick=0.12, seed=seed)
        return x * np.exp(-secs(len(x)) / 0.55)
    if tremolo <= 0:
        x = one(int(f))
    else:
        x = np.zeros(ns(dur)); step = 1 / 16.0
        for k, t0 in enumerate(np.arange(0, tremolo, step)):
            y = one(int(f) + k) * (0.7 + 0.3 * (k % 4 == 0)); s = ns(t0)
            x[s:] += y[:len(x) - s]
    x = peq(x, [(900, 4, 1.8), (2400, 5, 2.0)]); x = hp(x, 120)
    return (x / (np.abs(x).max() + 1e-9) * vel).astype(np.float32)


# ---------------------------------------------------------------- 打击乐
def modal(freqs, decays, amps, dur, glide=None):
    n = ns(dur); t = secs(n); x = np.zeros(n)
    for f, d, a in zip(freqs, decays, amps):
        ff = f * (glide(t) if glide else 1)
        ph = 2 * np.pi * np.cumsum(np.broadcast_to(ff, t.shape)) / SR
        x += a * np.sin(ph + RNG.uniform(0, 6)) * np.exp(-t / d)
    return x


def bangzi(vel=0.9, pitch=1.0):
    """梆子：两根硬木相击，又高又脆的"梆" """
    f = 1550 * pitch
    x = modal([f, f * 2.21, f * 3.86, f * 5.2], [0.07, 0.035, 0.018, 0.01], [1, 0.45, 0.25, 0.1], 0.25)
    click = bp(RNG.standard_normal(ns(0.25)), 2500, 9000) * np.exp(-secs(ns(0.25)) / 0.003) * 0.8
    x = (x + click) * vel
    return (x / (np.abs(x).max() + 1e-9) * vel).astype(np.float32)


def bangu(vel=0.7):
    """板鼓（单皮）：很紧、很高的"哒" """
    n = ns(0.2); t = secs(n)
    x = np.sin(2 * np.pi * np.cumsum(900 + 500 * np.exp(-t / 0.01)) / SR) * np.exp(-t / 0.035)
    x += bp(RNG.standard_normal(n), 1500, 7000) * np.exp(-t / 0.012) * 0.6
    return (x / np.abs(x).max() * vel).astype(np.float32)


def xiaoluo(vel=0.8):
    """小锣：敲下去音往上翘（京剧、皮影戏的"台"）"""
    f0 = 620
    x = modal([f0, f0 * 1.48, f0 * 2.27, f0 * 3.05, f0 * 4.1], [0.9, 0.5, 0.35, 0.22, 0.12], [1, 0.5, 0.35, 0.2, 0.1], 1.6,
              glide=lambda t: 1 + 0.16 * (1 - np.exp(-t / 0.09)))
    n = len(x); x += bp(RNG.standard_normal(n), 2000, 8000) * np.exp(-secs(n) / 0.02) * 0.4
    return (x / np.abs(x).max() * vel).astype(np.float32)


def daluo(vel=0.9, dur=3.5):
    """大锣：低沉，音往下沉，余音长"""
    f0 = 190
    x = modal([f0, f0 * 1.31, f0 * 1.67, f0 * 2.13, f0 * 2.74, f0 * 3.4, f0 * 4.5], [2.4, 1.8, 1.5, 1.1, 0.9, 0.6, 0.4],
              [1, 0.7, 0.6, 0.5, 0.35, 0.25, 0.15], dur, glide=lambda t: 1 - 0.07 * (1 - np.exp(-t / 0.4)))
    n = len(x); t = secs(n)
    x *= np.clip(t / 0.03, 0, 1)
    x += bp(RNG.standard_normal(n), 400, 4000) * np.exp(-t / 0.08) * 0.3
    return (x / np.abs(x).max() * vel).astype(np.float32)


def bo(vel=0.8, dur=1.2):
    """钹（铙钹）：一片亮的金属噪声，"呛" """
    n = ns(dur); t = secs(n)
    x = np.zeros(n)
    for f in RNG.uniform(1800, 9000, 40):
        x += np.sin(2 * np.pi * f * t + RNG.uniform(0, 6)) * np.exp(-t / RNG.uniform(0.15, 0.6)) * RNG.uniform(0.2, 1)
    x = x / 40 + bp(RNG.standard_normal(n), 3000, 12000) * np.exp(-t / 0.25) * 0.8
    x *= np.clip(t / 0.002, 0, 1)
    return (x / np.abs(x).max() * vel).astype(np.float32)


def qiang(vel=0.9):
    """"呛"：大锣 + 钹 + 小锣一起敲（段落的重音）"""
    a = daluo(vel, 3.0); b = bo(vel * 0.8, 1.2); c = xiaoluo(vel * 0.6)
    n = len(a); x = a.copy(); x[:len(b)] += b; x[:len(c)] += c
    return (x / np.abs(x).max() * vel).astype(np.float32)


# ---------------------------------------------------------------- 8-bit（手机游戏、小狗）
def _bl_pulse(f, n, duty=0.5, os=4):
    """带限的方波：4 倍过采样画方波，再降采样（去混叠）"""
    N = n * os; ph = np.cumsum(np.repeat(f, os) if np.ndim(f) else np.full(N, f)) / (SR * os)
    x = np.where((ph % 1) < duty, 1.0, -1.0)
    return signal.resample_poly(x, 1, os)[:n]


def chip_lead(notes, dur, duty=0.25, vib=0.0):
    """方波主旋律：notes [{t, d, f}]，每个音短起音、平音量，可加一点颤音"""
    n = ns(dur); f = np.full(n, 440.0); a = np.zeros(n)
    for nt in notes:
        s0 = ns(nt['t']); s1 = min(n, ns(nt['t'] + nt['d'])); L = s1 - s0
        if L <= 0:
            continue
        tt = secs(L)
        f[s0:s1] = nt['f'] * (1 + vib * np.sin(2 * np.pi * 6 * tt) * (tt > 0.15))
        env = np.clip(tt / 0.004, 0, 1) * np.clip((nt['d'] * 0.92 - tt) / 0.01, 0, 1) * nt.get('acc', 0.8)
        a[s0:s1] = env
    x = _bl_pulse(f, n, duty) * a
    return x.astype(np.float32) * 0.5


def chip_tri(notes, dur):
    """三角波低音"""
    n = ns(dur); f = np.full(n, 110.0); a = np.zeros(n)
    for nt in notes:
        s0 = ns(nt['t']); s1 = min(n, ns(nt['t'] + nt['d'])); L = s1 - s0
        if L <= 0:
            continue
        f[s0:s1] = nt['f']; a[s0:s1] = np.clip((nt['d'] * 0.95 - secs(L)) / 0.005, 0, 1) * nt.get('acc', 0.8)
    ph = np.cumsum(f) / SR
    x = (2 * np.abs(2 * (ph % 1) - 1) - 1) * a
    return x.astype(np.float32) * 0.6


def chip_noise(dur=0.12, vel=0.6, lo=False):
    """噪声鼓：短促的"嚓"（lo=True 时是低一点的"咚嚓"）"""
    n = ns(dur); t = secs(n)
    r = RNG.integers(0, 2, n // 24 + 2).repeat(24)[:n] * 2.0 - 1   # 像老游戏机那样的粗噪声
    x = r * np.exp(-t / (0.05 if lo else 0.025))
    if lo:
        x = lp(x, 3000)
    return (x * vel).astype(np.float32)


def kick(vel=0.9):
    """电子底鼓：正弦从高往下扫"""
    n = ns(0.45); t = secs(n)
    f = 45 + 120 * np.exp(-t / 0.03)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18)
    x += bp(RNG.standard_normal(n), 2000, 6000) * np.exp(-t / 0.004) * 0.3
    return (x / np.abs(x).max() * vel).astype(np.float32)


def clap(vel=0.7):
    n = ns(0.3); t = secs(n); x = np.zeros(n)
    for k, d in enumerate([0, 0.009, 0.018, 0.026]):
        s = ns(d); seg = bp(RNG.standard_normal(n - s), 900, 5000) * np.exp(-secs(n - s) / (0.008 if k < 3 else 0.09))
        x[s:] += seg
    return (x / np.abs(x).max() * vel).astype(np.float32)


def woof(vel=0.8):
    """小狗"汪"：方波音高往下一甩，带一点噪声（8-bit 风格，是声音设计，不是真狗叫）"""
    n = ns(0.22); t = secs(n)
    f = 520 * np.exp(-t / 0.12) + 180
    x = _bl_pulse(f, n, 0.3) * np.clip(t / 0.008, 0, 1) * np.exp(-t / 0.09)
    x += chip_noise(0.22, 0.25, lo=True)[:n]
    x = lp(x, 4000)
    return (x / np.abs(x).max() * vel).astype(np.float32)


# ---------------------------------------------------------------- 混音小工具
def place(track, clip, t, gain=1.0):
    s = ns(t)
    if s >= len(track) or s + len(clip) <= 0:
        return
    a = max(0, -s); e = min(len(clip), len(track) - s)
    track[s + a:s + e] += clip[a:e] * gain


def pan(x, p):
    """p: -1 左 … 1 右（等功率）"""
    th = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(th), x * np.sin(th)], 1)


def reverb_ir(rt60=0.8, pre=0.012, seed=5, bright=6000):
    r = np.random.default_rng(seed)
    n = ns(rt60 * 1.2); t = secs(n)
    env = np.exp(-6.9 * t / rt60)
    ir = np.stack([lp(r.standard_normal(n), bright) * env, lp(r.standard_normal(n), bright) * env], 1)
    ir[:ns(pre)] = 0
    return ir / np.sqrt((ir ** 2).sum(0, keepdims=True))


def reverb(st, ir, wet=0.25):
    out = np.stack([signal.fftconvolve(st[:, c], ir[:, c])[:len(st)] for c in range(2)], 1)
    return st * (1 - wet) + out * wet
