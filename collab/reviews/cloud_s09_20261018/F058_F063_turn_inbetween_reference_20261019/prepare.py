from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,math,hashlib
R=Path(__file__).resolve().parent;B=R.parent;P=B/'F063_zero_call_semantic_reintegration_20261019';size=(1672,941);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:Image.open(p).convert('RGBA');mask=lambda p:np.array(Image.open(p).convert('L'))>0
end=load(P/'candidate/F063_zero_call_semantic_RECONNECTED.png');a=np.array(end);start=load(B/'F058_reuse_locked044_gate/candidate/F058_exact_LOCKED044_REUSE_PENDING_ASTRA.png');g=json.loads((B/'F063_full_grip_shape_repair_gate_20261019/sources/F063_frozen_target_geometry_REFERENCE.json').read_text());M=np.array(g['unit_M']);t=np.array(g['unit_t']);T=np.array(g['T_target']);L=np.array(g['L_target']);G=np.array(g['G_target']);T0=M.T@(T-t);L0=M.T@(L-t);Tm=(T+T0)/2;angle=-math.radians(78.508/2);m=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]]);u=m@(L-T);Gm=Tm+.5186170239855135*u;tm=Gm-m@G;iv=m.T;it=-iv@tm
# Entire current grip and real rigid prop travel together as ONE SOFT group.
# No wrist/digit warp; the real complete new near chain will need native drawing.
yy,xx=np.indices(a.shape[:2]);near=mask(P/'masks/NEW_complete_near_skin_chain_FRONT_of_prop.png');hand=near&(xx>=965);prop=mask(P/'masks/KEEP_known_true_prop_AFTER_new_hand_occlusion.png')|mask(P/'masks/KEEP_actual_returned_unknown_cylinder_material_only.png');group=Image.fromarray(np.where((hand|prop)[:,:,None],a,0).astype('uint8'));midgroup=group.transform(size,Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),Image.Resampling.BICUBIC,fillcolor=0);midgroup.save(R/'layers/WHOLE_actual_hand_and_prop_Rminus39_254_SCALE1_SOFT_NOT_ART.png')
# A proposal diagram only: whole arm corridors and exposed source vacancies
# are deliberately blue/gray technical material, never final code people.
base=np.array(end);vacant=near|prop;base[vacant]=[191,208,218,255];mid=Image.fromarray(base);d=ImageDraw.Draw(mid);N=np.array([705.,666.]);E=np.array([815.,720.]);W=m@np.array([980.,651.])+tm
for p,q,r1,r2 in [(N,E,30,38),(E,W,38,24)]:
 v=q-p;v=np.array([-v[1],v[0]])/np.linalg.norm(v);d.polygon([tuple(p+v*r1),tuple(q+v*r2),tuple(q-v*r2),tuple(p-v*r1)],fill='#a3cee1',outline='#3e6d86',width=2)
d.ellipse((E[0]-38,E[1]-38,E[0]+38,E[1]+38),fill='#a3cee1',outline='#3e6d86',width=2);mid.alpha_composite(midgroup)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 sheet=Image.new('RGB',(2508,500),(235,240,245));ds=ImageDraw.Draw(sheet)
 for j,(name,z)in enumerate([('F058 ACTUAL LOCKED044 / start',start),('UNTIMED MID / TECHNICAL NOT_ART',mid),('F063 ACTUAL RECONNECTED / end',end)]):
  bg=Image.new('RGBA',size,col);bg.alpha_composite(z);sheet.paste(bg.resize((836,470)).convert('RGB'),(j*836,30));ds.text((j*836+8,5),name,font=font,fill='#315269')
 sheet.save(R/f'reference/058_MID_NOT_ART_063_{tone}.png')
rec={'state':'ONE_NECESSARY_TURN_MID_REFERENCE_UNTIMED_NOT_ART_NOT_A_CALL','cause':'Actual058x5→063x6 decoded11f shows one large78.508deg torch/near-arm change; no added hold/interpolation or old table edits.','source063_sha256':sha(P/'candidate/F063_zero_call_semantic_RECONNECTED.png'),'source058_sha256':sha(B/'F058_reuse_locked044_gate/candidate/F058_exact_LOCKED044_REUSE_PENDING_ASTRA.png'),'proposal':'One intermediate actual whole grip+rigid torch angle at half39.254deg. Complete near sleeve/elbow/forearm/wrist must be redrawn as one connected chain; blue corridor is NOT_ART, old vacancies gray. Far arm currently remains063source in this diagnostic and still needs an explicit inbetween action choice.','one_group_scale':1,'R_from063_degrees':-39.254,'M':m.tolist(),'t':tm.tolist(),'T_mid':Tm.tolist(),'L_mid':(Tm+u).tolist(),'G_mid_reference_only':Gm.tolist(),'technical_near_wrist':W.tolist(),'technical_near_root':N.tolist(),'technical_near_elbow':E.tolist(),'grip_station_not_claimed_measured':True,'time_assignment':None,'original058x5_063x6_exposure_changed':False,'imagegen_calls':0,'complete_inbetween_character_created':False,'A_B_inputs_frozen':False}
(R/'geometry/turn_mid_reference.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec,indent=2))
