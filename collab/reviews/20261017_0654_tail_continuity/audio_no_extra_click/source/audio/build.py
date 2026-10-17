# 全片声音：按剪辑表（js/film/edl.js）把环境声、音效、配乐放到每个镜头的时间上，混成一条立体声。
# 运行：python3 audio/build.py  → build/audio/film_mix.wav（以及分轨 build/audio/stem_*.wav）
# 时间都写成"镜头号 + 镜头内的秒数"，剪辑表改了时长会自动跟着走。镜头里的动作时间来自各镜头模块（注释里写了出处）。
#
# 音乐的走向（简报"声音与配乐"）：
#   第 1–5 场：没有配乐，只有环境声和手机游戏的 8-bit 小曲（手机喇叭里出来的，是剧中声音）
#   第 4 场木箱：扬琴轻轻两个音"叮—咚"（主题的头两个音，先埋一下）
#   第 6 场：开场锣鼓 → "呛" → 板胡奏主题（鹤昂首时进主题）
#   第 7 场：乌龟的低音拨弦步子；啄空、撞壳（大锣）、晕（板胡大滑音）、乌龟偷笑（笛子颤音）
#   第 8 场：上手——节奏绊跟头、乌龟翻肚皮、奶奶笑；影子忽大忽小；手把手时只剩笛子慢慢吹；咬嘴"呛"
#   第 9 场：小狗——8-bit 方波 + 电子鼓 + 板胡、梆子一起，越来越快（和画面的 tempo(t) 同步）
#   第 10 场：来电，音乐整段停；只剩一串电器的声音。手机开机提示音就是主题的"叮—咚"
#   第 12 场：关灯，安静；旋律先由笛子轻轻地回来，再完整地回来
#   第 13 场 + 字幕：完整的主题，最后扬琴"叮—咚"、一声梆子收
import sys, os, json, subprocess
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(__file__))
from inst import *
import inst
from sfx import *
from score import *

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'build', 'audio')
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- 剪辑表
shots = json.loads(subprocess.check_output(['node', '-e', "import('./js/film/edl.js').then(m=>console.log(JSON.stringify(m.SHOTS)))"], cwd=ROOT))
START = {}; t = 0.0
for s in shots:
    START[s['id']] = t; t += s['dur']
TOTAL = t + 1.0
N = ns(TOTAL)


def T(sid, off=0.0):
    return START[sid] + off


# ---------------------------------------------------------------- 轨道
MUS = {k: np.zeros(N, np.float32) for k in ['banhu', 'dizi', 'yq', 'pipa', 'perc', 'chip', 'beat']}
SFX = np.zeros((N, 2), np.float32)       # 屋里的音效（立体声，带声像）
AMB = np.zeros((N, 2), np.float32)       # 环境声


def sfx(clip, t, gain=1.0, p=0.0):
    if clip.ndim == 1:
        clip = pan(clip, p)
    s = ns(t)
    if s >= N:
        return
    e = min(N, s + len(clip)); SFX[s:e] += clip[:e - s] * gain


def gain_curve(points, n=N):
    """[(时间, dB)] → 每个采样的增益（线性插值 dB）"""
    ts = np.array([p[0] for p in points]); db = np.array([p[1] for p in points])
    tt = secs(n)
    return (10 ** (np.interp(tt, ts, db) / 20)).astype(np.float32)


# ---------------------------------------------------------------- 旋律：按乐句分段合成（每段单独算，省内存）
LINES = {'banhu': [], 'dizi': []}


def melody(inst_name, notes, gain=1.0):
    LINES[inst_name].append((notes, gain))


def render_lines():
    for name, phrases in LINES.items():
        fn = banhu if name == 'banhu' else dizi
        for notes, g in phrases:
            t0 = min(n['t'] for n in notes) - 0.2; t1 = max(n['t'] + n['d'] for n in notes) + 0.6
            loc = [dict(n, t=n['t'] - t0) for n in notes]
            y = fn(loc, t1 - t0)
            place(MUS[name], y, t0, g)


def mel(text, t0, bpm, key=587.33, oct=0, gap=0.02, acc=0.75, beats_from=0, beats_to=1e9):
    seq, nb = parse(text, key, oct)
    seq = [(b - beats_from, d, f, fl) for b, d, f, fl in seq if beats_from <= b < beats_to]
    return to_notes(seq, t0, bpm, gap, acc)


def yq_chords(t0, roots, bpm, bars, g=0.5, key=587.33, pattern='offbeat'):
    sp = 60 / bpm
    for b in range(bars):
        r = roots[b % len(roots)]; tb = t0 + b * 2 * sp
        place(MUS['yq'], yangqin(jp(r, -1, key), 2.0, 0.8), tb, g)
        if pattern == 'offbeat':
            for off in (0.5, 1.5):
                place(MUS['yq'], yangqin(jp(r, 0, key), 1.0, 0.6), tb + off * sp, g * 0.7)
                place(MUS['yq'], yangqin(jp(r, 0, key) * 1.5, 1.0, 0.5), tb + off * sp + 0.008, g * 0.45)
        elif pattern == 'arp':
            for k, (d, o) in enumerate([(1, 0), (5, 0), (1, 1), (5, 0)]):
                place(MUS['yq'], yangqin(jp(r, o, key) * (1.5 if d == 5 else 1), 1.2, 0.5), tb + k * sp / 2, g * 0.55)


def bangzi_beats(t0, bpm, beats, g=0.5, every=1.0, accent_bar=True):
    sp = 60 / bpm; b = 0.0
    while b < beats - 1e-6:
        strong = accent_bar and (b % 2 == 0)
        place(MUS['perc'], bangzi(0.9 if strong else 0.6), t0 + b * sp, g * (1 if strong else 0.65))
        b += every


THEME_ROOTS = THEME_A_ROOTS
D5 = 587.33

# ================================================================ 环境声（整片）
print('环境声…')
amb_len = TOTAL
cr = crickets(amb_len, 6, seed=1); fr = frogs(amb_len, 1.1, seed=3); ci = cicadas(amb_len, seed=2)
# 停电以后屋里静了，虫子显得更响；音乐进来时压低；来电时被电器盖住；关灯后又回来
CUT = T('S04', 0.6); ON = T('S27', 0.0); OFF = T('S30', 6.0)
insects_db = [(0, -14), (CUT, -14), (CUT + 1.5, -8), (T('S15'), -8), (T('S15', 3), -15), (ON - 0.01, -15), (ON, -24),
              (OFF, -24), (OFF + 2, -7), (T('S31', 2), -9), (T('S31', 6), -15), (T('S32'), -10), (T('END'), -14), (TOTAL, -30)]
g_ins = gain_curve(insects_db)[:, None]
AMB += cr * g_ins * 1.0 + fr * g_ins * 0.55 + ci * g_ins * 0.18
# 吊扇独立开关：开场转着；停电后慢慢停；来电后转起来；第12场只关电视和日光灯，吊扇继续转。
FAN_ON = T('S28', 0.2)


def fan_speed(tt):
    s = np.where(tt < CUT, 1.0, np.exp(-(tt - CUT) / 2.2))
    s = np.where(tt >= FAN_ON, 1 - np.exp(-(tt - FAN_ON) / 1.6), s)
    return np.clip(s, 0, 1)


fan_x = fan(TOTAL, fan_speed)
fan_db = [(0, -22), (T('S02'), -27), (T('S03'), -22), (CUT + 5, -22), (TOTAL, -22)]
AMB += pan(fan_x * gain_curve(fan_db), 0.0)
# 日光灯的嗡声：开场亮着，停电灭；来电亮，关灯灭
hum = fluor_hum(TOTAL)
hum_g = np.zeros(N, np.float32)
hum_g[:ns(CUT)] = 1; hum_g[ns(T('S27', 0.52)):ns(OFF)] = 1.3
AMB += pan(hum * hum_g * 10 ** (-30 / 20), 0.2)
# 电视：第12场先按掉电视，再走向门边拉灯绳；TV_OFF与S30开头CRT特写同步。
TV_ON = T('S28', 1.4)
TV_OFF = T('S30', 1.1)
tvb = tv_babble(TOTAL)
tv_g = np.zeros(N, np.float32); tv_g[:ns(CUT)] = 1; tv_g[ns(TV_ON + 0.9):ns(TV_OFF)] = 1
tv_g *= gain_curve([(0, -20), (T('S02'), -27), (T('S03'), -21), (TOTAL, -21)])
AMB += pan(tvb * tv_g, -0.55)
whine = crt_whine(TOTAL)
wg = np.zeros(N, np.float32); wg[:ns(CUT)] = 1; wg[ns(TV_ON):ns(TV_OFF)] = 1
wg[ns(TV_OFF):ns(TV_OFF + 0.3)] = np.linspace(1, 0, ns(TV_OFF + 0.3) - ns(TV_OFF))
AMB += pan(whine * wg * 0.25, -0.55)
# 马灯火苗：点着以后一直在（近景响一点）
LAMP = T('S08', 1.8)   # 灯芯着了
fl = flame(TOTAL - LAMP)
s0 = ns(LAMP)
flg = gain_curve([(0, -26), (T('S08', 4), -18), (T('S09'), -28), (T('S12'), -24), (T('S13'), -30), (ON, -40), (OFF + 1, -28), (TOTAL, -28)])[s0:s0 + len(fl)]   # 曲线是全片时间，截出灯亮以后的一段
fl = fl[:len(flg)]; AMB[s0:s0 + len(fl)] += pan(fl * flg, 0.3)

# ================================================================ 第 1–5 场：手机游戏、剥毛豆、停电
print('第 1–5 场…')
# 手机游戏的 8-bit 小曲（剧中声音，从手机小喇叭出来）：一段 2 小节的跳跃短句循环
GAME = "5:0.25 5:0.25 1':0.25 5:0.25 6:0.25 5:0.25 3:0.25 5:0.25 | 2:0.25 2:0.25 5:0.25 2:0.25 3:0.25 2:0.25 1:0.25 2:0.25"
GAME_END = T('S05', 3.05)   # 屏幕黑掉


def game_music(t0, t1):
    seq, nb = parse(GAME, key=D5, oct=1)
    sp = 60 / 150; notes = []; tb = t0
    while tb < t1:
        for b, d, f, fl in seq:
            tt = tb + b * sp
            if tt < t1:
                notes.append({'t': tt - t0, 'd': min(d * sp, t1 - tt), 'f': f, 'acc': 0.7})
        tb += nb * sp
    bass = []
    tb = t0
    while tb < t1:
        for k, r in enumerate([1, 1, 5, 5]):
            tt = tb + k * sp
            if tt < t1:
                bass.append({'t': tt - t0, 'd': min(sp, t1 - tt), 'f': jp(r, -2, D5), 'acc': 0.8})
        tb += 4 * sp
    y = chip_lead(notes, t1 - t0, 0.5) + chip_tri(bass, t1 - t0) * 0.7
    return phone_speaker(y)


gm = game_music(0, GAME_END)
gm_db = [(0, -30), (T('S02') - 0.01, -30), (T('S02'), -17), (T('S03'), -31), (CUT, -31), (CUT + 0.5, -27), (T('S05'), -18), (TOTAL, -18)]
s0 = 0; SFX[:len(gm)] += pan(gm * gain_curve(gm_db, len(gm)), -0.1)


def jump_snd():
    n = ns(0.18); f = 300 + 900 * secs(n) / 0.18
    return phone_speaker(inst._bl_pulse(f, n, 0.5) * np.exp(-secs(n) / 0.12))


def coin_snd():
    n = ns(0.25); f = np.where(secs(n) < 0.06, 1318.5, 1760.0)
    return phone_speaker(inst._bl_pulse(f, n, 0.5) * np.exp(-secs(n) / 0.1))


for p in [0.45, 1.35, 2.2, 3.05]:                           # js/code/s02.js PRESS
    sfx(jump_snd(), T('S02', p), 0.12); sfx(coin_snd(), T('S02', p + 0.3), 0.08)
for k in range(4):                                         # 远景里偶尔听到的跳、金币
    sfx(jump_snd(), T('S01', 1.5 + k * 2.6), 0.03, -0.2)
MASH = []; p = 1.15
while p < 3.0:
    MASH.append(p); p += 0.14 + 0.03 * np.sin(p * 13)       # js/code/s05.js MASH
for i, p in enumerate(MASH):
    if i % 3 == 0:
        sfx(jump_snd(), T('S05', p), 0.10)
sfx(click(0.25, 4500, 900), T('S05', 0.35), 0.4)          # 断开充电的小"嘀"（闪电消失）
for p in [3.4, 3.72]:
    sfx(click(0.2, 1800, 300), T('S05', p), 0.25)          # 黑屏后拇指戳屏幕
# 剥毛豆（奶奶，右边）、推西瓜
sfx(beans(T('S01', 12), 0.9, 10), T('S01', 0), 0.10, 0.45)
sfx(beans(6, 1.1, 11), T('S03', 0), 0.22, 0.2)
sfx(rustle(0.5, 21, 600, 4000), T('S03', 3.8), 0.15, 0.1)  # 咬西瓜（脆的、湿的一下）
sfx(burst(0.12, 1500, 6000, r=0.03, g=0.5), T('S03', 4.0), 0.25, 0.1)
# 停电：继电器"啪"、电视"嘣"
sfx(power_cut(), CUT, 0.7, -0.3)

# ================================================================ 第 2–5 场：插头、倒下、找灯、划火柴、手电、木箱、搭台（屋内镜头的动作按这些时间来做）
print('屋内音效…')
for t0, hard in [(1.0, False), (1.8, False), (3.0, False), (3.9, False), (6.4, True)]:
    sfx(plug(hard), T('S06', t0), 0.6 if hard else 0.4, 0.15)
sfx(lp(R.standard_normal(ns(0.35)), 1500).astype(np.float32) * np.hanning(ns(0.35)).astype(np.float32) * 0.3, T('S06', 3.4), 0.5, 0.15)   # 吹一口插头（脸在画外）
sfx(thud(0.9, 80, 0.15, 900), T('S07', 0.4), 0.5, -0.1); sfx(bamboo_mat(0.7), T('S07', 0.42), 0.4, -0.1)
sfx(fan_hand(3.5, 1.3), T('S07', 1.2), 0.25, -0.1)
sfx(scrape(0.3, 4), T('S07', 1.4), 0.2, 0.4)              # 奶奶起身，凳子挪一下
sfx(footsteps([0, 0.55, 1.1, 1.65, 2.2]), T('S07', 1.9), 0.35, 0.5)
sfx(creak(0.4, 5), T('S07', 4.3), 0.15, 0.6); sfx(metal_clink(0.5), T('S07', 4.6), 0.3, 0.6)
# js/code/s08.js：0.35 划火柴，1.8 灯芯着了，2.2 甩灭火柴，3.4 放下灯罩
sfx(match_strike(), T('S08', 0.2), 0.7, -0.15)
sfx(burst(0.4, 300, 3000, a=0.05, r=0.15, g=0.4), T('S08', 1.8), 0.4, 0.05)   # 灯芯着了
sfx(burst(0.25, 200, 1500, a=0.02, r=0.08, g=0.25), T('S08', 2.2), 0.3, 0.2)  # 甩灭火柴的"呼"
sfx(glass_clink(0.6), T('S08', 3.4), 0.4, 0.05)            # 放下灯罩
# js/paint/shots/s09.js：开镜时手电已经在手里（抽屉在上一镜之间翻过了）；1.6 推开关不亮，2.1、2.5 往手心磕，2.9 推亮
sfx(flashlight_click(), T('S09', 1.6), 0.4, -0.3)
sfx(flashlight_slap(), T('S09', 2.1), 0.45, -0.3); sfx(flashlight_slap(0.9), T('S09', 2.5), 0.5, -0.3)
sfx(flashlight_click(0.8), T('S09', 2.9), 0.45, -0.3)
# S31 手电从木箱拿起时就一直亮着；开镜直接照下巴，不增加推开关的 click。
# js/code/s12.js：0～0.9 箱盖开到底，1.5 手伸进来碰到布，2.4～4.0 握住签子把鹤立起来
# js/paint/shots/s12.js：开镜时箱盖已经开着（奶奶两只手都握着签子），没有开盖声
sfx(rustle(1.0, 23, 800, 5000), T('S12', 1.5), 0.3, 0.1)
sfx(leather(1.4, 24), T('S12', 2.4), 0.35, 0.1)           # 拿起鹤，牛皮沙沙
sfx(rustle(1.6, 25, 300, 2500, 0.6), T('S14', 0.5), 0.35, 0.0)   # 床单抖开
sfx(metal_clink(0.4), T('S14', 1.0), 0.25, 0.0)           # 铁丝晃
for k, t0 in enumerate([2.5, 3.2, 3.9]):
    sfx(clothespin(), T('S14', t0), 0.35, -0.2 + 0.2 * k)
sfx(metal_clink(0.6), T('S14', 5.0), 0.3, 0.3)            # 马灯挂上钩
sfx(scrape(1.2, 7), T('S14', 6.5), 0.35, -0.4); sfx(thud(0.6, 120, 0.06, 2000), T('S14', 7.8), 0.4, -0.4)
sfx(rustle(0.5, 26, 1000, 5000), T('S14', 8.5), 0.2, -0.4)   # 抱起胳膊
# 第 4 场木箱：奶奶把鹤举到马灯前，彩色光斑落下——扬琴很轻的"叮—咚"（主题头两个音，先埋一下）
place(MUS['yq'], yangqin(jp(1, 1, D5), 3.0, 0.5), T('S12', 4.6), 0.5)
place(MUS['yq'], yangqin(jp(5, 0, D5), 3.0, 0.5), T('S12', 5.0), 0.42)

# ================================================================ 第 6 场：开演（S15、S16）
print('第 6 场…')
BPM = 120; SP = 0.5
# 开场锣鼓：鹤从远处贴近床单的 3 秒里，板鼓越敲越密，小锣跟进，贴上床单时"呛"
t0 = T('S15'); tt = t0 + 0.2; gap = 0.34
while tt < t0 + 2.85:
    place(MUS['perc'], bangu(0.4 + 0.5 * (tt - t0) / 2.9), tt, 0.5); tt += gap; gap = max(0.055, gap * 0.87)
for k, x in enumerate([1.4, 2.0, 2.4]):
    place(MUS['perc'], xiaoluo(0.5 + 0.1 * k), t0 + x, 0.4)
place(MUS['perc'], qiang(0.9), t0 + 3.0, 0.75)
# 两拍梆子垫一下，鹤开始昂首（js/lamp/s06_key.js raiseAt：亮相后 1.0 秒起）时主题进来
bangzi_beats(t0 + 3.0, BPM, 2, 0.5)
TH = t0 + 4.0
melody('banhu', mel(THEME_A, TH, BPM, D5), 0.55)
yq_chords(TH, THEME_ROOTS, BPM, 8, 0.4)
bangzi_beats(TH, BPM, 16, 0.4)
place(MUS['perc'], xiaoluo(0.6), TH + 1.0, 0.35)          # 昂首到顶，"台"
# S16：主题第二遍在笛子上（鹤踱步、梳毛），最后两小节啄水——琵琶往下拨两下 + 梆子
TH2 = TH + 16 * SP
melody('dizi', mel(THEME_A_DIZI, TH2, BPM, D5), 0.5)
yq_chords(TH2, THEME_ROOTS, BPM, 8, 0.3)
bangzi_beats(TH2, BPM, 12, 0.3)
peck = T('S16', 6.5)                                       # js/lamp/shots/s16.js：6.0～6.5 低头啄
for k, d in enumerate([5, 3, 1]):
    place(MUS['pipa'], pipa(jp(d, 0, D5), 0.8, 0.7), peck - 0.25 + k * 0.12, 0.4)
place(MUS['perc'], bangzi(1.0, 1.15), peck, 0.5)

# ================================================================ 第 7 场：乌龟（S17）
print('第 7 场…')
t0 = T('S17')
# 乌龟的步子：低音拨弦"噔—噔—"（乌龟每秒两步，js/lamp/shots/s17.js turtlePose speed 1.0）
for k in range(10):
    place(MUS['pipa'], pipa(jp([1, 5][k % 2], -2, D5), 0.7, 0.9), t0 + 0.25 + k * 0.5, 0.45)
    if k % 2 == 1:
        place(MUS['perc'], bangzi(0.5, 0.8), t0 + 0.25 + k * 0.5, 0.2)
# 鹤发现了（2.8～4.2 秒低头看）：板胡"嗯？"一个往上挑的滑音
melody('banhu', [{'t': t0 + 3.0, 'd': 0.4, 'f': jp(3, 0, D5), 'acc': 0.6}, {'t': t0 + 3.4, 'd': 0.7, 'f': jp(5, 0, D5), 'acc': 0.75, 'slide': 0.25, 'legato': True, 'vib': 1.5}], 0.5)
# 第一啄（5.5 秒起，乌龟 5.75 缩头）：板胡往下扑一个音，小锣"台"，然后空一拍
melody('banhu', [{'t': t0 + 5.45, 'd': 0.3, 'f': jp(1, 1, D5), 'acc': 0.9, 'grace': jp(2, 1, D5)}, {'t': t0 + 5.75, 'd': 0.25, 'f': jp(5, 0, D5), 'acc': 0.8, 'slide': 0.08, 'legato': True}], 0.5)
place(MUS['perc'], xiaoluo(0.7), t0 + 5.85, 0.4)
# 乌龟又探出头（7.3～7.8）：笛子"嘀嘀"两声
melody('dizi', [{'t': t0 + 7.35, 'd': 0.12, 'f': jp(6, 1, D5), 'acc': 0.6}, {'t': t0 + 7.55, 'd': 0.2, 'f': jp(5, 1, D5), 'acc': 0.6}], 0.35)
# 第二啄撞在龟壳上（8.5 秒）："咣"（大锣 + 钹）
HIT = t0 + 8.5
place(MUS['perc'], daluo(1.0, 3.5), HIT, 0.8); place(MUS['perc'], bo(0.9), HIT, 0.4)
sfx(thud(0.9, 220, 0.05, 3000), HIT, 0.5, 0.2)
# 晕（8.6～12.4）：板胡大滑音一上一下，小锣闷着敲，像天旋地转
wob = []
for k in range(5):
    tk = HIT + 0.4 + k * 0.75
    wob.append({'t': tk, 'd': 0.375, 'f': jp(5, 0, D5) * 2 ** (-k / 24), 'acc': 0.75 - 0.08 * k, 'slide': 0.3, 'legato': k > 0, 'vib': 3})
    wob.append({'t': tk + 0.375, 'd': 0.375, 'f': jp(2, 0, D5) * 2 ** (-k / 24), 'acc': 0.7 - 0.08 * k, 'slide': 0.3, 'legato': True, 'vib': 3})
melody('banhu', wob, 0.5)
for k in range(4):
    place(MUS['perc'], xiaoluo(0.35), HIT + 0.8 + k * 0.75, 0.25)
# 乌龟慢慢探出头、一颤一颤地偷笑（11.5～12.6）：笛子颤音 + 几个碎音
melody('dizi', [{'t': t0 + 11.6, 'd': 0.8, 'f': jp(3, 1, D5), 'acc': 0.6, 'trill': jp(5, 1, D5)},
                {'t': t0 + 12.5, 'd': 0.15, 'f': jp(2, 1, D5), 'acc': 0.6}, {'t': t0 + 12.7, 'd': 0.15, 'f': jp(1, 1, D5), 'acc': 0.6},
                {'t': t0 + 12.9, 'd': 0.5, 'f': jp(6, 0, D5), 'acc': 0.6}], 0.4)
place(MUS['pipa'], pipa(jp(1, -1, D5), 1.0, 0.8), t0 + 13.4, 0.4); place(MUS['perc'], bangzi(0.8), t0 + 13.4, 0.35)
for t in [t0 + 5.6, HIT - 0.05]:
    sfx(leather(0.3, int(t)), t, 0.2, -0.1)

# ================================================================ 第 7、8 场：小满笑（S18）、上手（S20–S23）
print('第 8 场…')
place(MUS['pipa'], pipa(jp(5, 0, D5), 0.6, 0.6), T('S18', 0.6), 0.35)   # "噗"
# S20 后台：奶奶把乌龟递过去（拨弦主题碎片）→ 签子缠在一起（扬琴乱了拍子的音簇）→ 乌龟翻肚皮（板胡往下滚）→ 奶奶笑弯腰（笛子颤音 + 梆子碎敲）
t0 = T('S20')
for k, (d, o, x) in enumerate([(1, 1, 0.3), (5, 0, 0.55), (6, 0, 0.8), (1, 1, 0.92), (6, 0, 1.05), (5, 0, 1.17)]):
    place(MUS['pipa'], pipa(jp(d, o, D5), 0.7, 0.6), t0 + x, 0.35)
for k, x in enumerate([2.6, 3.05, 3.2, 3.75, 4.3, 4.45]):
    place(MUS['yq'], yangqin(jp([2, 4, 7, 3, 6, 4][k], 0, D5, alt=[0, 0, -1, 0, 0, 1][k]), 0.9, 0.6), t0 + x, 0.3)
    sfx(rod_tap(0.5), t0 + x + 0.02, 0.3, 0.2)
flip = t0 + 5.5
melody('banhu', [{'t': flip - 0.4 + k * 0.1, 'd': 0.1, 'f': jp(1, 1, D5) * 2 ** (-k / 12 * 2.4), 'acc': 0.8, 'legato': k > 0, 'slide': 0.06} for k in range(5)], 0.45)
sfx(thud(0.6, 140, 0.05, 2500), flip + 0.1, 0.35, 0.2); place(MUS['perc'], xiaoluo(0.5), flip + 0.1, 0.3)
melody('dizi', [{'t': flip + 0.8, 'd': 1.2, 'f': jp(5, 1, D5), 'acc': 0.6, 'trill': jp(6, 1, D5)}, {'t': flip + 2.1, 'd': 0.9, 'f': jp(3, 1, D5), 'acc': 0.55, 'trill': jp(5, 1, D5)}], 0.35)
for k in range(8):
    place(MUS['perc'], bangzi(0.6), flip + 0.9 + k * 0.25, 0.22)
# S21：乌龟的影子忽大忽小（js/lamp/shots/s21.js d(t)），鹤笑得前仰后合（sin(8.5t)）：板胡奏主题头两小节，音量跟着影子大小走；
# 鹤每仰一次，笛子"哈"一个小滑音
t0 = T('S21')
th = mel(THEME_A, t0 + 0.3, 120, D5, beats_to=8)
for n_ in th:
    tl = n_['t'] - t0; d = 0.004 + 0.24 * max(0, np.sin(tl * 2.3) * np.sin(tl * 1.1 + 0.6))
    n_['acc'] = 0.45 + 1.6 * d
melody('banhu', th, 0.5)
for k in range(7):
    tp = t0 + (np.pi / 2 + 2 * np.pi * k) / 8.5
    if tp < t0 + 5.8:
        melody('dizi', [{'t': tp - 0.05, 'd': 0.18, 'f': jp(6, 1, D5), 'acc': 0.55, 'slide': 0.0}, {'t': tp + 0.13, 'd': 0.2, 'f': jp(3, 1, D5), 'acc': 0.5, 'slide': 0.12, 'legato': True}], 0.3)
yq_chords(t0 + 0.3, [1, 6, 1], 120, 3, 0.25)
# S22：奶奶从后面握住小满的手——只剩笛子，慢一半，主题前两小节；乌龟一步一步爬起来，每步一个低音拨弦
t0 = T('S22')
melody('dizi', mel(THEME_A, t0 + 0.4, 60, D5, beats_to=4, gap=0.03, acc=0.55), 0.45)
for k in range(4):                                         # js/code/s22.js：手握住以后，1.4 秒起每秒一步
    place(MUS['pipa'], pipa(jp([1, 2, 3, 5][k], -1, D5), 0.9, 0.5), t0 + 1.4 + k * 1.0, 0.3)
# S23：乌龟伸长脖子（0～1.3，笛子往上滑）→ 咬住鹤嘴（1.2～1.6）"呛" → 鹤僵住（空一下）→ 甩（2.4～4.8，板胡颤音 + 梆子）→ 小满得意（一个俏皮的收尾）
t0 = T('S23')
melody('dizi', [{'t': t0 + 0.1, 'd': 1.1, 'f': jp(1, 1, D5), 'acc': 0.5}, {'t': t0 + 1.2, 'd': 0.2, 'f': jp(1, 2, D5), 'acc': 0.75, 'slide': 1.0, 'legato': True}], 0.35)
place(MUS['perc'], qiang(0.9), t0 + 1.45, 0.7)
melody('banhu', [{'t': t0 + 2.4, 'd': 2.0, 'f': jp(6, 0, D5), 'acc': 0.75, 'trill': jp(1, 1, D5)}], 0.45)
for k in range(9):
    place(MUS['perc'], bangzi(0.7), t0 + 2.4 + k * 0.25, 0.25)
melody('banhu', mel("5:0.25 6:0.25 1':0.5! 0:0.5 5:0.25 1':0.75!", t0 + 4.45, 140, D5), 0.45)

# ================================================================ 第 9 场：小狗（S25、S26）
print('第 9 场…')
t0 = T('S25')
sfx(flashlight_click(0.8), t0 + 0.8, 0.45, -0.2); sfx(thud(0.5, 200, 0.04, 3000), t0 + 1.2, 0.35, -0.2)   # 手电架在木箱上
# 两只手伸进光里：8-bit 琶音一点点往上爬，扬琴轮音垫着
arp = []
for k in range(16):
    tk = 2.0 + k * 0.25
    arp.append({'t': tk, 'd': 0.2, 'f': jp([1, 3, 5, 1, 2, 5, 6, 2][k % 8], 1 + (k >= 8), D5), 'acc': 0.4 + 0.03 * k})
y = chip_lead(arp, 6.0, 0.125); place(MUS['chip'], y, t0, 0.35)
for tw in (4.6, 5.35):                                     # js/code/s25.js：狗影第一次张嘴
    sfx(woof(0.7), t0 + tw, 0.16, 0.2)
place(MUS['yq'], yangqin(jp(5, -1, D5), 3.5, 0.5), t0 + 3.0, 0.25)
# S26：画面的时间是 u = tempo(t)（js/lamp/shots/s26.js，10 秒后越演越快）。音乐的拍 = 2u，所以和画面一起加速
t0 = T('S26')
tempo = lambda t: t + 0.8 * np.maximum(0, t - 10) ** 2 / 16
uu = np.linspace(0, 18, 18001); bb = 2 * tempo(uu)
beat_time = lambda b: t0 + float(np.interp(b, bb, uu))   # 第 b 拍在片中的时间
END26 = T('S27')


def put(track, clip, b, g):
    tt = beat_time(b)
    if tt < END26 - 0.005:
        place(MUS[track], clip[:max(1, ns(END26 - tt))], tt, g)


# 狗叫（1.0～2.8、9.5～10.5 秒，下巴 sin(u·14) 张开的时候）
for tw in [(1.0, 2.6), (9.6, 10.4)]:
    k = 0
    while True:
        u = (np.pi / 2 + 2 * np.pi * k) / 14; k += 1
        if u < tw[0]:
            continue
        if u > tw[1]:
            break
        sfx(woof(0.8), t0 + u, 0.22, 0.25)
# 前奏两拍：8-bit 低音"咚咚"+梆子；第 4 拍起主题：方波奏前四小节，板胡接后四小节；第二遍笛子领，方波和声；第三遍一起，越来越快
for b in range(4):
    put('chip', chip_tri([{'t': 0, 'd': 0.2, 'f': jp(1, -3, D5), 'acc': 0.9}], 0.3), b, 0.8)
    put('perc', bangzi(0.8), b + 0.5, 0.3)
seq, nb = parse(THEME_A, D5)
seqd, _ = parse(THEME_A_DIZI, D5)


def notes_at(sq, b0, mult=1.0, oct=0, acc=0.75, gap=0.02, lo=0, hi=1e9):
    out = []
    for b, d, f, fl in sq:
        if not (lo <= b < hi):
            continue
        ta = beat_time(b0 + b); tb = beat_time(b0 + b + d)
        if ta >= END26:
            continue
        n_ = {'t': ta, 'd': min(tb, END26) - ta - gap, 'f': f * 2 ** oct, 'acc': acc + (0.2 if '!' in fl else 0)}
        if '~' in fl:
            n_['slide'] = 0.1
        if '=' in fl:
            n_['legato'] = True
        if '^' in fl:
            n_['grace'] = f * 2 ** oct * 2 ** (2 / 12)
        if 't' in fl:
            n_['trill'] = f * 2 ** oct * 2 ** (2 / 12)
        out.append(n_)
    return out


B0 = 4
# 第一遍
ch = notes_at(seq, B0, oct=1, hi=8)
melody('banhu', notes_at(seq, B0, lo=8), 0.5)
# 第二遍：笛子领，方波高八度跟着
melody('dizi', notes_at(seqd, B0 + 16), 0.45)
ch += [dict(n_, acc=0.45) for n_ in notes_at(seq, B0 + 16, oct=1)]
# 第三遍：方波 + 板胡齐奏（加速）
ch += notes_at(seq, B0 + 32, oct=1)
melody('banhu', notes_at(seq, B0 + 32), 0.5)
y = chip_lead([dict(n_, t=n_['t'] - t0) for n_ in ch], END26 - t0, 0.25); place(MUS['chip'], y, t0, 0.32)
# 低音、鼓：每拍底鼓，2、4 拍拍手，后半拍梆子 + 8-bit 噪声；扬琴和弦
bass = []
b = 0
while beat_time(b) < END26:
    r = THEME_ROOTS[int((b - B0) // 2) % 8] if b >= B0 else 1
    bass.append({'t': beat_time(b) - t0, 'd': (beat_time(b + 0.5) - beat_time(b)) * 0.9, 'f': jp(r, -3, D5), 'acc': 0.9})
    bass.append({'t': beat_time(b + 0.5) - t0, 'd': (beat_time(b + 1) - beat_time(b + 0.5)) * 0.9, 'f': jp(r, -2, D5), 'acc': 0.7})
    if b >= B0:
        put('beat', kick(0.9), b, 0.55)
        if int(b) % 2 == 1:
            put('beat', clap(0.6), b, 0.4)
        put('beat', chip_noise(0.06, 0.3), b + 0.5, 0.4)
        put('perc', bangzi(0.7), b + 0.5, 0.3)
        if int(b - B0) % 2 == 0:
            put('yq', yangqin(jp(r, 0, D5), 1.0, 0.5), b + 0.5, 0.25)
    b += 1
y = chip_tri([n_ for n_ in bass if n_['t'] < END26 - t0], END26 - t0); place(MUS['chip'], y, t0, 0.45)
for bb_ in [B0 + 16, B0 + 32]:
    put('perc', qiang(0.8), bb_, 0.5)
# 乌龟骑上狗背（6.0～7.0）：小锣"台"
place(MUS['perc'], xiaoluo(0.7), t0 + 6.5, 0.35)

# ================================================================ 第 10 场：来电（S27–S29）——音乐整段停，只剩电器
print('第 10 场…')
# 所有音乐轨在来电那一刻切断（硬切，不淡出）
s_on = ns(ON)
for k in MUS:
    MUS[k][s_on:s_on + ns(8)] = 0          # 先清掉可能拖过来的余音（后面关灯后的音乐再加）
# 日光灯：启辉器"嗒"、闪两下、"叮"一声亮起（js/lamp/shots/s27.js fluorAt：0、0.22、0.52 秒亮）
for x, v in [(0.0, 0.7), (0.12, 0.4), (0.22, 0.6), (0.30, 0.4), (0.52, 0.8)]:
    sfx(click(v, 4000, 600), ON + x, 0.5, 0.25)
ping = modal([3100, 4800, 7400], [0.5, 0.3, 0.15], [1, 0.5, 0.3], 1.2); sfx(norm(ping, 0.5), ON + 0.52, 0.25, 0.25)
# 一串电器：吊扇转起来（嗡声和风声在环境声里）、电视"嗡—咚"显像管消磁再响起来、手机"叮"开始充电
dg_n = ns(1.2); dgt = secs(dg_n)
degauss = norm(np.sin(2 * np.pi * 60 * dgt) * np.exp(-dgt / 0.35) * (1 + 0.5 * np.sin(2 * np.pi * 7 * dgt)) + bp(R.standard_normal(dg_n), 100, 2000) * np.exp(-dgt / 0.05), 0.8)
sfx(click(0.6, 2500, 200), TV_ON - 0.05, 0.4, -0.55); sfx(degauss, TV_ON, 0.45, -0.55)
sfx(tv_static(0.9) * np.linspace(1, 0.2, ns(0.9)).astype(np.float32), TV_ON + 0.1, 0.15, -0.55)
sfx(click(0.5, 1800, 300), FAN_ON, 0.3, 0.0)                # 吊扇的开关
sfx(chime([1568.0], 0.2, 1.0), T('S28', 5.5), 0.25, -0.1)   # 手机开始充电
# 奶奶用布包皮影
sfx(rustle(3.0, 27, 600, 5000), T('S29', 1.0), 0.3, 0.2); sfx(leather(1.2, 28), T('S29', 1.6), 0.25, 0.2)
# 手机开机"叮—咚"：就是主题的头两个音（高音 1 → 5）
sfx(chime([jp(1, 1, D5), jp(5, 0, D5)], 0.28, 1.6), T('S29', 5.5), 0.35, -0.1)

# ================================================================ 第 12 场：关灯（S30、S31）
print('第 12 场…')
sfx(footsteps([0, 0.5, 1.0, 1.5, 2.0, 2.5]), T('S30', 1.5), 0.3, -0.5)
sfx(pull_cord(), OFF - 0.05, 0.6, -0.6)
sfx(click(0.5, 2500, 200), TV_OFF, 0.3, -0.55)            # 电视关掉
# 关灯后：安静几秒；S31 笛子轻轻地、慢慢地回来（主题前四小节），然后板胡、扬琴加进来，完整地回来
t0 = T('S31')
melody('dizi', mel(THEME_A, t0 + 1.0, 84, D5, beats_to=8, gap=0.03, acc=0.5), 0.4)
T2 = t0 + 1.0 + 8 * 60 / 84
yq_chords(T2, THEME_ROOTS[4:], 84, 2, 0.2, pattern='arp')
melody('dizi', mel(THEME_A, T2, 84, D5, beats_from=8, gap=0.03, acc=0.55), 0.4)
T3 = T2 + 8 * 60 / 84                                       # 约 S31 的 12.4 秒
BPF = 118                                                   # 尾声的速度：32 拍正好走到 S32 结尾
melody('banhu', mel(THEME_A, T3, BPF, D5, beats_to=4), 0.4)
yq_chords(T3, THEME_ROOTS, BPF, 2, 0.3)
bangzi_beats(T3, BPF, 4, 0.25)

# ================================================================ 第 13 场 + 字幕：完整的主题
print('第 13 场、字幕…')
BP = BPF; sp = 60 / BP
t0 = T3 + 4 * sp
melody('banhu', mel(THEME_A, t0, BP, D5, beats_from=4), 0.45)
yq_chords(t0, THEME_ROOTS[2:], BP, 6, 0.3)
bangzi_beats(t0, BP, 12, 0.25)
t1 = t0 + 12 * sp
melody('dizi', mel(THEME_A_DIZI, t1, BP, D5), 0.45)
melody('banhu', mel(THEME_A, t1, BP, D5, oct=-1, acc=0.55), 0.3)            # 板胡低八度托着
yq_chords(t1, THEME_ROOTS, BP, 8, 0.3)
for b in range(8):
    place(MUS['pipa'], pipa(jp(THEME_ROOTS[b], -1, D5), 1.2, 0.5, tremolo=1.0), t1 + b * 2 * sp, 0.25)
bangzi_beats(t1, BP, 16, 0.25)
t2 = t1 + 16 * sp
place(MUS['perc'], qiang(0.7), t2, 0.45)                    # 片名出来
# 片尾（js/code/credits.js）：锁屏亮着的时候扬琴"叮—咚"，屏幕熄灭（6.3 秒）时一声梆子
TE = T('END')
place(MUS['yq'], yangqin(jp(1, 1, D5), 4.0, 0.6), TE + 2.4, 0.3)
place(MUS['yq'], yangqin(jp(5, 0, D5), 4.0, 0.6), TE + 2.85, 0.28)
place(MUS['perc'], bangzi(0.8), TE + 6.3, 0.4)
t4 = TE + 4.3
print(f'  片名"呛"在 {t2:.1f} 秒（S32 结尾 {T("END"):.1f}），最后一声梆子 {TE + 6.3:.1f} 秒（全片 {TOTAL - 1:.1f} 秒）')

# ================================================================ 合成旋律、混音
print('合成旋律…')
render_lines()
# 来电那一刻再切一次（旋律线是最后合成的）
for k in MUS:
    MUS[k][s_on:s_on + ns(OFF - ON)] = 0
for k in ('chip', 'beat'):                                  # 方波占空比 25% 有直流分量，先隔直
    MUS[k] = hp(MUS[k], 20).astype(np.float32)
music = (pan(MUS['banhu'] * 0.55, 0.15) + pan(MUS['dizi'] * 0.5, -0.12) + pan(MUS['yq'] * 0.35, -0.35) + pan(MUS['pipa'] * 0.45, 0.35)
         + pan(MUS['perc'] * 0.6, 0.05) + pan(MUS['chip'] * 0.35, 0.0) + pan(MUS['beat'] * 0.5, 0.0))
print('混响…')
music = reverb(music, reverb_ir(1.1), wet=0.2)
music[s_on:s_on + ns(OFF - ON)] = 0                            # 混响尾巴也切掉：来电是一刀切
SFX_r = reverb(SFX, reverb_ir(0.45, bright=5000), wet=0.15)
music = music * 0.9                                          # 分轨和总混音用同一个系数，三条分轨相加就是总混音
# 15 Hz 高通在每条分轨上各做一次再相加（线性滤波，等价于对总混音做），这样三条分轨相加仍然就是总混音
hp2 = lambda x: np.stack([hp(x[:, 0], 15), hp(x[:, 1], 15)], 1).astype(np.float32)
music, SFX_r, AMB = hp2(music), hp2(SFX_r), hp2(AMB)
mix = music + SFX_r + AMB
peak = np.abs(mix).max(); mix = mix / peak * 0.89
print(f'峰值归一前 {peak:.2f}')
for name, x in [('music', music), ('sfx', SFX_r), ('amb', AMB)]:
    wavfile.write(os.path.join(OUT, f'stem_{name}.wav'), SR, (np.clip(x / peak * 0.89, -1, 1) * 32767).astype(np.int16))
wavfile.write(os.path.join(OUT, 'film_mix.wav'), SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
# 响度归一（两遍 loudnorm）：-16 LUFS，PCM 真峰目标 -4.5 dBTP；成片 AAC 仍须独立复测。
# 2026-10-17 云端实测：-2.5 目标所得256k全片AAC为-0.66dBTP；-3.5目标全片通过但S08单独编码为-0.79dBTP。
# 在修电视/吊扇时序前，同参数实测WAV为-4.40dBTP/-16.00LUFS，256k全片AAC为-3.19dBTP/-16.05LUFS。
# 同一WAV按当前EDL单独编码31镜后均<=-3.28dBTP；不把PCM目标值或单一片段测量当编码后保证。
# 修正TV_OFF与吊扇后：WAV -16.04LUFS/-4.40dBTP；全片256k AAC -16.08/-3.72；31镜单独编码最高-3.16dBTP。
# 实际文件/hash/命令见collab/reviews/20261017_0616_integration/audio_final/，本行仅补验收记录，不改变音频计算。
# 修改混音/剪辑/编码参数后，以最终AAC <= -1.5dBTP复验；这些数字不代替试听。
src = os.path.join(OUT, 'film_mix.wav'); dst = os.path.join(OUT, 'film_mix_norm.wav')
r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', src, '-af', 'loudnorm=I=-16:TP=-4.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
af = f"loudnorm=I=-16:TP=-4.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-af', af, '-ar', str(SR), dst], check=True)
print(f"响度：原 {m['input_i']} LUFS / 真峰 {m['input_tp']} dBTP → -16 LUFS")
print(dst, f'{TOTAL:.1f}s')
