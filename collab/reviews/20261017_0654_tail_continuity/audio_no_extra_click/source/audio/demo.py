# 主题小样（约 28 秒）：开场锣鼓 → 板胡奏主题（扬琴、梆子伴奏）→ 笛子加花再奏一遍 → 8-bit 方波和板胡一问一答（电子鼓 + 梆子）→ "呛"
# 运行：python3 audio/demo.py  → build/audio/theme_demo.wav
import sys, os
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(__file__))
from inst import *
from score import *

BPM = 120; SP = 60 / BPM
DUR = 30.0
n = ns(DUR)
L = {k: np.zeros(n, np.float32) for k in ['banhu', 'dizi', 'yq', 'perc', 'chip', 'beat', 'pipa']}

# ---- 开场锣鼓：板鼓越敲越密，小锣跟着，最后"呛"
t = 0.0; gap = 0.30
while t < 2.3:
    place(L['perc'], bangu(0.5 + 0.4 * t / 2.3), t); t += gap; gap = max(0.06, gap * 0.86)
for tt in [1.2, 1.7, 2.0]:
    place(L['perc'], xiaoluo(0.5), tt)
T0 = 2.5
place(L['perc'], qiang(0.9), T0)

def accomp(t0, roots, bars, yq_gain=0.5, bz=True):
    for b in range(bars):
        r = roots[b % len(roots)]; tb = t0 + b * 2 * SP
        place(L['yq'], yangqin(jp(r, -1), 2.0, 0.8), tb, yq_gain)                 # 低音
        for k in range(4):                                                        # 后半拍的和弦音
            tk = tb + (k + 0.5) * SP / 2 * 2 * 0.5 + k * SP * 0.0
        for k, off in enumerate([0.5, 1.5]):
            place(L['yq'], yangqin(jp(r, 0), 1.2, 0.6), tb + off * SP, yq_gain * 0.7)
            place(L['yq'], yangqin(jp(r, 0) * 1.5, 1.2, 0.5), tb + off * SP + 0.01, yq_gain * 0.5)
        if bz:
            place(L['perc'], bangzi(0.9), tb, 0.55); place(L['perc'], bangzi(0.6), tb + SP, 0.35)

# ---- 第一遍：板胡
seq, beats = parse(THEME_A, key=587.33)
L['banhu'] += banhu(to_notes(seq, T0, BPM, gap=0.02), DUR)
accomp(T0, THEME_A_ROOTS, 8)
T1 = T0 + beats * SP
place(L['perc'], xiaoluo(0.7), T1 - SP * 0.5)
# ---- 第二遍：笛子加花，琵琶轮指垫底
seq2, _ = parse(THEME_A_DIZI, key=587.33)
L['dizi'] += dizi(to_notes(seq2, T1, BPM, gap=0.015), DUR)
accomp(T1, THEME_A_ROOTS, 8, yq_gain=0.35, bz=True)
for b in range(8):
    place(L['pipa'], pipa(jp(THEME_A_ROOTS[b], -1), 1.1, 0.5, tremolo=0.9), T1 + b * 2 * SP, 0.35)
T2 = T1 + beats * SP
place(L['perc'], qiang(0.8), T2)
# ---- 第三遍：8-bit 方波奏前四小节，板胡接后四小节；电子底鼓 + 拍手 + 梆子；小狗"汪"
chip = [{'t': T2 + b * SP, 'd': d * SP, 'f': f * 2, 'acc': 0.8} for b, d, f, fl in seq if b < 8]
L['chip'] += chip_lead(chip, DUR, duty=0.25)
L['banhu'] += banhu(to_notes([s for s in seq if s[0] >= 8], T2, BPM, gap=0.02), DUR)
L['chip'] += chip_tri([{'t': T2 + b * 2 * SP + k * SP / 2, 'd': SP / 2, 'f': jp(THEME_A_ROOTS[b], -3 + (k % 2), key=587.33)} for b in range(8) for k in range(4)], DUR)
for b in range(16):
    tb = T2 + b * SP
    place(L['beat'], kick(0.9), tb)
    if b % 2:
        place(L['beat'], clap(0.6), tb)
    place(L['beat'], chip_noise(0.08, 0.3), tb + SP / 2)
    place(L['perc'], bangzi(0.7), tb + SP * 0.75, 0.3)
for tt in [T2 + 8 * SP + SP * 1.5, T2 + 10 * SP + SP * 1.5, T2 + 14 * SP + SP * 0.5, T2 + 14 * SP + SP * 1.0]:
    place(L['chip'], woof(0.7), tt)
T3 = T2 + beats * SP
place(L['perc'], qiang(0.9), T3)

# ---- 混音：声像、音量、混响
mix = (pan(L['banhu'] * 0.55, 0.15) + pan(L['dizi'] * 0.5, -0.1) + pan(L['yq'] * 0.35, -0.35) + pan(L['pipa'] * 0.4, 0.35)
       + pan(L['perc'] * 0.6, 0.05) + pan(L['chip'] * 0.35, 0.0) + pan(L['beat'] * 0.5, 0.0))
mix = reverb(mix, reverb_ir(1.1), wet=0.22)
mix = mix / np.abs(mix).max() * 0.89
out = os.path.join(os.path.dirname(__file__), '..', 'build', 'audio', 'theme_demo.wav')
wavfile.write(out, SR, (mix * 32767).astype(np.int16))
print(out, f'{DUR}s')
