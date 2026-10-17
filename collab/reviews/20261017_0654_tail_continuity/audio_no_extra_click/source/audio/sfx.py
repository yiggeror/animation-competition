# 音效合成：全部用代码算（噪声、振荡器、共鸣滤波、粘滑摩擦），不用录音素材。
# 每个函数返回单声道 float32；长的环境声（虫鸣、蛙声、吊扇）按时长生成。
import numpy as np
from scipy import signal
from inst import SR, ns, secs, bp, lp, hp, peq, smooth_noise, modal

R = np.random.default_rng(7)


def norm(x, g=1.0):
    m = np.abs(x).max()
    return (x / m * g).astype(np.float32) if m > 0 else x.astype(np.float32)


def env_ar(n, a, r):
    t = secs(n); return np.clip(t / max(a, 1e-4), 0, 1) * np.exp(-t / max(r, 1e-4))


def burst(dur, lo, hi, a=0.001, r=0.02, g=1.0):
    n = ns(dur); return norm(bp(R.standard_normal(n), lo, hi) * env_ar(n, a, r), g)


# ================================================================ 夏夜环境
def crickets(dur, voices=5, seed=1):
    """蟋蟀：几只，各自的音高、节奏、声像；每声"唧"是 3～4 个 15 毫秒的小脉冲"""
    r = np.random.default_rng(seed); n = ns(dur)
    out = np.zeros((n, 2), np.float32)
    for v in range(voices):
        f = r.uniform(4200, 5600); rate = r.uniform(1.6, 2.6); p = r.uniform(-0.8, 0.8); g = r.uniform(0.3, 1.0)
        x = np.zeros(n); t = r.uniform(0, 1)
        pulse_n = ns(0.014); pt = secs(pulse_n); pulse = np.sin(2 * np.pi * f * pt) * np.sin(np.pi * pt / 0.014) ** 2
        while t < dur:
            k = r.integers(3, 5)
            for j in range(k):
                s = ns(t + j * 0.032)
                if s + pulse_n < n:
                    x[s:s + pulse_n] += pulse * (0.8 + 0.2 * r.random())
            t += 1 / rate * r.uniform(0.85, 1.15)
            if r.random() < 0.05:
                t += r.uniform(1, 3)          # 偶尔停一会儿
        th = (p + 1) * np.pi / 4
        out[:, 0] += x * np.cos(th) * g; out[:, 1] += x * np.sin(th) * g
    return out / voices


def cicadas(dur, seed=2):
    """蝉：一片持续的"知——"，高频的噪声按 150 Hz 左右的脉冲调制，慢慢起伏"""
    r = np.random.default_rng(seed); n = ns(dur); out = np.zeros((n, 2), np.float32)
    for v in range(3):
        nz = bp(r.standard_normal(n), 4300 + 600 * v, 7200 + 400 * v, 4)
        am = 0.55 + 0.45 * np.sin(2 * np.pi * r.uniform(140, 190) * secs(n)) ** 2
        sw = 0.5 + 0.5 * np.clip(smooth_noise(n, 0.15, seed + v) * 0.6 + 0.4, 0, 1)
        x = nz * am * sw
        p = [-0.6, 0.1, 0.7][v]; th = (p + 1) * np.pi / 4
        out[:, 0] += x * np.cos(th); out[:, 1] += x * np.sin(th)
    return out / np.abs(out).max()


def frogs(dur, rate=1.2, seed=3, far=False):
    """蛙声：一声"呱"是一串 50 Hz 左右的脉冲，去激励 500～900 Hz 的共鸣；很多只，此起彼伏"""
    r = np.random.default_rng(seed); n = ns(dur); out = np.zeros((n, 2), np.float32)
    t = 0.0
    while t < dur:
        cd = r.uniform(0.12, 0.28); cn = ns(cd); pr = r.uniform(38, 62)
        tt = secs(cn); tr = (np.sin(2 * np.pi * pr * tt) > 0.85).astype(float)
        fc = r.uniform(450, 950)
        b, a = signal.iirpeak(fc, 6, fs=SR); c = signal.lfilter(b, a, tr)
        b2, a2 = signal.iirpeak(fc * 2.1, 8, fs=SR); c += 0.4 * signal.lfilter(b2, a2, tr)
        c *= np.sin(np.pi * tt / cd) ** 0.6
        reps = r.integers(1, 4)
        p = r.uniform(-0.9, 0.9); th = (p + 1) * np.pi / 4; g = r.uniform(0.3, 1.0)
        for k in range(reps):
            s = ns(t + k * (cd + 0.06))
            if s + cn < n:
                out[s:s + cn, 0] += c * np.cos(th) * g; out[s:s + cn, 1] += c * np.sin(th) * g
        t += r.exponential(1 / rate)
    out = out / (np.abs(out).max() + 1e-9)
    if far:
        out = np.stack([lp(out[:, 0], 2500), lp(out[:, 1], 2500)], 1)
    return out.astype(np.float32)


def fan(dur, speed):
    """吊扇：speed(t) 0..1 的转速曲线。电机嗡声（100 Hz 及谐波，转速低时变弱）+ 三片扇叶切风的"呼呼"（叶片通过频率调制的低频噪声）+ 一点咔哒的松动声"""
    n = ns(dur); t = secs(n); sp = speed(t)
    hum = sum(np.sin(2 * np.pi * 100 * h * t) / h for h in (1, 2, 3)) * 0.15 * sp ** 1.5
    rev = np.cumsum(sp * 3.2) / SR            # 每秒最多约 3.2 转
    blade = 0.6 + 0.4 * np.cos(2 * np.pi * rev * 3) ** 2
    air = lp(R.standard_normal(n), 900) * blade * sp ** 1.2
    tick_n = ns(0.006); tick = bp(R.standard_normal(tick_n), 1500, 5000) * np.exp(-secs(tick_n) / 0.0015)
    ticks = np.zeros(n)
    k_prev = 0
    for i in np.nonzero(np.diff(np.floor(rev)) > 0)[0]:
        if i + tick_n < n:
            ticks[i:i + tick_n] += tick * 0.25 * sp[i]
    x = hum + air * 0.9 + ticks
    return norm(x, 0.9)


def tv_babble(dur, seed=5):
    """电视：隔着小喇叭的含糊人声（脉冲串 + 随时间变的共振峰 + 辅音噪声），再加一点背景音乐的感觉"""
    r = np.random.default_rng(seed); n = ns(dur); t = secs(n)
    # 语调：一句一句的，句间停顿
    f0 = 150 + 50 * smooth_noise(n, 3, seed) + 30 * np.sin(2 * np.pi * 0.4 * t)
    voiced = (smooth_noise(n, 2.5, seed + 1) > -0.4).astype(float)
    voiced = lp(voiced, 20)
    ph = np.cumsum(f0) / SR
    src = ((ph % 1) < 0.08).astype(float) * voiced
    # 元音：每 0.12～0.25 秒换一个
    VOW = [(700, 1200, 2600), (300, 2200, 3000), (450, 800, 2500), (350, 1700, 2600), (600, 1000, 2400)]
    out = np.zeros(n); s = 0
    while s < n:
        L = ns(r.uniform(0.11, 0.24)); e = min(n, s + L)
        v = VOW[r.integers(len(VOW))]
        seg = src[s:e]
        y = np.zeros(e - s)
        for fc, g in zip(v, (1, 0.6, 0.3)):
            b, a = signal.iirpeak(fc, 5, fs=SR); y += g * signal.lfilter(b, a, seg)
        if r.random() < 0.35:                     # 辅音：一小段噪声
            cn = min(e - s, ns(0.04)); y[:cn] += bp(r.standard_normal(cn), 2500, 6000) * 0.3 * voiced[s:s + cn]
        out[s:e] = y * np.hanning(e - s) ** 0.3
        s = e
    out = bp(out, 350, 3800)                      # 小喇叭
    return norm(out, 0.8)


def crt_whine(dur, f=15625):
    n = ns(dur); return (np.sin(2 * np.pi * f * secs(n)) * 0.05).astype(np.float32)


def tv_static(dur):
    n = ns(dur); return norm(bp(R.standard_normal(n), 800, 9000), 0.6)


# ================================================================ 开关、电器
def click(vel=0.8, f=2500, body=180):
    """开关 / 继电器的"啪"：一个很短的高频脉冲 + 一点低频的壳体声"""
    n = ns(0.08); t = secs(n)
    x = bp(R.standard_normal(n), f * 0.6, f * 2.5) * np.exp(-t / 0.0025)
    x += np.sin(2 * np.pi * body * t) * np.exp(-t / 0.02) * 0.4
    return norm(x, vel)


def power_cut():
    """停电"啪"：墙里的继电器跳一下 + 电视的"嘣"（显像管放电）"""
    a = click(1.0, 3000, 120); b = np.zeros(ns(0.6))
    t = secs(len(b)); b += np.sin(2 * np.pi * 60 * t) * np.exp(-t / 0.08) * 0.6 + bp(R.standard_normal(len(b)), 200, 3000) * np.exp(-t / 0.03) * 0.5
    b[:len(a)] += a
    return norm(b, 1.0)


def pull_cord():
    """拉线开关"咔—嗒"：往下拉一声，弹簧回去一声"""
    x = np.zeros(ns(0.4)); a = click(0.9, 2200, 300); b = click(0.6, 3200, 400)
    x[:len(a)] += a; s = ns(0.13); x[s:s + len(b)] += b
    x[ns(0.02):ns(0.02) + ns(0.1)] += bp(R.standard_normal(ns(0.1)), 3000, 8000) * 0.06
    return norm(x, 0.9)


def fluor_start(n_flicker=2):
    """日光灯启动：启辉器"嗒…嗒"，灯管"叮"一声亮起，然后是持续的 100 Hz 嗡嗡声（另给）"""
    x = np.zeros(ns(1.6))
    for k, t0 in enumerate([0.0, 0.45, 0.95][:n_flicker + 1]):
        c = click(0.6, 4000, 600); s = ns(t0); x[s:s + len(c)] += c
        z = ns(0.25); hum = np.sin(2 * np.pi * 100 * secs(z)) * np.exp(-secs(z) / 0.08) * 0.3
        x[s:s + z] += hum
    ping = modal([3100, 4800, 7400], [0.4, 0.25, 0.12], [1, 0.5, 0.3], 0.8)
    s = ns(0.95); x[s:s + len(ping)] += ping[:len(x) - s] * 0.5
    return norm(x, 0.8)


def fluor_hum(dur):
    n = ns(dur); t = secs(n)
    x = sum(np.sin(2 * np.pi * 100 * h * t + h) / h ** 1.3 for h in range(1, 12))
    x += bp(R.standard_normal(n), 3000, 8000) * 0.02
    return norm(x, 0.5)


def chime(freqs, step=0.22, dur=1.6):
    """手机提示音：柔和的电子"叮—咚"（正弦 + 一点三次谐波）"""
    x = np.zeros(ns(dur + step * len(freqs)))
    for k, f in enumerate(freqs):
        n = ns(dur); t = secs(n)
        y = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.1)) * np.exp(-t / 0.45) * np.clip(t / 0.004, 0, 1)
        s = ns(k * step); x[s:s + n] += y
    return norm(x, 0.7)


def phone_speaker(x):
    """手机小喇叭：只剩中高频"""
    return norm(bp(x, 900, 7000, 3), np.abs(x).max())


# ================================================================ 手里的东西
def plug(hard=False):
    """充电线插头：塑料摩擦一下，"咔"地插进去"""
    x = np.zeros(ns(0.3))
    rub = bp(R.standard_normal(ns(0.12)), 1500, 6000) * np.hanning(ns(0.12)) * (0.3 if not hard else 0.2)
    x[:len(rub)] += rub
    c = click(1.0 if hard else 0.6, 2800, 250 if hard else 400); s = ns(0.11); x[s:s + len(c)] += c
    return norm(x, 1.0 if hard else 0.6)


def stick_slip(dur, rate_lo, rate_hi, f_lo, f_hi, seed=0):
    """粘滑摩擦（木头吱呀、凳子拖地）：一串间隔不匀的小冲击，去激励共鸣"""
    r = np.random.default_rng(seed); n = ns(dur); x = np.zeros(n)
    rate = rate_lo + (rate_hi - rate_lo) * (0.5 + 0.5 * smooth_noise(n, 3, seed))
    ph = np.cumsum(rate) / SR
    idx = np.nonzero(np.diff(np.floor(ph)) > 0)[0]
    x[idx] = r.uniform(0.5, 1.0, len(idx))
    y = np.zeros(n)
    for fc in (f_lo, (f_lo * f_hi) ** 0.5, f_hi):
        b, a = signal.iirpeak(fc, 12, fs=SR); y += signal.lfilter(b, a, x)
    return norm(y * np.hanning(n) ** 0.3, 0.8)


def creak(dur=0.8, seed=0):
    """木箱盖 / 立柜门的"吱——" """
    return stick_slip(dur, 60, 180, 600, 2400, seed)


def scrape(dur=1.2, seed=1):
    """板凳在水泥地上拖"""
    x = stick_slip(dur, 25, 70, 300, 1500, seed) + norm(bp(R.standard_normal(ns(dur)), 400, 3000), 0.3) * np.hanning(ns(dur))
    return norm(x, 0.8)


def thud(vel=0.8, f=90, dec=0.12, bright=1200):
    """闷响：东西放下、人倒在竹席上"""
    n = ns(0.5); t = secs(n)
    x = np.sin(2 * np.pi * np.cumsum(f + 60 * np.exp(-t / 0.02)) / SR) * np.exp(-t / dec)
    x += lp(R.standard_normal(n), bright) * np.exp(-t / 0.03) * 0.6
    return norm(x, vel)


def bamboo_mat(dur=0.6, seed=2):
    """竹席被压的"咯吱、噼啪"（一串细碎的小脆响）"""
    r = np.random.default_rng(seed); n = ns(dur); x = np.zeros(n)
    for _ in range(int(dur * 40)):
        s = r.integers(0, n - ns(0.01)); c = bp(r.standard_normal(ns(0.01)), 2000, 7000) * np.exp(-secs(ns(0.01)) / 0.0015)
        x[s:s + len(c)] += c * r.uniform(0.2, 1) * np.exp(-s / n * 2)
    return norm(x, 0.6)


def rustle(dur=1.0, seed=3, lo=1500, hi=8000, density=1.0):
    """布料窸窣：一阵一阵的噪声"""
    n = ns(dur); e = np.clip(smooth_noise(n, 14 * density, seed), 0, None) ** 1.5 * np.hanning(n) ** 0.5
    return norm(bp(R.standard_normal(n), lo, hi) * e, 0.6)


def leather(dur=0.5, seed=4):
    """皮影的牛皮沙沙声：细碎、脆"""
    r = np.random.default_rng(seed); n = ns(dur); x = np.zeros(n)
    for _ in range(int(dur * 120)):
        s = r.integers(0, max(1, n - ns(0.004))); c = r.standard_normal(ns(0.004)) * np.exp(-secs(ns(0.004)) / 0.0008)
        x[s:s + len(c)] += c * r.uniform(0.1, 1)
    x = bp(x, 2500, 10000)
    return norm(x * np.hanning(n) ** 0.4, 0.5)


def rod_tap(vel=0.5):
    """竹签轻碰一下"""
    return norm(modal([1900, 3300, 5200], [0.03, 0.02, 0.01], [1, 0.5, 0.3], 0.12) + burst(0.12, 2000, 8000, r=0.002, g=0.3), vel)


def sheet_pat(vel=0.4):
    """皮影轻轻拍在床单上：软的"噗" """
    n = ns(0.15); t = secs(n)
    return norm(lp(R.standard_normal(n), 900) * np.exp(-t / 0.02), vel)


def match_strike():
    """划火柴：擦（0.15 秒的粗糙摩擦）→ "嚓"地着了（亮的爆燃 + 呼的一下）→ 小火苗的嘶嘶声"""
    x = np.zeros(ns(2.0))
    sc = stick_slip(0.16, 300, 700, 1500, 5000, 9) * 0.7 + norm(bp(R.standard_normal(ns(0.16)), 2000, 9000), 0.4) * np.hanning(ns(0.16))
    x[:len(sc)] += sc
    s = ns(0.15); n = ns(0.5); t = secs(n)
    flare = bp(R.standard_normal(n), 800, 9000) * np.exp(-t / 0.08) * 1.2 + lp(R.standard_normal(n), 400) * np.exp(-t / 0.2) * 0.8
    x[s:s + n] += flare
    s2 = ns(0.4); n2 = len(x) - s2
    x[s2:] += bp(R.standard_normal(n2), 1500, 6000) * 0.06 * np.exp(-secs(n2) / 1.2)
    return norm(x, 0.9)


def flame(dur, seed=6):
    """马灯的火苗：很轻的呼呼声 + 偶尔"噼啪" """
    r = np.random.default_rng(seed); n = ns(dur)
    x = lp(R.standard_normal(n), 500) * 0.25 * (1 + 0.3 * smooth_noise(n, 2, seed))
    for _ in range(int(dur * 0.8)):
        s = r.integers(0, n - ns(0.01)); c = bp(r.standard_normal(ns(0.01)), 1500, 7000) * np.exp(-secs(ns(0.01)) / 0.002)
        x[s:s + len(c)] += c * r.uniform(0.3, 1)
    return norm(x, 0.5)


def glass_clink(vel=0.5):
    """灯罩放下：玻璃轻碰铁丝架"""
    return norm(modal([2650, 4100, 6300, 8100], [0.25, 0.18, 0.1, 0.06], [1, 0.6, 0.4, 0.2], 0.6), vel)


def metal_clink(vel=0.5):
    """铁丝、挂钩、箱扣"""
    return norm(modal([1800, 2950, 4400, 6100], [0.12, 0.08, 0.05, 0.03], [1, 0.6, 0.4, 0.2], 0.3), vel)


def flashlight_click(vel=0.7):
    return norm(click(vel, 3500, 500), vel)


def flashlight_slap(vel=0.8):
    """拍手电：手掌拍在金属筒上（闷响 + 一点金属余音）"""
    a = thud(vel, 160, 0.04, 2500); m = modal([2200, 3700], [0.08, 0.05], [1, 0.5], 0.2) * 0.25
    a[:len(m)] += m
    return norm(a, vel)


def drawer(dur=0.5, seed=8):
    """抽屉拉开：木头摩擦 + 里面的东西哗啦一下"""
    x = stick_slip(dur, 40, 90, 400, 1800, seed) * 0.7
    for k in range(6):
        s = ns(R.uniform(0.1, dur)); c = modal([R.uniform(1500, 4000)], [0.03], [1], 0.06)
        x[s:s + len(c)] += c[:len(x) - s] * 0.3
    return norm(x, 0.7)


def clothespin(vel=0.6):
    """塑料衣夹夹上去"""
    return norm(click(vel, 2400, 700) + burst(0.08, 1000, 4000, r=0.006, g=0.3), vel)


def beans(dur, rate=1.2, seed=10):
    """剥毛豆：豆荚"啪"地掰开 + 豆子落进搪瓷盆"叮叮" """
    r = np.random.default_rng(seed); n = ns(dur); x = np.zeros(n); t = r.uniform(0.2, 0.8)
    while t < dur - 0.5:
        s = ns(t); c = burst(0.03, 1500, 5000, r=0.004, g=0.5); x[s:s + len(c)] += c
        for k in range(r.integers(2, 4)):
            s2 = ns(t + 0.15 + k * r.uniform(0.05, 0.1))
            pg = modal([r.uniform(2300, 3600), r.uniform(5000, 6500)], [0.12, 0.06], [1, 0.4], 0.25) * r.uniform(0.15, 0.35)
            if s2 + len(pg) < n:
                x[s2:s2 + len(pg)] += pg
        t += 1 / rate * r.uniform(0.7, 1.4)
    return norm(x, 0.6)


def footsteps(times, vel=0.4, seed=11):
    """拖鞋走在水泥地上（软的"嚓"）"""
    n = ns(max(times) + 0.5); x = np.zeros(n); r = np.random.default_rng(seed)
    for t in times:
        c = norm(bp(r.standard_normal(ns(0.12)), 300, 3000) * env_ar(ns(0.12), 0.01, 0.03), vel * r.uniform(0.7, 1))
        s = ns(t); x[s:s + len(c)] += c
    return x.astype(np.float32)


def fan_hand(dur, rate=1.4, seed=12):
    """蒲扇扇风：一下一下的"呼" """
    n = ns(dur); t = secs(n)
    e = np.maximum(0, np.sin(2 * np.pi * rate * t)) ** 2
    return norm(lp(R.standard_normal(n), 1200) * e, 0.4)
