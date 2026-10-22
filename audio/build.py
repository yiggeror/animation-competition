# 全片声音：按剪辑表（js/film/edl.js）把环境声、音效、配乐放到每个镜头的时间上，混成一条立体声。
# 运行：python3 audio/build.py  → build/audio/film_mix.wav（以及分轨 build/audio/stem_*.wav）
# 时间都写成"镜头号 + 镜头内的秒数"，剪辑表改了时长会自动跟着走。镜头里的动作时间来自各镜头模块（注释里写了出处）。
#
# 音乐的走向（简报"声音与配乐"）：
#   片头：皮影戏开场的小锣鼓，很轻；片名贴上床单变清楚时小锣"台"
#   第 1–5 场：没有配乐，只有环境声和手机游戏的 8-bit 小曲（手机喇叭里出来的，是剧中声音）
#   第 4 场木箱：扬琴轻轻两个音"叮—咚"（主题的头两个音，先埋一下）
#   第 6 场：开场锣鼓 → "呛" → 板胡奏主题（鹤昂首时进主题）
#   第 7 场：乌龟的低音拨弦步子；啄空、撞壳（大锣）、晕（板胡大滑音）、乌龟偷笑（笛子颤音）
#   第 8 场：上手——节奏绊跟头、乌龟翻肚皮、奶奶笑；影子忽大忽小；手把手时只剩笛子慢慢吹；咬嘴"呛"
#   第 9 场：小狗——8-bit 方波 + 电子鼓 + 板胡、梆子一起，越来越快（14.4 秒起和画面一起加速）
#   第 10 场：来电，音乐整段停；只剩一串电器的声音。手机开机提示音就是主题的"叮—咚"
#   第 12 场：关灯，安静；旋律先由笛子轻轻地回来，再完整地回来
#   第 12 场切到床单正面"又演起来了"：板胡把主题拉回来；第 13 场屋外拉远：笛子领奏，结尾"呛"
#   尾声手机：扬琴"叮—咚"、屏幕熄灭一声梆子；片尾"制作与资源"：笛子慢慢吹一遍主题收
import sys, os, json, subprocess
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(__file__))
from inst import *
import inst
from sfx import *
from score import *
import rec as RC

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


S01 = T('S01')                                             # 片头之后正片从这里开始


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


def act(x):
    """有声部分的 RMS（只算幅度在峰值 1% 以上的采样）"""
    x = np.asarray(x); m = x if x.ndim == 1 else x.mean(1); a = np.abs(m); v = m[a > a.max() * 0.01]
    return float(np.sqrt(np.mean((v if len(v) else m) ** 2))) + 1e-9


def like(clip, ref):
    """真实录音按原来合成音效的响度（有声部分 RMS）对齐：只换音色，不动混音平衡；峰值不超过原来合成音效的 1.2 倍（短促的录音按 RMS 对齐会冲得太高）"""
    pk = lambda x: float(np.abs(np.asarray(x)).max()) + 1e-9
    return (clip * min(act(ref) / act(clip), 1.2 * pk(ref) / pk(clip))).astype(np.float32)


def steps(name, times, vel=0.4):
    """真实脚步：录音里切出的一步一步轮流用，按 times 放"""
    hs = RC.hits(name); out = np.zeros(ns(max(times) + 1.3), np.float32)
    for k, tt in enumerate(times):
        c = hs[(k * 3 + 1) % len(hs)][1] * (vel if k % 2 else vel * 0.85)
        s0 = ns(tt); out[s0:s0 + len(c)] += c[:len(out) - s0]
    return out


def voice(name, t, gain, p=0.0, semis=0.0, maxlen=None):
    """人物的语气声（无台词）：录音起音对齐 t。10-22 用户听后决定先不放人声（之后试语音模型），这个函数留着备用"""
    c = RC.one(name, rel=-30, maxlen=maxlen or 6.0)
    if semis:
        c = RC.pitch(c, semis)
    sfx(c, t, gain, p)


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
# 虫鸣：真实的夏夜蟋蟀（Freesound 333221，220 秒）和蛙鸣（32655，81 秒）循环，按原来合成虫鸣的响度对齐
cr_old = crickets(amb_len, 6, seed=1)[:, 0] + 0.55 * frogs(amb_len, 1.1, seed=3)[:, 0]
night = RC.loop('night', amb_len, xf=3.0) + 0.45 * RC.loop('frogs', amb_len, xf=3.0, t0=2.0)
night = np.pad(night, (0, max(0, N - len(night))))[:N] * (act(cr_old) / act(night)); del cr_old
fr = ci = None
# 停电以后屋里静了，虫子显得更响；音乐进来时压低；来电时被电器盖住；关灯后又回来
CUT = T('S04', 7 / 24); ON = T('S27', 0.0); OFF = T('S30', 110 / 24)   # S30 196 格版：F110 拉灯绳灭灯
insects_db = [(0, -40), (0.4, -40), (1.2, -19), (S01 - 0.01, -19), (S01, -14), (CUT, -14), (CUT + 1.5, -8), (T('S15'), -8), (T('S15', 3), -15), (ON - 0.01, -15), (ON, -24),
              (OFF, -24), (OFF + 2, -7), (T('S31', 2), -9), (T('S31', 6), -15), (T('S32'), -10), (T('END'), -14), (TOTAL, -30)]
g_ins = gain_curve(insects_db)[:, None]
AMB += np.stack([night, np.roll(night, ns(0.013))], 1) * g_ins   # 两声道错开 13 毫秒，宽一点
# 吊扇独立开关：开场转着；停电后慢慢停；来电后转起来；第12场只关电视和日光灯，吊扇继续转。
FAN_ON = T('S28', 0.2)


def fan_speed(tt):
    s = np.where(tt < CUT, 1.0, np.exp(-(tt - CUT) / 2.2))
    s = np.where(tt >= FAN_ON, 1 - np.exp(-(tt - FAN_ON) / 1.6), s)
    return np.clip(s, 0, 1)


fan_syn = fan(TOTAL, fan_speed)
# 吊扇：真实吊扇录音（345230）循环，音量跟转速走（转慢了也闷一点），响度对齐原来合成的吊扇
tt_all = secs(N); spd = fan_speed(tt_all).astype(np.float32)
fan_rec = np.pad(RC.loop('fan', TOTAL, xf=1.0), (0, 2))[:N]
fan_x = fan_rec * spd ** 1.3 + lp(fan_rec, 600) * spd * (1 - spd) * 0.8
fan_x = fan_x * (act(fan_syn) / act(fan_rec)); del fan_syn
fan_db = [(0, -22), (T('S02'), -27), (T('S03'), -22), (CUT + 5, -22), (TOTAL, -22)]
ROOM = np.zeros(N, np.float32); ROOM[ns(S01):] = 1           # 片头没有屋里的电器声
AMB += pan(fan_x * gain_curve(fan_db) * ROOM, 0.0)
# 日光灯的嗡声：开场亮着，停电灭；来电亮，关灯灭
hum = np.pad(RC.loop('fluor_hum', TOTAL, xf=0.8), (0, 2))[:N]          # 真实日光灯镇流器的嗡声（474312）
hum = hum * (act(fluor_hum(10.0)) / act(hum))
hum_g = np.zeros(N, np.float32)
hum_g[ns(S01):ns(CUT)] = 1; hum_g[ns(T('S27', 0.52)):ns(OFF)] = 1.3
AMB += pan(hum * hum_g * 10 ** (-30 / 20), 0.2)
# 电视：第12场先按掉电视，再走向门边拉灯绳；TV_OFF与S30开头CRT特写同步。
TV_ON = T('S28', 1.4)
TV_OFF = T('S30', 27 / 24)   # 画稿 S30：F027 按下关屏
tvb = tv_babble(TOTAL)
tv_g = np.zeros(N, np.float32); tv_g[ns(S01):ns(CUT)] = 1; tv_g[ns(TV_ON + 0.9):ns(TV_OFF)] = 1
tv_g *= gain_curve([(0, -20), (T('S02'), -27), (T('S03'), -21), (TOTAL, -21)])
AMB += pan(tvb * tv_g, -0.55)
whine = crt_whine(TOTAL)
wg = np.zeros(N, np.float32); wg[ns(S01):ns(CUT)] = 1; wg[ns(TV_ON):ns(TV_OFF)] = 1
wg[ns(TV_OFF):ns(TV_OFF + 0.3)] = np.linspace(1, 0, ns(TV_OFF + 0.3) - ns(TV_OFF))
AMB += pan(whine * wg * 0.25, -0.55)
# 马灯火苗：点着以后一直在（近景响一点）
LAMP = T('S08', 43 / 24)   # 灯芯着了（画稿 F043）
fl = flame(TOTAL - LAMP)
s0 = ns(LAMP)
flg = gain_curve([(0, -26), (T('S08', 4), -18), (T('S09'), -28), (T('S12'), -24), (T('S13'), -30), (ON, -40), (OFF + 1, -28), (TOTAL, -28)])[s0:s0 + len(fl)]   # 曲线是全片时间，截出灯亮以后的一段
fl = fl[:len(flg)]; AMB[s0:s0 + len(fl)] += pan(fl * flg, 0.3)
# 片头床单后面的马灯：跟着画面的亮暗（js/code/title.js：0.2–1.1 亮起，4.25–4.95 暗下去）
tfl = flame(S01, seed=9)
tfl *= gain_curve([(0, -60), (0.2, -60), (1.1, -27), (T('TITLE', 4.25), -27), (T('TITLE', 4.95), -60), (S01, -60)], len(tfl))
AMB[:len(tfl)] += pan(tfl, 0.1)
# 片尾字幕时屋里的声音慢慢退下去
AMB *= gain_curve([(0, 0), (T('MAKING'), 0), (T('MAKING', 8), -14), (TOTAL, -40)])[:, None]

# ================================================================ 片头
print('片头…')
# 皮影戏开场的小锣鼓，很轻，像隔着床单：板鼓越敲越密，片名贴上床单变清楚（js/code/title.js 3.0 秒）时小锣"台"，扬琴低音托一下
t0 = T('TITLE'); tt = t0 + 1.0; gap = 0.3
while tt < t0 + 2.85:
    place(MUS['perc'], bangu(0.25 + 0.35 * (tt - t0 - 1.0) / 1.85), tt, 0.35); tt += gap; gap = max(0.06, gap * 0.85)
place(MUS['perc'], xiaoluo(0.55), t0 + 3.0, 0.32)
place(MUS['yq'], yangqin(jp(5, -1, D5), 3.0, 0.45), t0 + 3.0, 0.25)

# ================================================================ 第 1–5 场：手机游戏、剥毛豆、停电
print('第 1–5 场…')
# 手机游戏的 8-bit 小曲（剧中声音，从手机小喇叭出来）：一段 2 小节的跳跃短句循环
GAME = "5:0.25 5:0.25 1':0.25 5:0.25 6:0.25 5:0.25 3:0.25 5:0.25 | 2:0.25 2:0.25 5:0.25 2:0.25 3:0.25 2:0.25 1:0.25 2:0.25"
GAME_END = T('S05', 2.42)   # 屏幕一暗（js/anim/s05.js 取原 s05 的 0.63 秒起，原 3.05）；2.5～3.0 全黑停半秒


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


gm = game_music(S01, GAME_END)
gm_db = [(0, -30), (T('S02') - 0.01, -30), (T('S02'), -17), (T('S03'), -31), (CUT, -31), (CUT + 0.5, -27), (T('S05'), -18), (TOTAL, -18)]
s0 = ns(S01); gm = gm[:N - s0]; SFX[s0:s0 + len(gm)] += pan(gm * gain_curve(gm_db)[s0:s0 + len(gm)], -0.1)


def jump_snd():
    n = ns(0.18); f = 300 + 900 * secs(n) / 0.18
    return phone_speaker(inst._bl_pulse(f, n, 0.5) * np.exp(-secs(n) / 0.12))


def coin_snd():
    n = ns(0.25); f = np.where(secs(n) < 0.06, 1318.5, 1760.0)
    return phone_speaker(inst._bl_pulse(f, n, 0.5) * np.exp(-secs(n) / 0.1))


for p in [0.45, 1.35, 2.2, 3.05]:                           # js/code/s02.js PRESS（js/anim/s02.js 取原片 1.5 秒起）
    if p >= 1.5:
        sfx(jump_snd(), T('S02', p - 1.5), 0.12); sfx(coin_snd(), T('S02', p - 1.5 + 0.3), 0.08)
sfx(jump_snd(), T('S01', 1.2), 0.03, -0.2)                 # 远景里偶尔听到的一声"跳"
# S02a 小满近景：1.0 游戏里差点输（一串急促的跳），1.85 躲过去（金币）
for p in [0.3, 0.75, 0.95, 1.05]:
    sfx(jump_snd(), T('S02a', p), 0.08)
sfx(coin_snd(), T('S02a', 1.85), 0.1)
MASH = []; p = 1.15
while p < 3.0:
    MASH.append(p); p += 0.14 + 0.03 * np.sin(p * 13)       # js/code/s05.js MASH
S05_OFF = 0.63                                             # js/anim/s05.js 取原 s05 的 0.63 秒起
for i, p in enumerate(MASH):
    if i % 3 == 0:
        sfx(jump_snd(), T('S05', p - S05_OFF), 0.10)
for p in [39 / 24, 44 / 24]:
    sfx(click(0.2, 1800, 300), T('S05a', p), 0.25)          # 黑屏后猛按电源键：手机举进画面后拇指按侧键的两下（F039、F044）
# 剥毛豆（奶奶，右边）、推西瓜
# S01 奶奶剥豆的声音对画面（Astra 的 S01 B 曝光表，帧号 24fps）：掰开豆荚那一帧"啪"，两颗豆落盆各"叮"一下（悬空三帧之后、换成落定那一帧，即落下那帧后 3 帧）
# 10-18 重排后（js/anim/s01.js）：0.5 掐开豆荚，1.35–1.7 豆子落盆两下
sfx(beans_at([12 / 24], [34 / 24, 35 / 24], 10), T('S01', 0), 0.10, 0.45)   # Astra 17:47：F012 掐开，F034/F035 两豆各自第一次碰盆
# S03 不演剥豆（母版手里是西瓜，10-17 定），这里不再放剥豆声
sfx(like(RC.one('bite'), rustle(0.5, 21, 600, 4000)), T('S03b', 0.6), 0.3, 0.1)   # 咬西瓜（js/anim/s03b.js 0.6 咬下），真实咬脆果子的录音
# 停电：继电器"啪"、电视"嘣"
sfx(power_cut(), CUT, 0.4, -0.3); sfx(like(RC.whole('tv_off'), power_cut()), CUT, 0.45, -0.55)   # 继电器"啪" + 真实显像管电视断电

# ================================================================ 第 2–5 场：插头、倒下、找灯、划火柴、手电、木箱、搭台（屋内镜头的动作按这些时间来做）
print('屋内音效…')
# S06 画稿版（插线板在席子边，Astra 10-19）：F011 拔、F030 插、F046 拔、F070 插；中间两次看仍黑的手机，不吹插头
for k, t0 in enumerate((11 / 24, 30 / 24, 46 / 24, 70 / 24)):   # 拔、插、拔、插（真实插头录音）
    sfx(like(RC.one('plug_out' if k % 2 == 0 else 'plug_in'), plug(False)), T('S06', t0), 0.4, 0.15)
# js/anim/s07.js（10-18 Astra 修订版 f75be82 的节拍）：0.5 手机落席，0.64～1.08 小满侧滚到仰躺，1.45 起扇风；
# 奶奶 0.72 盆落地，0.92 掌压膝、1.05 离凳，1.62～1.98 转身两步，走四步落脚 2.43/2.88/3.33/3.78、4.095 收脚，4.3 抓住提梁
# S07 画稿版（Astra 10-19 按实片给的帧）：008 手机落席、018 盆触地、043 扇风、068/079/090/095 四脚承重、103 握提梁
# 小满翻身在 016–038 被切走（画外），沙沙声在 039 仰躺前收住；奶奶转身两步在 048/054（画外，听感补的）；凳子没挪，只轻轻吱一声
sfx(like(RC.one('phone_drop'), click(0.12, 900, 250)), T('S07', 8 / 24), 0.2, -0.1)   # 手机落在竹席上
sfx(like(RC.whole('mat'), bamboo_mat(0.3)), T('S07', 1.0), 0.2, -0.1)                 # 画外侧滚，衣服蹭席子
sfx(like(RC.one('flop'), thud(0.9, 80, 0.15, 900)), T('S07', 36 / 24), 0.4, -0.1); sfx(like(RC.whole('mat'), bamboo_mat(0.7)), T('S07', 36 / 24 + 0.02), 0.35, -0.1)   # 仰面落定
sfx(fan_hand(1.4, 1.4), T('S07', 43 / 24), 0.25, -0.1)
sfx(like(RC.one('basin', 4), thud(0.3, 160, 0.05, 1800)), T('S07', 18 / 24), 0.16, 0.4)   # 搪瓷盆放到地上（真实敲铁盆录音）
sfx(like(RC.one('sit', maxlen=0.25), scrape(0.12, 4)), T('S07', 27 / 24), 0.1, 0.4)       # 起身时凳子轻轻吱一声
sfx(like(steps('steps_slipper', [0, 6 / 24], 0.25), footsteps([0, 6 / 24], 0.25)), T('S07', 48 / 24), 0.3, 0.5)   # 转身的两步，轻（画外）
sfx(like(steps('steps_slipper', [0, 11 / 24, 22 / 24, 27 / 24]), footsteps([0, 11 / 24, 22 / 24, 27 / 24])), T('S07', 68 / 24), 0.35, 0.55)   # 走到桌边，四脚承重（真实拖鞋脚步）
sfx(like(RC.whole('latch'), click(0.15, 2600, 500)), T('S07', 103 / 24), 0.12, 0.7)       # 握住提梁"咔"一下
# js/code/s08.js：0.35 划火柴，1.8 灯芯着了，2.2 甩灭火柴，3.4 放下灯罩
# S08 画稿版（Astra 41 态表，帧号 24fps）：003 擦柴、017 盒落桌、025 压杆升罩、043 灯芯着、049 甩柴、066 柴落桌、078 松杆、082 罩落座
sfx(like(RC.one('match', 1), match_strike()), T('S08', 3 / 24), 0.7, -0.15)   # 真实划火柴：擦、着
sfx(like(RC.whole('thud_small'), thud(0.25, 220, 0.03, 2500)), T('S08', 17 / 24), 0.18, -0.1)   # 火柴盒放到桌上
sfx(like(RC.whole('latch'), click(0.15, 2200, 500)), T('S08', 25 / 24), 0.15, 0.1)               # 压下拨杆、灯罩升起
sfx(burst(0.4, 300, 3000, a=0.05, r=0.15, g=0.4), T('S08', 43 / 24), 0.4, 0.05)   # 灯芯着了
sfx(burst(0.25, 200, 1500, a=0.02, r=0.08, g=0.25), T('S08', 49 / 24), 0.3, 0.2)  # 甩灭火柴的"呼"
sfx(like(RC.whole('tap'), click(0.08, 3000, 400)), T('S08', 66 / 24), 0.08, -0.05)   # 火柴梗落桌
sfx(like(RC.whole('latch'), click(0.1, 1800, 400)), T('S08', 78 / 24), 0.1, 0.1)       # 松开拨杆
sfx(like(RC.whole('glass'), glass_clink(0.6)), T('S08', 82 / 24), 0.4, 0.05)           # 灯罩落座"叮"（真实小玻璃杯）
# js/paint/shots/s09.js：开镜时手电已经在手里（抽屉在上一镜之间翻过了）；1.6 推开关不亮，2.1、2.5 往手心磕，2.9 推亮
# S09 画稿版（Astra 10-19）：014 推开关不亮、026 推回、042/056 尾盖两下磕手心、073 再推亮了
fc = lambda i, v=0.7: like(RC.one('torch_click', i), flashlight_click(v))           # 真实手电开关
sfx(fc(0), T('S09', 14 / 24), 0.4, -0.3); sfx(fc(1, 0.5), T('S09', 26 / 24), 0.3, -0.3)
sfx(like(RC.whole('tap'), flashlight_slap()), T('S09', 42 / 24), 0.45, -0.3); sfx(like(RC.whole('tap'), flashlight_slap(0.9)), T('S09', 56 / 24), 0.5, -0.3)
sfx(like(RC.one('torch_on'), flashlight_click(0.8)), T('S09', 73 / 24), 0.45, -0.3)
# S31 手电从木箱拿起时就一直亮着；开镜直接照下巴，不增加推开关的 click。
# js/code/s12.js：0～0.9 箱盖开到底，1.5 手伸进来碰到布，2.4～4.0 握住签子把鹤立起来
# js/paint/shots/s12.js：开镜时箱盖已经开着（奶奶两只手都握着签子），没有开盖声
# S12 画稿 140 格（10-21 交接）：000–028 两手探进箱里，030 前后握住签子，072–084 把鹤立起来，084 起鹤站在箱里、灯光透过牛皮
sfx(like(RC.one('cloth2'), rustle(0.9, 23, 800, 5000)), T('S12', 0.3), 0.25, 0.1)   # 手碰到包布（真实布料）
sfx(like(RC.one('leather', 3), leather(0.5, 29)), T('S12', 30 / 24), 0.2, 0.1)        # 握住签子
sfx(like(RC.one('leather', 1), leather(1.0, 24)), T('S12', 72 / 24), 0.35, 0.1)       # 立起来，牛皮沙沙（真实皮革）
# S14 画稿 190 格（10-21 交接的曝光表）：000–017 奶奶站在凳上把床单甩上铁丝，040 前后夹好第一只衣夹、086 第二只，092 手收回；
# 096–131 近景挂马灯（108 握住提梁、116 挂上钩）；132–144 小满站着拖凳子，161 坐到凳上，175 抱起胳膊
ref = rustle(1.0, 25, 300, 2500, 0.6)
sfx(like(RC.whole('sheet'), ref), T('S14', 0.0), 0.3, 0.0); sfx(like(RC.whole('sheet'), ref), T('S14', 0.3), 0.25, 0.05)   # 床单甩上铁丝（真实布料抖动，两下）
sfx(like(RC.one('hook', 0), metal_clink(0.4)), T('S14', 10 / 24), 0.18, 0.0)          # 铁丝晃
sfx(like(RC.one('clothespin', 0), clothespin()), T('S14', 40 / 24), 0.35, -0.1); sfx(like(RC.one('clothespin', 2), clothespin()), T('S14', 86 / 24), 0.35, 0.1)   # 真实木衣夹
sfx(like(RC.whole('latch'), click(0.15, 2600, 500)), T('S14', 108 / 24), 0.12, 0.2)   # 握住提梁
sfx(like(RC.one('hook', 1), metal_clink(0.6)), T('S14', 116 / 24), 0.3, 0.2)          # 马灯挂上钩
sfx(like(RC.one('stool'), scrape(0.55, 7)), T('S14', 133 / 24), 0.35, -0.4)          # 拖凳子（真实木椅挪动）
sfx(like(RC.one('sit'), thud(0.5, 120, 0.06, 2000)), T('S14', 161 / 24), 0.35, -0.4)  # 坐到凳上
sfx(like(RC.one('cloth', 1), rustle(0.4, 26, 1000, 5000)), T('S14', 173 / 24), 0.18, -0.4)   # 抱起胳膊
# 第 4 场木箱：奶奶把鹤举到马灯前，彩色光斑落下——扬琴很轻的"叮—咚"（主题头两个音，先埋一下）
place(MUS['yq'], yangqin(jp(1, 1, D5), 3.0, 0.5), T('S12', 86 / 24), 0.5)   # 鹤站稳、透光（F084 之后）
place(MUS['yq'], yangqin(jp(5, 0, D5), 3.0, 0.5), T('S12', 96 / 24), 0.42)

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
sfx(like(RC.whole('knock'), thud(0.9, 220, 0.05, 3000)), HIT, 0.5, 0.2)   # 鹤嘴撞龟壳（真实敲木头）
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
    sfx(like(RC.one('leather', 3), leather(0.3, int(t))), t, 0.2, -0.1)

# ================================================================ 第 7、8 场：小满笑（S18）、上手（S20–S23）
print('第 8 场…')
place(MUS['pipa'], pipa(jp(5, 0, D5), 0.6, 0.6), T('S18', 0.6), 0.35)   # "噗"
# S20 后台：奶奶把乌龟递过去（拨弦主题碎片）→ 签子缠在一起（扬琴乱了拍子的音簇）→ 乌龟翻肚皮（板胡往下滚）→ 奶奶笑弯腰（笛子颤音 + 梆子碎敲）
# S20 画稿 127 格（10-21 交接）：000–028 奶奶把乌龟递到小满手里，042–058 小满让乌龟往左走，052–064 签子缠住，064–070 乌龟翻过去、070 肚皮朝天；
# 079 切奶奶近景笑弯了腰（080–126）
t0 = T('S20')
for k, (d, o, x) in enumerate([(1, 1, 0.2), (5, 0, 0.42), (6, 0, 0.64), (1, 1, 0.76), (6, 0, 0.88), (5, 0, 1.0)]):
    place(MUS['pipa'], pipa(jp(d, o, D5), 0.7, 0.6), t0 + x, 0.35)
for k, x in enumerate([1.85, 2.15]):                       # 乌龟走两步
    place(MUS['pipa'], pipa(jp([1, 5][k], -2, D5), 0.6, 0.7), t0 + x, 0.3)
for k, x in enumerate([2.17, 2.33, 2.5, 2.62]):            # 签子缠在一起：扬琴乱了拍子的音簇
    place(MUS['yq'], yangqin(jp([2, 4, 7, 3][k], 0, D5, alt=[0, 0, -1, 0][k]), 0.9, 0.6), t0 + x, 0.3)
    sfx(like(RC.whole('rods'), rod_tap(0.5)), t0 + x + 0.02, 0.3, 0.2)   # 签子相碰（真实木棍）
flip = t0 + 70 / 24 - 0.1
melody('banhu', [{'t': flip - 0.4 + k * 0.1, 'd': 0.1, 'f': jp(1, 1, D5) * 2 ** (-k / 12 * 2.4), 'acc': 0.8, 'legato': k > 0, 'slide': 0.06} for k in range(5)], 0.45)
sfx(like(RC.whole('thud_small'), thud(0.6, 140, 0.05, 2500)), flip + 0.1, 0.35, 0.2); place(MUS['perc'], xiaoluo(0.5), flip + 0.1, 0.3)
melody('dizi', [{'t': flip + 0.6, 'd': 1.0, 'f': jp(5, 1, D5), 'acc': 0.6, 'trill': jp(6, 1, D5)}, {'t': flip + 1.7, 'd': 0.7, 'f': jp(3, 1, D5), 'acc': 0.55, 'trill': jp(5, 1, D5)}], 0.35)
for k in range(8):                                         # 奶奶笑（F080 起）
    place(MUS['perc'], bangzi(0.6), flip + 0.65 + k * 0.22, 0.22)
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
for k in range(4):                                         # 每推一次签子一声低音拨弦
    place(MUS['pipa'], pipa(jp([1, 2, 3, 5][k], -1, D5), 0.9, 0.5), t0 + 1.5 + k * 1.0, 0.3)   # 画稿 S22：每次推签的起点 F036/060/084/108（Astra 10-18）
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
# S25 V8 108 格（js/anim/s25_continuous_v8.js）：000–015 手电放到木箱上（F015 落稳），042 手伸进光里，066 狗成形，074–078、093–097 狗嘴张两下
t0 = T('S25')
sfx(like(RC.whole('thud_small'), thud(0.5, 200, 0.04, 3000)), t0 + 15 / 24, 0.35, -0.2)   # 手电架在木箱上（手电从第 3 场起一直亮着，不再有开关声）
# 两只手伸进光里：8-bit 琶音一点点往上爬，狗成形时到顶，扬琴低音垫着
arp = []
for k in range(9):
    tk = 42 / 24 + k * 0.125
    arp.append({'t': tk, 'd': 0.11, 'f': jp([1, 3, 5, 1, 2, 5, 6, 2, 3][k], 1 + (k >= 6), D5), 'acc': 0.4 + 0.04 * k})
y = chip_lead(arp, 4.5, 0.125); place(MUS['chip'], y, t0, 0.35)
place(MUS['yq'], yangqin(jp(5, -1, D5), 2.5, 0.5), t0 + 66 / 24, 0.25)
for k, tw in enumerate((74 / 24, 93 / 24)):                 # 狗嘴张开：真实小奶狗的叫声
    sfx(like(RC.one('puppy', k), woof(0.7)), t0 + tw, 0.16, 0.2)
# S26 新动作（js/lamp/shots/s26_motion.js）：0–1.4 狗影进来，0.95、1.68 两声叫，1.35 鹤吓一跳转身，2.5–5.2 被追着往左跑；
# 6.05–7.8 乌龟爬上狗背（7.8 坐稳）；8.05–8.8 狗掉头，鹤往右跑、狗追回去；11.85–13.35 鹤啄狗、狗一缩；14.4 起越玩越快。
# 音乐的拍 b(t) = 2t + 0.25·max(0, t−14.4)²：前面 120 拍/分，14.4 秒起跟画面一起加速；来电（S27）一刀切断。
t0 = T('S26')
ACC0 = 14.4
uu = np.linspace(0, 18, 18001); bb = 2 * uu + 0.25 * np.maximum(0, uu - ACC0) ** 2
beat_time = lambda b: t0 + float(np.interp(b, bb, uu))   # 第 b 拍在片中的时间
END26 = T('S27')


def put(track, clip, b, g):
    tt = beat_time(b)
    if tt < END26 - 0.005:
        place(MUS[track], clip[:max(1, ns(END26 - tt))], tt, g)


for k, tw in enumerate((0.95, 1.68)):                      # 狗嘴张开的两下
    sfx(like(RC.one('puppy', k + 1), woof(0.8)), t0 + tw, 0.22, 0.25)
place(MUS['perc'], xiaoluo(0.45), t0 + 1.4, 0.25)          # 鹤吓一跳
# 前奏四拍：8-bit 低音"咚咚"+梆子；第 4 拍（2.0 秒，开追）起主题：方波奏前四小节，板胡接后四小节；第二遍笛子领，方波和声；第三遍一起，越来越快
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
# 乌龟爬上狗背：琵琶往上一抹（6.1–6.7），坐稳（7.8）小锣"台"
for k, d in enumerate([1, 2, 3, 5, 6]):
    place(MUS['pipa'], pipa(jp(d, 0, D5), 0.5, 0.5), t0 + 6.1 + k * 0.14, 0.28)
place(MUS['perc'], xiaoluo(0.7), t0 + 7.8, 0.35)
# 鹤啄狗（12.4）：梆子重一下 + 小钹
place(MUS['perc'], bangzi(1.0, 1.2), t0 + 12.4, 0.45); place(MUS['perc'], bo(0.5, 0.6), t0 + 12.4, 0.25)

# ================================================================ 第 10 场：来电（S27–S29）——音乐整段停，只剩电器
print('第 10 场…')
# 所有音乐轨在来电那一刻切断（硬切，不淡出）
s_on = ns(ON)
for k in MUS:
    MUS[k][s_on:s_on + ns(8)] = 0          # 先清掉可能拖过来的余音（后面关灯后的音乐再加）
# 日光灯：启辉器"嗒"、闪两下、"叮"一声亮起（js/lamp/shots/s27.js fluorAt：0、0.22、0.52 秒亮）
for x, v in [(0.0, 0.7), (0.12, 0.4), (0.22, 0.6), (0.30, 0.4), (0.52, 0.8)]:   # 真实日光灯启辉器的"嗒"（145120 切出来的）
    sfx(like(RC.one('fluor_start', 0), click(v, 4000, 600)), ON + x, 0.5, 0.25)
sfx(like(RC.one('fluor_start', 1), click(0.8, 4000, 600)), ON + 0.52, 0.35, 0.25)   # 灯管亮起那一下
# 一串电器：吊扇转起来（嗡声和风声在环境声里）、电视"嗡—咚"显像管消磁再响起来、手机"叮"开始充电
dg_n = ns(1.2); dgt = secs(dg_n)
degauss = norm(np.sin(2 * np.pi * 60 * dgt) * np.exp(-dgt / 0.35) * (1 + 0.5 * np.sin(2 * np.pi * 7 * dgt)) + bp(R.standard_normal(dg_n), 100, 2000) * np.exp(-dgt / 0.05), 0.8)
sfx(like(RC.whole('latch'), click(0.6, 2500, 200)), TV_ON - 0.05, 0.4, -0.55); sfx(degauss, TV_ON, 0.45, -0.55)
sfx(tv_static(0.9) * np.linspace(1, 0.2, ns(0.9)).astype(np.float32), TV_ON + 0.1, 0.15, -0.55)
sfx(like(RC.whole('latch'), click(0.5, 1800, 300)), FAN_ON, 0.3, 0.0)   # 吊扇的开关
sfx(chime([1568.0], 0.2, 1.0), T('S28', 5.5), 0.25, -0.1)   # 手机开始充电
# 奶奶用布包皮影
sfx(like(RC.one('cloth2'), rustle(1.0, 27, 600, 5000)), T('S29', 1.0), 0.3, 0.2); sfx(like(RC.one('cloth', 0), rustle(1.0, 28, 600, 5000)), T('S29', 2.2), 0.25, 0.2)   # 奶奶用布包皮影（真实布料）
sfx(like(RC.one('leather', 0), leather(1.2, 28)), T('S29', 1.6), 0.25, 0.2)
# 手机开机"叮—咚"：就是主题的头两个音（高音 1 → 5）
sfx(chime([jp(1, 1, D5), jp(5, 0, D5)], 0.28, 1.6), T('S29', 5.5), 0.35, -0.1)

# ================================================================ 第 12 场：关灯（S30、S31）
print('第 12 场…')
st = [k * 10 / 24 for k in range(6)]
sfx(like(steps('steps_light', st), footsteps(st)), T('S30', 30 / 24), 0.3, -0.5)   # 关了电视走到门边（F030–084），真实轻脚步
sfx(like(RC.one('cord', 1), pull_cord()), OFF - 0.05, 0.6, -0.6)   # 真实拉线开关
sfx(like(RC.whole('tv_off'), click(0.5, 2500, 200)), TV_OFF, 0.3, -0.55)   # 电视关掉
# 关灯后安静；S31 A 段（小满手电照下巴做鬼脸，4.7–7.3 举着乌龟晃）只有笛子轻轻吹主题前两小节；
# 7.5 秒切到床单正面"又演起来了"：小锣、梆子带起，板胡奏主题；乌龟爬进来（8.0–10）低音拨弦一步一下，鹤低头碰乌龟（11.3）小锣"台"；
# S32 屋外拉远：笛子领奏第二遍，板胡低八度托、琵琶轮指，再把后半句走一遍收住。速度按拍数算，"呛"正好落在 S32 结尾。
t0 = T('S31')
melody('dizi', mel(THEME_A, t0 + 1.0, 84, D5, beats_to=8, gap=0.03, acc=0.5), 0.4)
for k, x in enumerate([4.9, 5.6, 6.3]):                    # 举着乌龟晃三下
    place(MUS['pipa'], pipa(jp([5, 6, 5][k], 0, D5), 0.5, 0.45), t0 + x, 0.25)
TB = t0 + 7.5; TE32 = T('END')
BPF = 42 * 60 / (TE32 - TB); sp = 60 / BPF                  # 2 拍带起 + 16 + 16 + 8 = 42 拍
place(MUS['perc'], xiaoluo(0.5), TB, 0.3); bangzi_beats(TB, BPF, 2, 0.3)
t1 = TB + 2 * sp
melody('banhu', mel(THEME_A, t1, BPF, D5), 0.42)
yq_chords(t1, THEME_ROOTS, BPF, 8, 0.28)
bangzi_beats(t1, BPF, 16, 0.22)
for k in range(4):
    place(MUS['pipa'], pipa(jp([1, 5][k % 2], -2, D5), 0.7, 0.8), t0 + 8.0 + k * 0.5, 0.35)
place(MUS['perc'], xiaoluo(0.55), t0 + 11.3, 0.3)
t2 = t1 + 16 * sp
melody('dizi', mel(THEME_A_DIZI, t2, BPF, D5), 0.45)
melody('banhu', mel(THEME_A, t2, BPF, D5, oct=-1, acc=0.55), 0.3)            # 板胡低八度托着
yq_chords(t2, THEME_ROOTS, BPF, 8, 0.3)
for b in range(8):
    place(MUS['pipa'], pipa(jp(THEME_ROOTS[b], -1, D5), 1.2, 0.5, tremolo=1.0), t2 + b * 2 * sp, 0.25)
bangzi_beats(t2, BPF, 16, 0.25)
t3 = t2 + 16 * sp                                           # 最后四小节：主题后半句再走一遍收住
melody('banhu', mel(THEME_A, t3, BPF, D5, beats_from=8, acc=0.6), 0.42)
melody('dizi', mel(THEME_A_DIZI, t3, BPF, D5, beats_from=8), 0.4)
yq_chords(t3, THEME_ROOTS[4:], BPF, 4, 0.3)
bangzi_beats(t3, BPF, 8, 0.25)
t4 = t3 + 8 * sp
place(MUS['perc'], qiang(0.7), t4, 0.45)
# 片尾（js/code/credits.js）：锁屏亮着的时候扬琴"叮—咚"，屏幕熄灭（6.3 秒）时一声梆子
TE = T('END')
place(MUS['yq'], yangqin(jp(1, 1, D5), 4.0, 0.6), TE + 2.4, 0.3)
place(MUS['yq'], yangqin(jp(5, 0, D5), 4.0, 0.6), TE + 2.85, 0.28)
place(MUS['perc'], bangzi(0.8), TE + 6.3, 0.4)
# 片尾"制作与资源"（js/code/making.js，22 秒）：笛子慢慢吹一遍主题，扬琴分解和弦垫着；片名那张卡（19.1 秒起）扬琴"叮—咚"，最后一声梆子
TM = T('MAKING')
BPM_M = 16 * 60 / 16.8                                      # 主题 16 拍，从 0.8 秒吹到 17.6 秒
melody('dizi', mel(THEME_A_DIZI, TM + 0.8, BPM_M, D5, gap=0.03, acc=0.5), 0.38)
yq_chords(TM + 0.8, THEME_ROOTS, BPM_M, 8, 0.22, pattern='arp')
place(MUS['yq'], yangqin(jp(1, 1, D5), 4.0, 0.55), TM + 19.2, 0.3)
place(MUS['yq'], yangqin(jp(5, 0, D5), 4.0, 0.55), TM + 19.65, 0.28)
place(MUS['perc'], bangzi(0.7), TM + 21.0, 0.3)
print(f'  尾声速度 {BPF:.1f} 拍/分，"呛"在 {t4:.2f} 秒（S32 结尾 {T("END"):.2f}），屏幕熄灭梆子 {TE + 6.3:.1f} 秒，全片 {TOTAL - 1:.2f} 秒')

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
# 响度：整体线性增益到 -16 LUFS，再用快速限幅器只削短促的尖峰（停电"啪"、拉灯绳、划火柴、大锣、"呛"），4 倍过采样后限在 -2.5 dBFS（压住采样点之间的峰）。
# 不用 loudnorm 的动态模式（它会把全片的强弱拉平，锣鼓没了冲击力）。限幅会让响度略降，所以按实测再补一次增益。
# 成片 AAC 编码后真峰须 <= -1.5 dBTP，编码后另行复测。
src = os.path.join(OUT, 'film_mix.wav'); dst = os.path.join(OUT, 'film_mix_norm.wav')


def measure(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    tail = r.stderr[r.stderr.rindex('Summary:'):]
    I = float(tail.split('I:')[1].split('LUFS')[0]); tp = float(tail.split('Peak:')[1].split('dBFS')[0])
    return I, tp


I0, tp0 = measure(src); g = -16.0 - I0
for _ in range(2):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-af', f'volume={g:.3f}dB,aresample=192000,alimiter=limit=0.75:attack=5:release=80:asc=1:level=disabled,aresample={SR}',
                    '-ar', str(SR), '-c:a', 'pcm_s16le', dst], check=True)
    I1, tp1 = measure(dst); g += -16.0 - I1
print(f"响度：原 {I0:.2f} LUFS / 真峰 {tp0:.2f} dBTP → {I1:.2f} LUFS / 真峰 {tp1:.2f} dBTP")
print(dst, f'{TOTAL:.1f}s')
