"""Author static correction guides and explicit masks; never call an image model."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import base64, hashlib, json
import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'generation_001/S20_F000_call001_raw.png'
SIZE = (1672, 941)
RAW_SHA = 'de1aec591119393f7f99a61a166f62e9af456ce24ffd718fec0429b20fe2e330'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == RAW_SHA
for name in ['masks', 'svg', 'qa']:
    (ROOT / name).mkdir(exist_ok=True)
raw = Image.open(SOURCE).convert('RGBA')
assert raw.size == SIZE

def save_json(name, obj):
    (ROOT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def polygon(points):
    im = Image.new('L', SIZE)
    ImageDraw.Draw(im).polygon(points, fill=255)
    return im

left_hand = [(890,281),(940,280),(960,294),(975,318),(992,327),
             (998,340),(991,364),(976,379),(954,374),(941,358),
             (915,357),(897,344),(889,318)]
right_hand = [(899,428),(912,423),(912,419),(923,417),(934,413),
              (945,414),(963,419),(978,421),(978,453),
              (981,454),(968,460),(958,466),(945,474),(932,475),
              (921,472),(914,468),(912,463),(906,460),(902,452),
              (897,447),(896,436)]
protect_L = polygon(left_hand)
protect_R = polygon(right_hand)
rods = Image.new('L', SIZE)
d = ImageDraw.Draw(rods)
front_segments = {
    'CN': [(826,79),(921,300)], 'CB': [(792,111),(906,299)],
    'TH': [(787,343),(914,431)], 'TS': [(774,388),(912,438)],
}
for ends in front_segments.values():
    d.line(ends, fill=255, width=9)
hands_rods = np.maximum.reduce([np.array(protect_L), np.array(protect_R), np.array(rods)])
Image.fromarray(hands_rods).save(ROOT/'masks/protect_palms_bracelet_front_rods.png')
protect_L.save(ROOT/'masks/protect_L_palm_bracelet.png')
protect_R.save(ROOT/'masks/protect_R_palm.png')
rods.save(ROOT/'masks/protect_four_front_rods.png')

# Full corridors include old limb occupancy, new limb volume and sleeve roots.
corridors = [
    [(980,332),(1048,347),(1053,419),(1014,425),(979,376)],
    [(978,414),(1110,405),(1146,369),(1187,381),(1166,454),(1112,468),(978,467)],
    [(1080,250),(1174,249),(1198,282),(1197,412),(1164,451),
     (1103,457),(980,380),(977,332),(1017,332),(1088,372),(1088,316)],
    [(1033,270),(1077,251),(1132,271),(1135,463),(1018,469),
     (978,459),(978,413),(1023,404),(1026,329)],
    [(948,465),(974,465),(976,483),(948,483)],
]
edit = np.maximum.reduce([np.array(polygon(p)) for p in corridors])
protected = Image.new('L', SIZE)
pd = ImageDraw.Draw(protected)
pd.rectangle((0,0,834,940), fill=255)  # Complete child and surrounding gap.
pd.rectangle((0,485,1671,940), fill=255)  # Waist / trousers / shoes fixed.
pd.rectangle((0,0,1671,246), fill=255)  # Head, hair, face and high neck fixed.
pd.polygon([(1065,214),(1137,212),(1140,251),(1100,279),(1071,267)], fill=255)
protected = np.maximum(np.array(protected), hands_rods)
edit[protected > 0] = 0
edit = np.where(edit > 0, 255, 0).astype('uint8')
Image.fromarray(edit).save(ROOT/'masks/edit_white.png')
Image.fromarray(255-edit).save(ROOT/'masks/protect_white.png')
clear_old = np.maximum.reduce([np.array(polygon(corridors[i])) for i in [0,1,4]])
clear_old[edit==0]=0
Image.fromarray(clear_old).save(ROOT/'masks/clear_old_limb_occupancy.png')

# Measure the two existing turtle front axes from opaque bamboo pixels only.
a = np.array(raw); rgb = a[:,:,:3].astype(float)
axis_fits = {}
for role, upper in [('TH',True),('TS',False)]:
    samples=[]
    for x in range(800,881):
        yy = np.arange(330,445)
        good = ((a[yy,x,3]>100) & (rgb[yy,x,0]>rgb[yy,x,1]+15)
                & (rgb[yy,x,1]>rgb[yy,x,2]+15))
        ys=yy[good]
        separator=(0.70*x-209+0.375*x+97)/2
        ys=ys[ys<separator] if upper else ys[ys>separator]
        if len(ys): samples.append((x,float(np.median(ys))))
    slope,intercept=np.polyfit(np.array(samples)[:,0],np.array(samples)[:,1],1)
    axis_fits[role]={'slope':float(slope),'intercept':float(intercept),
                    'fit_columns':[800,880],'sample_count':len(samples),
                    'y_at_x960':float(slope*960+intercept),
                    'hidden_end_under_palm':[944,float(slope*944+intercept)],
                    'target_exposed_tail_added':False}

near_path = ('M 1108 380 C 1106 388 1100 396 1096 397 '
             'C 1068 383 1028 358 994 344 L 980 372 '
             'C 1019 393 1059 420 1101 439 '
             'Q 1129 452 1149 429 Q 1165 411 1174 395 Z')
far_path = ('M 1049 340 Q 1046 374 1053 407 Q 1056 423 1041 426 '
            'Q 1014 425 975 429 L 975 461 Q 1010 462 1047 461 Q 1098 466 1100 433 '
            'L 1102 345 Z')
far_sleeve = ('M 1062 264 Q 1034 281 1030 315 L 1027 357 '
              'Q 1067 368 1102 353 L 1106 300 Q 1102 272 1085 264 Z')
torso = ('M 1077 249 Q 1051 270 1041 310 L 1028 397 '
         'L 1027 488 L 1208 488 L 1196 389 L 1191 297 '
         'Q 1176 258 1138 244 L 1102 274 Z')
near_sleeve = ('M 1135 247 Q 1167 252 1181 279 Q 1195 316 1180 400 '
               'L 1097 380 Q 1101 326 1119 285 Q 1122 259 1135 247 Z')

def path(d, fill, stroke='#594b46', width=1.4, extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" {extra}/>'

def flowers():
    out=[]
    for x,y in [(1053,354),(1068,416),(1098,458),(1155,474),(1154,294),
                (1131,341),(1170,363),(1077,293),(1123,389)]:
        for dx,dy in [(-4,0),(4,0),(0,-4),(0,4)]:
            out.append(f'<ellipse cx="{x+dx}" cy="{y+dy}" rx="2.6" ry="3.1" fill="#f0f4f4"/>')
    return ''.join(out)

far = path(far_sleeve,'#86a9c8') + path(far_path,'#e7bea4')
near = path(near_path,'#f5c7a5') + path(near_sleeve,'#8dafd0')
near += path('M 1108 418 Q 1117 418 1124 408','none','#ab826b',1)
torso_layer = path(torso,'#8caed0') + flowers()
torso_layer += path('M 1051 313 Q 1040 383 1042 486','none','#4e657a',1.1)
torso_layer += path('M 1191 399 L 1202 487','none','#4e657a',1.1)
header = '<svg xmlns="http://www.w3.org/2000/svg" width="1672" height="941" viewBox="0 0 1672 941">'
(ROOT/'svg/arm_volume_layers.svg').write_text(header+far+torso_layer+near+'</svg>')

# X-ray: full far limb volume is visible beneath a translucent torso plane.
# This is an anatomical construction reference, not a proposed skin layer.
source_uri='data:image/png;base64,'+base64.b64encode(SOURCE.read_bytes()).decode()
hand_mask_uri='data:image/png;base64,'+base64.b64encode((ROOT/'masks/protect_palms_bracelet_front_rods.png').read_bytes()).decode()
xray = header + '<defs><mask id="hands"><image width="1672" height="941" href="'+hand_mask_uri+'"/></mask></defs>'
xray += '<rect width="1672" height="941" fill="#e6e7e8"/>'
xray += far
xray += '<g opacity="0.23">'+torso_layer+'</g>'
xray += near
xray += '<image width="1672" height="941" href="'+source_uri+'" mask="url(#hands)"/>'
xray += '<g fill="none" stroke-width="2">'
xray += '<path d="M1067 285 L1076 435 L984 439" stroke="#7c628c" stroke-dasharray="6 4"/>'
xray += '<path d="M1148 283 L1120 419 L986 352" stroke="#2c6f76" stroke-dasharray="6 4"/>'
xray += '</g></svg>'
(ROOT/'svg/full_arm_volume_xray.svg').write_text(xray)

save_json('geometry_and_protection.json',{
    'source_commit':'300840f48aaa8fec60f2392bc16beb28e0a963e1',
    'source_raw':'../generation_001/S20_F000_call001_raw.png','source_sha256':RAW_SHA,
    'canvas':list(SIZE),'image_generation_calls_this_round':0,'submitted':False,
    'near_L':{'shoulder':[1148,283],'elbow':[1120,419],'wrist':[986,352],
              'palm_center':[938,323],'single_jade_bracelet':'unchanged original pixels',
              'holders':['CN','CB'],'volume_path':near_path},
    'far_R':{'shoulder':[1067,285],'elbow':[1076,435],'wrist':[984,439],
             'palm_center':[944,446],'holders':['TH','TS'],
             'upper_arm_and_elbow':'behind torso; full volume shown in xray',
             'volume_path':far_path},
    'layer_order':['far_R full sleeve/upper arm/elbow/forearm','front torso',
                   'near_L upper arm/forearm and near sleeve','unchanged source palms/bracelet/front rods'],
    'joint_positions':'Projected construction anchors, not measured 3D joints',
    'frozen_front_segments':front_segments,'low_turtle_axis_fits':axis_fits,
    'tail_correction':'Remove the displaced exposed R-hand tails; both corrected ends terminate under opaque palm at x944. Do not add visible tails.',
    'preserve_child':'All original pixels, no scale or translation',
    'size_ratio_note':'Astra approx child/adult 0.82 vs construction0.88: defer registration review; do not lock size or scale child now.',
    'deferred_same_raw_items':['neck-side semantic dewarming only after core arm gate',
                               'only isolated outside alpha1 points; preserve rod/hair anti-alias'],
    'white_mask_meaning':'255 editable,0 protected; inverse protection mask white means protect',
    'L_hand_protection_polygon':left_hand,'R_hand_protection_polygon':right_hand,
    'edit_corridors':corridors,'not_a_generated_character_output':True,
})
print('Static two-arm volume SVG and explicit 1672x941 masks prepared. Model calls:0.')
