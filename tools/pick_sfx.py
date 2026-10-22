# 把选中入片的 Freesound 录音逐条打开页面核对授权（必须是 CC0 1.0 公有领域），下载 128k 预览 MP3 到 assets/sfx/<名字>.mp3，登记到 assets/sfx/manifest.json。
# 用法：python3 tools/pick_sfx.py
import json, os, re, subprocess, html
PICK = {
    'match': 248236, 'glass': 549899, 'latch': 278205, 'basin': 659438, 'phone_drop': 637747, 'flop': 187136, 'thud_small': 447922,
    'mat': 320144, 'steps_slipper': 176538, 'steps_light': 596537, 'stool': 364988, 'sit': 364985, 'sheet': 389170,
    'cloth': 334219, 'cloth2': 19291, 'leather': 108533, 'clothespin': 624484, 'hook': 489767, 'torch_click': 410360,
    'torch_on': 187335, 'tap': 566685, 'plug_in': 525017, 'plug_out': 477641, 'cord': 591569, 'tv_off': 869534,
    'fluor_start': 145120, 'fluor_hum': 474312, 'fan': 345230, 'rods': 348959, 'knock': 629987, 'bite': 275015,
    'night': 333221, 'frogs': 32655, 'puppy': 583142,
    'girl_yawn': 471859, 'girl_gasp': 471930, 'girl_effort': 471926, 'girl_sigh': 377736, 'girl_giggle': 203230,
    'girl_laugh': 184616, 'girl_laugh2': 119450, 'woman_laugh': 433921, 'woman_laugh2': 93775,
}
os.makedirs('assets/sfx', exist_ok=True)
man = {}
for name, sid in PICK.items():
    h = subprocess.run(['curl', '-sL', '--max-time', '40', f'https://freesound.org/s/{sid}/'], capture_output=True, text=True).stdout
    lic = 'publicdomain/zero/1.0' in h
    mp3 = re.search(r'https://cdn\.freesound\.org/previews/\d+/' + str(sid) + r'_\d+-(?:lq|hq)\.mp3', h)
    title = html.unescape((re.search(r'<title>([^<]*)</title>', h) or [None, ''])[1]).replace(' - Freesound', '').strip()
    user = (re.search(r'/people/([^/"]+)/sounds/' + str(sid), h) or [None, ''])[1]
    if not lic or not mp3:
        print('跳过', name, sid, '授权' if not lic else '没找到预览'); continue
    url = mp3.group(0).replace('-lq.mp3', '-hq.mp3'); f = f'assets/sfx/{name}.mp3'
    if not os.path.exists(f):
        subprocess.run(['curl', '-s', '--max-time', '120', '-o', f, url], check=True)
    man[name] = {'id': sid, 'title': title, 'author': user, 'license': 'CC0 1.0', 'page': f'https://freesound.org/people/{user}/sounds/{sid}/', 'file': f}
    print(name, sid, user, title[:50])
json.dump(man, open('assets/sfx/manifest.json', 'w'), ensure_ascii=False, indent=1)
