# 配乐的谱子：主题旋律、伴奏型，以及把简谱变成音符的小工具。
# 简谱写法（空格分开，| 只是小节线，不起作用）：
#   5:0.5   = 5，半拍；   1':1 = 高音 1，一拍；   6,:1 = 低音 6；   0:0.5 = 休止半拍
#   后缀：~ 滑进来   ^ 前倚音（从上方邻音落下）   ! 重音   t 颤音   = 和前一个音连着（连弓/不吐音）   v 揉弦加深
import re
from inst import jp

# 主题：开头两个音"叮—咚"（高音 1 落到 5，像门铃，也像手机的来电提示），后面一串五声音阶的碎步。1 = D。
THEME_A = """
1':0.5! 5:0.5 6:0.25 1':0.25 6:0.25 5:0.25 | 3:0.5 5:0.5 6~:1v |
1':0.5! 5:0.5 6:0.25 5:0.25 3:0.25 2:0.25 | 1:0.5 2:0.5 3:1v |
5:0.75! 3:0.25 2:0.5 3:0.5 | 5:0.5 6:0.5 1'^:1v |
6:0.25 1':0.25 6:0.25 5:0.25 3:0.5 2:0.5 | 1:1.5v 0:0.5
"""
# 每小节的根音（伴奏用）
THEME_A_ROOTS = [1, 6, 1, 3, 5, 6, 5, 1]

# 主题的"笛子版"：同一条旋律加花（倚音、颤音、连音）
THEME_A_DIZI = """
1'^:0.5! 5:0.5 6:0.25 1':0.25= 6:0.25= 5:0.25 | 3:0.5 5:0.5 6t:1 |
1'^:0.5! 5:0.5 6:0.25 5:0.25= 3:0.25= 2:0.25 | 1:0.5 2:0.5 3t:1 |
5:0.75! 6:0.125= 5:0.125= 3:0.25 2:0.5 3:0.5 | 5:0.5 6:0.5 1'^:1 |
6:0.25 1':0.25= 6:0.25= 5:0.25 3:0.5 2:0.5 | 1:1.5 0:0.5
"""

TOKEN = re.compile(r"^(\d)([',]*)([~^!t=v]*)(?::([\d.]+))?([~^!t=v]*)$")


def parse(text, key=587.33, oct=0):
    """简谱 → [(拍位置, 拍数, 频率或 None, 记号)]"""
    out, beat = [], 0.0
    for tok in text.replace('|', ' ').split():
        m = TOKEN.match(tok)
        if not m:
            raise ValueError(tok)
        deg, marks, d, flags = int(m.group(1)), m.group(2), float(m.group(4) or 1), m.group(3) + m.group(5)
        if deg == 0:
            beat += d; continue
        o = oct + marks.count("'") - marks.count(',')
        out.append((beat, d, jp(deg, o, key), flags))
        beat += d
    return out, beat


def to_notes(seq, t0, bpm, gap=0.0, acc=0.75):
    """拍 → 秒，给旋律线合成器用的音符；gap 是每个音后面留的空（断奏）"""
    sp = 60.0 / bpm
    notes = []
    for b, d, f, fl in seq:
        n = {'t': t0 + b * sp, 'd': d * sp - gap, 'f': f, 'acc': acc + (0.2 if '!' in fl else 0)}
        if '~' in fl:
            n['slide'] = 0.12
        if '=' in fl:
            n['legato'] = True; n['d'] = d * sp
        if '^' in fl:
            n['grace'] = f * 2 ** (2 / 12)
        if 't' in fl:
            n['trill'] = f * 2 ** (2 / 12)
        if 'v' in fl:
            n['vib'] = 1.8; n['swell'] = 1
        notes.append(n)
    # 连着的音：前一个音的长度补满
    return notes
