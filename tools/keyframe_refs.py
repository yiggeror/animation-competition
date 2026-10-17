# 关键帧的骨架参考图：在淡化的母版图上画出这一帧的目标姿势（骨长按母版量，手臂用两节 IK 解，保证每帧骨长一致），
# 并写上帧号、时间、表情要点。给合作方生图时照着画姿势、审查时核对动作用。
# 用法：python3 -I tools/keyframe_refs.py S18   → renders/keyframes/S18/k01.png … 和 sheet.jpg
import json
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

shot = sys.argv[1]
spec = json.load(open(f'docs/keyframes/{shot}.json', encoding='utf-8'))
master = Image.open(spec['master']).convert('RGBA')
W, H = master.size
font = ImageFont.truetype('assets/fonts/NotoSansSC-VF.ttf', 26)
small = ImageFont.truetype('assets/fonts/NotoSansSC-VF.ttf', 20)
J0 = spec['joints']                     # 母版关节（像素）
L = lambda a, b: math.dist(J0[a], J0[b])
ARM = {s: (L(f'sh_{s}', f'el_{s}'), L(f'el_{s}', f'wr_{s}'), L(f'wr_{s}', f'hd_{s}')) for s in ('n', 'f')}


def ik(sh, target, l1, l2, bend):
    """两节 IK：肩 sh、腕的目标 target、上臂 l1、前臂 l2，bend=+1/-1 选肘往哪边弯"""
    dx, dy = target[0] - sh[0], target[1] - sh[1]
    d = min(math.hypot(dx, dy), l1 + l2 - 1e-3)
    a = math.atan2(dy, dx)
    c = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    b = math.acos(max(-1, min(1, c)))
    el = (sh[0] + l1 * math.cos(a + bend * b), sh[1] + l1 * math.sin(a + bend * b))
    wr = (sh[0] + d * math.cos(a), sh[1] + d * math.sin(a))
    return el, wr


out = Path(f'renders/keyframes/{shot}'); out.mkdir(parents=True, exist_ok=True)
thumbs = []
for k, kf in enumerate(spec['keys'], 1):
    J = dict(J0)
    # 身体：肩膀整体上下（耸肩）、头绕颈根转（度，正 = 低头/顺时针）
    lift = kf.get('shoulder_lift', 0)
    for s in ('n', 'f'):
        J[f'sh_{s}'] = (J0[f'sh_{s}'][0], J0[f'sh_{s}'][1] - lift)
    J['neck'] = (J0['neck'][0], J0['neck'][1] - lift * 0.6)
    ha = math.radians(kf.get('head_rot', 0))
    hx, hy = J0['head'][0] - J0['neck'][0], J0['head'][1] - J0['neck'][1]
    J['head'] = (J['neck'][0] + hx * math.cos(ha) - hy * math.sin(ha), J['neck'][1] + hx * math.sin(ha) + hy * math.cos(ha))
    nose_dir = math.radians(spec['nose_deg'] + kf.get('head_rot', 0))
    # 手：给手腕目标位置，IK 解肘；手掌方向（度）
    for s in ('n', 'f'):
        if f'wr_{s}' in kf:
            l1, l2, l3 = ARM[s]
            el, wr = ik(J[f'sh_{s}'], kf[f'wr_{s}'], l1, l2, kf.get(f'bend_{s}', 1))
            J[f'el_{s}'], J[f'wr_{s}'] = el, wr
            hd = math.radians(kf.get(f'hand_deg_{s}', 0))
            J[f'hd_{s}'] = (wr[0] + l3 * math.cos(hd), wr[1] + l3 * math.sin(hd))
    # 画：淡化的母版 + 骨架
    img = Image.new('RGBA', (W, H + 150), (255, 255, 255, 255))   # 文字条放在图下面，不挡脚和凳子
    faded = master.copy(); faded.putalpha(faded.getchannel('A').point(lambda v: v * 0.28))
    img.alpha_composite(faded)
    d = ImageDraw.Draw(img)
    def bone(a, b, col, w=10):
        d.line([J[a], J[b]], fill=col, width=w); d.ellipse([J[b][0] - 7, J[b][1] - 7, J[b][0] + 7, J[b][1] + 7], fill=col)
    d.line([J['pelvis'], J['neck']], fill=(40, 40, 40), width=12)
    for s, col in (('f', (90, 120, 220)), ('n', (220, 60, 60))):
        d.line([J['neck'], J[f'sh_{s}']], fill=col, width=8)
        bone(f'sh_{s}', f'el_{s}', col); bone(f'el_{s}', f'wr_{s}', col); bone(f'wr_{s}', f'hd_{s}', col, 14)
    d.line([J['pelvis'], J['knee']], fill=(60, 60, 60), width=10); d.line([J['knee'], J['ankle']], fill=(60, 60, 60), width=10)
    r = spec['head_r']; c = J['head']
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=(30, 30, 30), width=6)
    d.line([c, (c[0] + r * 1.15 * math.cos(nose_dir), c[1] + r * 1.15 * math.sin(nose_dir))], fill=(30, 30, 30), width=6)   # 鼻子朝向
    # 两个不动的定位点（绿色十字，每张关键帧都标在同样的地方）
    for i, (ax, ay) in enumerate(spec.get('anchors', {}).get('points', []), 1):
        d.line([(ax - 16, ay), (ax + 16, ay)], fill=(20, 160, 60), width=4); d.line([(ax, ay - 16), (ax, ay + 16)], fill=(20, 160, 60), width=4)
        d.text((ax + 10 if ax < W - 60 else ax - 40, ay - 36), f'A{i}', font=small, fill=(20, 140, 50))
    f = f"第 {kf['f']} 帧，" if 'f' in kf else ''
    d.text((16, H + 8), f"{shot} 关键帧 {k:02d}  {f}{kf['t']:.2f} 秒", font=font, fill=(0, 0, 0))
    for i, line in enumerate([kf['note'][j:j + 26] for j in range(0, len(kf['note']), 26)][:4]):
        d.text((16, H + 44 + i * 26), line, font=small, fill=(40, 40, 40))
    img.convert('RGB').save(out / f'k{k:02d}.png')
    thumbs.append(img.convert('RGB').resize((W // 3, (H + 150) // 3)))
# 总览
cols = 6; rows = math.ceil(len(thumbs) / cols); tw, th = thumbs[0].size
sheet = Image.new('RGB', (cols * tw, rows * th), 'white')
for i, t in enumerate(thumbs): sheet.paste(t, ((i % cols) * tw, (i // cols) * th))
sheet.save(out / 'sheet.jpg', quality=88)
print(out, len(thumbs))
