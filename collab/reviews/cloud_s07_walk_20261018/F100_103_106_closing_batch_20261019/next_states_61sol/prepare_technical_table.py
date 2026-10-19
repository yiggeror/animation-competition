from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,math,json,hashlib
R=Path(__file__).resolve().parent;S=R/'sources';size=(1960,1080);s=.36410361842105265;off=np.array([627.0254537171638,402.7604324894813]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16);small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',13)
g=json.loads((S/'F095_actual_preparation_metadata.json').read_text());H=np.array(g['softH_near']);NS=np.array(g['target_sleeve_roots095']['near']);FS=np.array(g['target_sleeve_roots095']['far']);G=(np.array([1262.,524.7])-off)/s;W=G+[-48.,8.];U,V=95.,110.;dy=-4.5/s;crop=(1240,0,1960,1080)
load=lambda n:Image.open(S/n).convert('RGBA');body=load('F095_body_head_blouse.png');far=load('F095_far_complete_arm_jade_hand.png');nf=load('F095_near_shoe_ankle_COLLECTED_LANDED.png');ff=load('F095_far_shoe_ankle_SUPPORT_FIXED.png');pants=np.array(load('F095_locked_actual_whole_trousers_ORIGINAL_COLOR.png'));pants[:690]=0;pants=Image.fromarray(pants);lamp=Image.open(R/'reference/existing_lamp_object_same_registration.png').convert('RGBA');shadow=Image.open(R/'reference/existing_lamp_shadow_same_registration.png').convert('RGBA')
def pad(z):
 o=Image.new('RGBA',size);o.alpha_composite(z);return o
def rigid(z,M,t):
 iv=np.linalg.inv(M);it=-iv@t;return z.transform(size,Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),Image.Resampling.BICUBIC,fillcolor=0)
def rot(a):
 r=math.radians(a);return np.array([[math.cos(r),-math.sin(r)],[math.sin(r),math.cos(r)]])
def IK(root,w):
 v=w-root;d=np.linalg.norm(v)
 if not abs(U-V)<=d<=U+V:return None
 e=v/d;q=(U*U-V*V+d*d)/(2*d);return root+e*q+np.array([-e[1],e[0]])*math.sqrt(U*U-q*q)
def volume(ps,rs):
 z=Image.new('RGBA',size);d=ImageDraw.Draw(z)
 for p,q,r1,r2 in zip(ps[:-1],ps[1:],rs[:-1],rs[1:]):
  n=np.array([-(q-p)[1],(q-p)[0]])/np.linalg.norm(q-p);d.polygon([tuple(p+n*r1),tuple(q+n*r2),tuple(q-n*r2),tuple(p-n*r1)],fill='#a6cee0',outline='#3d7695',width=2)
 for p,r in zip(ps[1:-1],rs[1:-1]):x,y=p;d.ellipse((x-r,y-r,x+r,y+r),fill='#a6cee0',outline='#3d7695',width=2)
 return z
# Explicit complete-grip NOT_ART model, no source finger/wrist pose inherited.
hand=Image.new('RGBA',size);d=ImageDraw.Draw(hand);gx,gy=G;wx,wy=W
d.rounded_rectangle((gx-43,gy-17,gx+13,gy+25),radius=15,fill='#c7addc',outline='#765090',width=2)
d.polygon([(wx-13,wy-12),(gx-29,gy-15),(gx-23,gy+23),(wx-13,wy+13)],fill='#c7addc',outline='#765090')
for k in range(4):
 x=gx-9+10*k;d.rounded_rectangle((x-5,gy-21,x+5,gy+19),radius=5,fill='#c7addc',outline='#765090',width=2);d.arc((x-5,gy-4,x+5,gy+13),0,180,fill='#765090',width=2)
# Thumb opposing fingers on the visible front. Wire runs through the closed grip.
d.rounded_rectangle((gx-31,gy+1,gx+10,gy+15),radius=6,fill='#d9bee9',outline='#765090',width=2)
hand.save(R/'reference/F103_complete_closed_hand_VOLUME_NOT_ART.png');lamp_hand=Image.alpha_composite(lamp,hand);lamp_hand.save(R/'reference/F103_same_lamp_and_closed_hand_GROUP_NOT_ART.png');lifted=rigid(lamp_hand,np.eye(2),np.array([0.,dy]));lifted.save(R/'reference/F106_same_group_LIFT_only_NOT_ART.png')
records=[];renders={};waist=Image.new('RGBA',size);d=ImageDraw.Draw(waist);d.polygon([(1404,474),(1580,530),(1555,575),(1525,630),(1509,690),(1407,690),(1399,643),(1389,585),(1380,530)],fill='#bcc8da',outline='#637892',width=2)
for name,deg,lift in [('F103_16deg_PROXY_HOLD',16.,False),('F103_24deg_PROPOSAL',24.,False),('F106_24deg_PROPOSAL',24.,True)]:
 M=rot(deg);t=H-M@H;b=rigid(body,M,t);f=rigid(far,M,t);root=M@NS+t;fr=M@FS+t;w=W+[0.,dy if lift else 0.];E=IK(root,w);z=Image.new('RGBA',size)
 for p in [pad(ff),waist,pad(pants),f,b,pad(nf),shadow]:z.alpha_composite(p)
 if E is not None:z.alpha_composite(volume([root,E,w],[22.,19.,13.]))
 z.alpha_composite(lifted if lift else lamp_hand)
 # Outline link only for unreachable comparison: never draw a stretched arm.
 dz=ImageDraw.Draw(z)
 if E is None:dz.line([tuple(root),tuple(w)],fill='#d37471',width=3)
 else:dz.line([tuple(root),tuple(E),tuple(w)],fill='#386789',width=2)
 for p in [root,w]+([] if E is None else[E]):x,y=p;dz.ellipse((x-4,y-4,x+4,y+4),fill='#386789')
 renders[name]=z
 for tone,bgcol in [('gray',(214,224,232,255)),('dark',(35,43,52,255))]:
  bg=Image.new('RGBA',size,bgcol);bg.alpha_composite(z);bg.crop(crop).save(R/f'qa/{name}_{tone}_NOT_ART.png')
 records.append({'state':name,'lean_DEGREES_PROPOSAL':deg,'source_body_fararm_M':M.tolist(),'source_body_fararm_t':t.tolist(),'shared_hidden_pivot_NOT_ANATOMY':H.tolist(),'scale':1,'near_sleeve_root':root.tolist(),'far_sleeve_root':fr.tolist(),'hand_entry_wrist_DEFINED_BY_COMPLETE_TECH_PALM_NOT_MEASURED':w.tolist(),'bail_top_material_reference':(G+[0,dy if lift else 0]).tolist(),'proxy_projected_lengths':[U,V],'root_to_wrist':float(np.linalg.norm(root-w)),'chosen_2D_proxy_IK_feasible':E is not None,'technical_elbow_NOT_ANATOMY':None if E is None else E.tolist(),'actual_proxy_lengths':None if E is None else[float(np.linalg.norm(root-E)),float(np.linalg.norm(E-w))],'whole_lamp_and_same_whole_hand_translation':[0.,dy if lift else 0.],'source_shadow_translation':[0,0]})
for tone,col in [('gray',(214,224,232,255)),('dark',(35,43,52,255))]:
 sheet=Image.new('RGB',(2160,1160),(235,240,245));d=ImageDraw.Draw(sheet)
 main100=Image.new('RGBA',size);main100.alpha_composite(Image.open(S/'F100_6cb57488_corrected_A_720x1080.png').convert('RGBA'),(1240,0))
 mainrenders={'F100_16deg_CORRECTED_OPEN_APPROACH':main100,'F103_24deg_PROPOSAL':renders['F103_24deg_PROPOSAL'],'F106_24deg_PROPOSAL':renders['F106_24deg_PROPOSAL']}
 for j,(name,z)in enumerate(mainrenders.items()):
  d.text((720*j+12,8),name+' / NOT_ART',font=font,fill='#314c65');d.text((720*j+12,34),'95/110 = projected proxies, NOT measured bones',font=small,fill='#63457c');bg=Image.new('RGBA',size,col);bg.alpha_composite(z);sheet.paste(bg.crop(crop).convert('RGB'),(720*j,62))
 d.text((12,1140),'PRELIMINARY BATCH REVIEW ONLY. Replace real source groups after actual F100. No calls. No final pose acceptance.',font=small,fill='#883e43');sheet.save(R/f'qa/F103_F106_batch_technical_table_{tone}_NOT_ART.png')
 # Contact images show real original wire, tech fingers only; whole grip unchanged.
 panel=Image.new('RGB',(1080,920),(235,240,245));dd=ImageDraw.Draw(panel)
 for j,(name,grp)in enumerate([('103: closed grip; TABLE still supports',lamp_hand),('106: SAME grip + lamp move upward',lifted)]):
  bg=Image.new('RGBA',size,col);bg.alpha_composite(shadow);bg.alpha_composite(grp);panel.paste(bg.crop((1640,280,1850,710)).resize((420,860),Image.Resampling.NEAREST).convert('RGB'),(j*540+50,48));dd.text((j*540+10,10),name,font=small,fill='#40546b')
 dd.text((10,910),'PURPLE HAND IS NOT_ART. New real fingers/ownership/contact must be reviewed after drawing.',font=small,fill='#88465b');panel.save(R/f'qa/F103_F106_whole_grip_and_lift_closeup_{tone}_NOT_ART.png')
# Continuous same-length projected path, not3D/anatomical proof.
reach=[]
root=np.array(records[1]['near_sleeve_root'])
for k in range(7):
 w=W+[0,dy*k/6];e=IK(root,w);reach.append({'fraction':k/6,'wrist':w.tolist(),'elbow':None if e is None else e.tolist(),'projection_proxy_feasible':e is not None})
checks={'status':'PRELIMINARY_TECHNICAL_BATCH_REFERENCE_NOT_NATIVE_INPUT_FROZEN','states':{'100':[100,102,3,'open approach; all fingertips air; table only'],'103':[103,105,3,'whole fingers closed around true cubic bail; table remains support'],'106':[106,107,2,'same whole grip and whole lamp dy=-4.5world; body/shoes fixed; shadow stays']},'records':records,'single_group_lift_native':dy,'single_group_lift_world':-4.5,'body_fararm_between103and106_same_M_t':records[1]['source_body_fararm_M']==records[2]['source_body_fararm_M'] and records[1]['source_body_fararm_t']==records[2]['source_body_fararm_t'],'feet_source_files_unchanged':True,'table_shadow_not_part_of_lifted_object':True,'lamp_only_existing_exact_prop_function_no_object_redesign':True,'whole_grip_rearticulation_proxy_path':reach,'contact_is_technical_not_actual_hands_verified':True,'replace_sources_after_actual100':True,'not_using_legacy100to103_body_translation':True,'limits':['24degree entire head/chest/blouse plus complete fararm is proposed; 16degree comparison does not close chosen95/110 proxies. These proxies are not measured bones.','24degree projected IK feasible does not approve shoulder/forearm naturalness, five fingers, or final waist. All are pending actual100/Astra.','The closed palm is a complete NEW technical volume, not an actual hand image or inherited hanging wrist. No source limb pixels stretched.','106 body/fararm/shoes fixed to proposed103; only whole hand+whole lamp shares exact dy. Near arm must articulate as a complete chain, not float with the lifted hand.','No standalone per-state operation mask or native image request is frozen here. Root must replace actual100 sources and prepare complete white/real guards before any103 call.']}
(R/'geometry/batch_contact_and_proxy_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'states':[{'name':x['state'],'root_to_wrist':x['root_to_wrist'],'feasible':x['chosen_2D_proxy_IK_feasible'],'E':x['technical_elbow_NOT_ANATOMY']}for x in records],'dy':dy},indent=2))
