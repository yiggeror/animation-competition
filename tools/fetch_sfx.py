# 从 Freesound 搜公有领域（CC0 1.0）录音做音效和人声候选：每个用途搜一两个关键词，按下载量取前几条，下载 128k 预览 MP3。
# 用法：python3 tools/fetch_sfx.py [键名...]   → assets/sfx/cand/<键>_<id>.mp3 和 assets/sfx/cand/index.json（id、作者、标题、时长、链接）
# 只用搜索页上的 CC0 过滤结果；选中入片的每一条另在 assets/sfx/manifest.json 里登记，并核对过页面上的授权。
import json, os, re, subprocess, sys, html, urllib.parse
OUT = 'assets/sfx/cand'
Q = {
    # 屋里的动作
    'match': (['match strike light'], 8), 'glass': (['glass clink small'], 3), 'latch': (['metal latch click'], 3),
    'basin': (['metal bowl put down'], 3), 'phone_drop': (['phone drop on bed', 'phone put down table'], 3),
    'flop': (['body fall on bed', 'flop on mattress'], 4), 'mat': (['straw mat rustle', 'bamboo mat'], 6),
    'steps_slipper': (['slippers footsteps'], 15), 'steps_light': (['footsteps barefoot tile', 'light footsteps'], 15),
    'stool': (['wooden stool drag', 'chair drag wood floor'], 4), 'sit': (['sit down wooden chair'], 3),
    'sheet': (['bed sheet shake', 'fabric flap'], 4), 'cloth': (['cloth rustle'], 6), 'leather': (['parchment rustle', 'leather rustle'], 5),
    'clothespin': (['clothespin'], 6), 'wire': (['metal wire rattle'], 4), 'hook': (['metal hook clink'], 4),
    'torch_click': (['flashlight click'], 3), 'tap': (['plastic tap hand', 'flashlight hit'], 4), 'plug': (['plug socket'], 5),
    'cord': (['pull cord light switch'], 4), 'power_off': (['crt tv turn off', 'power outage'], 4), 'tv_on': (['crt tv turn on'], 6),
    'fluor': (['fluorescent light turn on'], 10), 'fan': (['ceiling fan'], 120), 'pod': (['pea pod snap', 'snapping peas'], 8),
    'bean_drop': (['beans drop bowl', 'small object drop metal bowl'], 4), 'rods': (['bamboo sticks clack', 'chopsticks tap'], 4),
    'box_thud': (['flashlight put down', 'object put down wood table'], 3), 'bite': (['watermelon bite', 'apple bite'], 3),
    'night': (['summer night crickets', 'crickets night'], 300), 'frogs': (['frogs night'], 300),
    # 人声（无台词，只有语气）
    'girl_giggle': (['little girl giggle', 'child giggle'], 6), 'girl_laugh': (['little girl laughing'], 8),
    'girl_yawn': (['child yawn', 'girl yawn'], 5), 'girl_sigh': (['child sigh', 'girl sigh'], 4), 'girl_hmph': (['girl hmph', 'child humph'], 3),
    'girl_gasp': (['child gasp', 'girl gasp surprise'], 3), 'girl_groan': (['child groan', 'girl frustrated'], 4),
    'girl_woof': (['child imitating dog bark', 'kid woof'], 4), 'grandma_laugh': (['old woman laugh', 'elderly woman laughing'], 8),
    'grandma_chuckle': (['old woman chuckle'], 5),
    # 第二轮：第一轮没搜到或不合用的
    'basin2': (['metal bowl', 'enamel pot set down'], 3), 'flop2': (['fall on bed', 'jump on bed'], 4), 'mat2': (['rattan mat', 'tatami'], 8),
    'sit2': (['sitting down chair', 'sit on stool'], 3), 'hook2': (['metal clank small', 'lantern'], 4), 'tv_on2': (['tv turn on static', 'old television on'], 6),
    'fluor2': (['fluorescent lamp', 'fluorescent tube flicker'], 15), 'bean2': (['pebbles drop bowl', 'peas pour bowl'], 4),
    'rods2': (['wooden sticks hit', 'drumsticks click'], 3), 'thud2': (['put down object table', 'wood knock'], 2),
    'grandma2': (['grandmother laugh', 'old lady laughing', 'senior woman laugh'], 8), 'grandma3': (['woman chuckle', 'warm laugh woman'], 4),
    'woof2': (['girl barking like dog', 'child bark imitation', 'kid says woof'], 4), 'girl_hum': (['girl hum', 'child mm hmm'], 3),
    'child_laugh2': (['girl laughing short', 'kid laughing'], 5),
}


def search(q):
    url = 'https://freesound.org/search/?' + urllib.parse.urlencode({'q': q, 'f': 'license:"Creative Commons 0"', 's': 'Downloads (most first)'})
    h = subprocess.run(['curl', '-s', '--max-time', '40', url], capture_output=True, text=True).stdout
    out = []
    for m in re.finditer(r'data-sound-id="(\d+)"', h):
        seg = h[m.start():m.start() + 4000]
        g = lambda k: (re.search(k + r'="([^"]*)"', seg) or [None, None])[1]
        user = re.search(r'/people/([^/]+)/sounds/' + m.group(1), h)
        mp3 = g('data-mp3')
        if not mp3 or any(o['id'] == m.group(1) for o in out):
            continue
        out.append({'id': m.group(1), 'user': user.group(1) if user else '', 'title': html.unescape(g('data-title') or ''),
                    'dur': float(g('data-duration') or 0), 'downloads': int(g('data-num-downloads') or 0), 'hq': mp3.replace('-lq.mp3', '-hq.mp3'),
                    'page': f"https://freesound.org/people/{user.group(1) if user else ''}/sounds/{m.group(1)}/", 'query': q})
    return out


os.makedirs(OUT, exist_ok=True)
idx_path = os.path.join(OUT, 'index.json')
index = json.load(open(idx_path)) if os.path.exists(idx_path) else {}
keys = sys.argv[1:] or list(Q)
for k in keys:
    qs, maxdur = Q[k]; got = []
    for q in qs:
        got += [r for r in search(q) if 0.2 < r['dur'] <= maxdur and r['id'] not in {g['id'] for g in got}]
    got = sorted(got, key=lambda r: -r['downloads'])[:4]
    for r in got:
        f = os.path.join(OUT, f"{k}_{r['id']}.mp3")
        if not os.path.exists(f):
            subprocess.run(['curl', '-s', '--max-time', '120', '-o', f, r['hq']])
        r['file'] = f
    index[k] = got
    print(k, ' | '.join(f"{r['id']} {r['title'][:28]} {r['dur']:.1f}s" for r in got))
    json.dump(index, open(idx_path, 'w'), ensure_ascii=False, indent=1)
