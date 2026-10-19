from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
P=Path(__file__).resolve().parent;PACK=P.parent;F=P/'F032';I=F/'inputs';Q=F/'qa'
info=json.loads((F/'source_and_geometry.json').read_text());source=Path(info['accepted_actual020'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)==info['accepted_actual020_sha256']
A=np.array(Image.open(source).convert('RGBA'));C=np.array(Image.open(F/'art/adult_R_release_volume.png').convert('RGBA'))
M=np.array(Image.open(I/'04_release_only_edit_white.png'))>0;clear=np.array(Image.open(F/'art/old_R_palm_forearm_clear.png'))>0
out=A.copy();out[clear]=0
# Tail continuations reveal only the previously hidden original straight shafts.
reg=json.loads((PACK/'F000/f000_scene_gate_001/registration_input.json').read_text())
tail=Image.new('RGBA',(1672*4,941*4));d=ImageDraw.Draw(tail)
for role in ['T_H','T_S']:
 r=reg['rods'][role];pts=[(x*4,(r['slope']*x+r['intercept'])*4) for x in [885,944]]
 d.line(pts,fill='#675034',width=13);d.line(pts,fill='#b28b52',width=8)
tail=tail.resize((1672,941),Image.Resampling.LANCZOS)
layer=Image.new('RGBA',(1672,941));layer.alpha_composite(tail);layer.alpha_composite(Image.fromarray(C))
L=np.array(layer);take=M&(L[:,:,3]>0)
out[take]=L[take]
assert not np.any(out[~M]!=A[~M]) and np.array_equal(out[:,:885],A[:,:885])
Image.fromarray(out).save(I/'01_F032_release_target_child020_exact.png')
Image.fromarray(C).save(F/'art/release_volume_raster.png')
box=(770,385,1115,540);im=Image.fromarray(out);im.crop(box).resize((1380,620),Image.Resampling.NEAREST).save(I/'02_release_same_view_4x.png')
bg=Image.new('RGBA',im.size,'#bec2c5');bg.alpha_composite(im);bg=bg.convert('RGB');bg.save(Q/'release_target_full_gray.png')
bg.crop(box).resize((1380,620),Image.Resampling.NEAREST).save(Q/'release_target_detail_4x.png')
# Diagnostic for the new open palm and finger clearance; guide raster only.
rod=np.array(Image.open(F/'art/source_visible_rod_protection.png'))>0
D=distance_transform_edt(~((rod&(A[:,:,3]>100))|(np.array(tail)[:,:,3]>100)))
hm=np.zeros(M.shape,bool);hm[435:530,910:1017]=C[435:530,910:1017,3]>180
assert not np.any(hm&~M),'New palm must remain inside approved release white.'
gaps=float(D[hm].min());assert gaps>5,gaps
prompt='''把第一张完整F032放握新姿态自然完稿。第一张是唯一完整动作底，来自已经通过的020实物：孩子全片、两只实握手与两杆轴线、头身腿脚、奶奶高位带玉镯L臂和两鹤签均保持原像素；只把奶奶低位裸腕远R供应掌改成已张开撤离。原低R闭掌/旧前臂占位已清，第一张已有连续新远前臂与真实拇指加四指开掌轮廓。不得改回闭拳或添回原供应掌。第二张只从第一张放握区直接4倍放大。第三张只有奶奶头部与内部布/肤/发裁片，不含完整旧臂或旧全身。第四张唯一白可完稿、黑保持原RGBA，不反转语义。
动作因果：020孩子两接收握点已稳，032仍由X.R夹T_H（龟head[20,0]）、X.L握T_S（龟shell[0,40]），两手、指腹对握、腕臂和杆轴按第一张完全不动。奶奶远R原肩(1067,285)→隐在躯干后的肘(1091.357,433.283)→腕(1012,480)，张开掌中心(978,487)，完整前臂带腕向右下撤离；只有远臂正常露出的部分可见，隐藏上臂/肘不能画透到前襟。拇指与四指全部自然张开，与两龟签均留清楚空气，G.R接触数0，不能捏住任何一签或只松拇指。
两根龟签各自沿原真实硬直轴到独立后端，清除旧掌后应露出的杆段必须接回原轴，不折杆、不软结、不合成一签、不换偶端，杆不穿掌。已过020整张孩子及双握接触、原鞋踝、奶奶高L全臂/玉镯/两鹤签、头颈躯干及黑域可见杆原像素全部保持。孩子不得随奶奶放手漂移、重画或缩放。不是新动作插帧，也不改变高鹤接景、灯或相机。
只将白域内简化施工体量自然完稿为第一/三张相同二维手绘风格：完整袖口后方臂链、肘腕过渡、掌厚和五指真实，保自然体积与中性固有色，不用圆圈/胶囊假手，不留旧臂双边或旧掌残影。严格1672×941透明两人四杆人物层，仅本态；无文字、骨架、透衣线、场景、偶、灯光、影子或其他帧，不裁切、补边或缩放角色。'''
roles=[('01_F032_release_target_child020_exact.png','unique complete release pose, accepted020 child and grips exact'),('02_release_same_view_4x.png','exact direct same-view release crop4x'),('03_grandma_head_internal_materials_only.png','grandma head/material crop only'),('04_release_only_edit_white.png','release-only white; child/grips and highL source-black protection')]
rows=[]
for n,(name,role) in enumerate(roles,1):
 f=I/name;rows.append({'order':n,'path':str(f.resolve()),'sha256':sha(f),'size':list(Image.open(f).size),'role':role})
args={'prompt':prompt,'transparent_background':True,'referenced_image_paths':[r['path'] for r in rows]}
(F/'prompt_prepared_zh.txt').write_text(prompt+'\n');(F/'tool_args_prepared.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
(F/'input_manifest.json').write_text(json.dumps({'inputs':rows,'source_accepted_actual020_sha256':sha(source),'whole_child_RGBA_changes_in_target':0,'black_domain_RGBA_changes_in_target':0,'target_G_R_open_hand_to_visible_rods_clearance_px':gaps,'submitted':False},ensure_ascii=False,indent=2)+'\n')
print('F032 four real inputs prepared; actual020 whole child/grips exact, G.R open hand clearance',gaps,'px; no model call yet.')
