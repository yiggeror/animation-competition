from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes,binary_dilation,distance_transform_edt
import numpy as np,math,json,hashlib,shutil,argparse
R=Path(__file__).resolve().parent;B=R.parent;ap=argparse.ArgumentParser();ap.add_argument('--out');q=ap.parse_args();O=Path(q.out)if q.out else R
for d in['sources','geometry','qa','requests']:(O/d).mkdir(parents=True,exist_ok=True)
P=B/'F063_zero_call_semantic_reintegration_20261019';F=B/'F069_FINAL_reference_GATE_0abc3fd9_20261019';files={'F063_LOCKED0abc.png':P/'candidate/F063_zero_call_semantic_RECONNECTED.png','F058_LOCKED044.png':B/'F058_reuse_locked044_gate/candidate/F058_exact_LOCKED044_REUSE_PENDING_ASTRA.png','near_actual_mask.png':P/'masks/NEW_complete_near_skin_chain_FRONT_of_prop.png','prop_actual_visible_mask.png':P/'masks/KEEP_known_true_prop_AFTER_new_hand_occlusion.png','prop_unknown_visible_mask.png':P/'masks/KEEP_actual_returned_unknown_cylinder_material_only.png','head_guard.png':P/'masks/KEEP_actual044_head_neck_complete_collar.png','skirt_guard.png':P/'masks/KEEP_actual044_skirt_material.png','D_identity_cloth_1280x1536.png':F/'inputs_1280x1536/D_F069_PREPARED_NOT_FROZEN_1280x1536.png','unit_geometry.json':B/'F063_full_grip_shape_repair_gate_20261019/sources/F063_frozen_target_geometry_REFERENCE.json'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,p in files.items():
 sp=R/'sources'/n
 if not sp.exists():sp.parent.mkdir(exist_ok=True);shutil.copyfile(p,sp)
 if O!=R:shutil.copyfile(sp,O/'sources'/n)
load=lambda n:Image.open(R/'sources'/n).convert('RGBA');mask=lambda n:np.array(Image.open(R/'sources'/n).convert('L'))>0
src=load('F063_LOCKED0abc.png');a=np.array(src);sz=src.size;yy,xx=np.indices(a.shape[:2]);assert sha(R/'sources/F063_LOCKED0abc.png')=='0abc3fd9cfcf7964f825ac7be0227fb9f588da709809f6d15362063741e545ef'
near=mask('near_actual_mask.png');prop=mask('prop_actual_visible_mask.png')|mask('prop_unknown_visible_mask.png');head=mask('head_guard.png');skirt=mask('skirt_guard.png');grip=near&(xx>=965);groupmask=grip|prop;group=Image.fromarray(np.where(groupmask[:,:,None],a,0).astype('uint8'));propim=Image.fromarray(np.where(prop[:,:,None],a,0).astype('uint8'))
warm=(a[:,:,0]>160)&(a[:,:,0]>a[:,:,1]+16)&(a[:,:,1]>a[:,:,2]+8)&(a[:,:,2]>75)&(a[:,:,3]>=16);la,_=label(warm);far=binary_dilation(binary_fill_holes(la==la[765,1000]),iterations=2)&(a[:,:,3]>0);w0=np.array([1092.,694.]);palm=far&((xx-w0[0])*.84-(yy-w0[1])*.54>=0);palmim=Image.fromarray(np.where(palm[:,:,None],a,0).astype('uint8'))
def poly(pts):
 z=Image.new('L',sz);ImageDraw.Draw(z).polygon([tuple(x)for x in pts],fill=255);return np.array(z)>0
oldfar=poly([(910,650),(1040,610),(1260,610),(1260,740),(1135,780),(1020,825),(950,825),(910,760)])|far
vacant=(near|prop|oldfar)&~(head|skirt);base=a.copy();base[vacant]=0
geo=json.loads((R/'sources/unit_geometry.json').read_text());T=np.array(geo['T_target']);L=np.array(geo['L_target']);G=np.array(geo['G_target']);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',15);sm=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',12);crop=(550,0,1320,924);records={};states=[]
def transform(im,m,t):
 iv=m.T;it=-iv@t;return im.transform(sz,Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),Image.Resampling.BICUBIC,fillcolor=0)
for frame,angle,newG,E in[(60,26,np.array([1090.,560.]),np.array([850.,710.])),(62,52,np.array([1060.,600.]),np.array([820.,725.]))]:
 sr=O/f'F{frame:03d}'
 for d in['reference_native','inputs_1280x1536','layers','masks','requests']:(sr/d).mkdir(parents=True,exist_ok=True)
 theta=math.radians(angle-78.508);M=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]]);t=newG-M@G;newgroup=transform(group,M,t);newprop=transform(propim,M,t);W=M@np.array([980.,651.])+t
 f=angle/78.508;pt=(1-f)*np.array([-18.,74.]);fp=palmim.transform(sz,Image.Transform.AFFINE,(1,0,-pt[0],0,1,-pt[1]),Image.Resampling.BICUBIC,fillcolor=0);FW=w0+pt;FE=np.array([995.,810.-30*f]);FR=np.array([945.,695.]);N=np.array([705.,666.])
 vol=Image.new('RGBA',sz);d=ImageDraw.Draw(vol)
 def cap(p,q,r1,r2,col):
  v=q-p;n=np.array([-v[1],v[0]])/np.linalg.norm(v);d.polygon([tuple(p+n*r1),tuple(q+n*r2),tuple(q-n*r2),tuple(p-n*r1)],fill=col,outline='#315b75',width=2)
  for z,r in[(p,r1),(q,r2)]:d.ellipse((z[0]-r,z[1]-r,z[0]+r,z[1]+r),fill=col,outline='#315b75',width=2)
 cap(FR,FE,32,34,(100,160,198,255));cap(FE,FW,34,25,(116,179,216,255));A=Image.fromarray(base.copy());A.alpha_composite(vol);A.alpha_composite(fp)
 nearvol=Image.new('RGBA',sz);volfar=vol;vol=nearvol;d=ImageDraw.Draw(vol);cap(N,E,31,36,(135,192,222,255));cap(E,W,36,25,(135,192,222,255));A.alpha_composite(nearvol);A.alpha_composite(newgroup)
 # Stable source head/collar/skirt stays fixed where naturally in front.
 az=np.array(A);az[head|skirt]=a[head|skirt];A=Image.fromarray(az)
 av=(np.array(volfar)[:,:,3]>0)|(np.array(nearvol)[:,:,3]>0)|(np.array(fp)[:,:,3]>0)|(np.array(newgroup)[:,:,3]>0)
 front=poly([(663,530),(1020,495),(1280,560),(1280,790),(1040,840),(943,800),(820,777),(674,751)])
 white=binary_dilation(vacant|av|front,iterations=8)&~(head|skirt);Bm=Image.fromarray(white.astype('uint8')*255).convert('RGBA');dr=ImageDraw.Draw(A);dr.text((562,12),f'F{frame:03d} / +{angle}deg FROM058 / WHOLE RIGID GROUP / NOT ART',font=font,fill='#306a91');dr.text((930,850),'Blue arms and source cut joins need full redraw.',font=sm,fill='#4d8aaa')
 C=A.copy();dc=ImageDraw.Draw(C)
 for line,col in[([FR,FE,FW],'#ce3b8c'),([N,E,W],'#8750aa')]:
  dc.line([tuple(p)for p in line],fill=col,width=3)
  for p in line:dc.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill=col)
 dc.line([tuple(M@T+t),tuple(M@L+t)],fill='#359296',width=2);D=load('D_identity_cloth_1280x1536.png')
 for letter,img in[('A',A),('B',Bm),('C',C)]:
  img.crop(crop).save(sr/f'reference_native/{letter}_F{frame:03d}_770x924_NOT_ART.png');img.crop(crop).resize((1280,1536),Image.Resampling.NEAREST if letter=='B'else Image.Resampling.LANCZOS).save(sr/f'inputs_1280x1536/{letter}_F{frame:03d}_PREPARED_NOT_CALLED.png')
 D.save(sr/f'inputs_1280x1536/D_F{frame:03d}_IDENTITY_CLOTH_ONLY.png');newgroup.save(sr/'layers/ONE_actual_full_grip_torch_scale1_SOFT.png');fp.save(sr/'layers/ONE_whole_far_palm_SOFT.png');Image.fromarray(white.astype('uint8')*255).save(sr/'masks/COMPLETE_old_new_action_band_WHITE.png')
 hp=np.array(fp)[:,:,3]>=128;pp=np.array(newprop)[:,:,3]>=128;dt=distance_transform_edt(~pp);gap=float(dt[hp].min());ov=int((hp&pp).sum())
 prompt=f'''Draw only F{frame:03d}, the dark, non-contact turning bridge from F058 toward locked F063. Keep image A's1280x1536 transparent canvas and common composition. A has ONE complete real rigid torch and full near wrist/palm/gripping-hand source group rotated approximately{angle}degrees from F058 at scale1. Keep that whole lamp/grip geometry and proportions together; do not stretch the torch or separate a finger/wrist from the group. Its complete near sleeve, upperarm, elbow and forearm must be newly drawn into a natural continuous connection, not attached with a cut wrist or narrow bridge. Blue volumes and soft joints are NOT_ART guides, not measured bones or a finished person.

Draw the complete far sleeve-root, upperarm, elbow, forearm, natural wrist and full receiving palm from its own sleeve behind the near arm. It is still approaching in air: NO palm or fingertip touches the lamp or the near grip. Keep the two forearms separate with clear depth ownership. The placed whole actual far palm is source material and soft orientation only, with no individual finger transforms.

B covers the full old/new arm, hand, moving-lamp and vacated-clothing action band. Redraw continuous blouse/sleeve material and all necessary natural joins throughout it. C is exactly the same pose with complete soft chains; D is identity and internal clothing only, with no competing hand gesture. Visible source grip/prop pixels were moved as one rigid group. Any source extraction cut or newly exposed hidden surface is UNKNOWN, not a physical cylinder neck or recovered RGB; reconstruct it coherently while preserving actual scale and axis. Keep the source head/face/neck/collar, stable skirt and composition. Lamp stays OFF and entirely dark; white lens reflections are notON. No support, switch push, light, guide colors/text, added hands or later state. Return one transparent drawing only. This package prepares reference inputs and performs no image call.\n'''
 (sr/'requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').write_text(prompt);(sr/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps({'prompt':prompt,'referenced_image_paths':[str((R/(f'F{frame:03d}/inputs_1280x1536/{letter}_F{frame:03d}_'+('IDENTITY_CLOTH_ONLY.png'if letter=='D'else 'PREPARED_NOT_CALLED.png'))).resolve())for letter in 'ABCD'],'transparent_background':True,'requested_outputs':1,'status':'INPUT_PREPARATION_ONLY_NOT_CALLED'},indent=2)+'\n')
 records[str(frame)]={'hold':2 if frame==60 else 1,'angle_from058_deg':angle,'angle_from063_deg':angle-78.508,'rigid_group_scale':1,'M':M.tolist(),'t':t.tolist(),'G_soft':newG.tolist(),'T_soft':(M@T+t).tolist(),'L_soft':(M@L+t).tolist(),'near_chain_soft':[N.tolist(),E.tolist(),W.tolist()],'far_chain_soft':[FR.tolist(),FE.tolist(),FW.tolist()],'whole_far_hand_translation_soft':pt.tolist(),'actual_far_palm_to_visible_torch_alpha128':{'min_pixel_center_distance_native':gap,'overlap_pixels':ov},'head_skirt_white_overlap':int((white&(head|skirt)).sum()),'note':'Translation/G and whole chains are explicit soft timing/pose proposals, not frozen measured bone points; actual connected arms and genuine air require drawing review.'};states.append((frame,A))
 for tone,col in[('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
  sheet=Image.new('RGB',(1280,800),(233,239,244));sd=ImageDraw.Draw(sheet)
  for j,letter in enumerate('ABCD'):
   p=next((sr/'inputs_1280x1536').glob(letter+'_*.png'));z=Image.open(p).convert('RGBA');bg=Image.new('RGBA',z.size,col);bg.alpha_composite(z);sheet.paste(bg.resize((320,384)).convert('RGB'),(j*320,20))
  c=A.crop((940,390,1290,825));bg=Image.new('RGBA',c.size,col);bg.alpha_composite(c);sheet.paste(bg.resize((560,350)).convert('RGB'),(650,440));sd.text((15,425),f'F{frame:03d}: full group R={angle}deg from058, s1. Far palm stays in air.',font=font,fill='#36536b');sd.text((15,465),'Blue arms = complete NOT_ART redraw corridors.',font=font,fill='#36536b');sd.text((15,495),'Old single39deg reference is WITHDRAWN.',font=font,fill='#36536b');sheet.save(O/f'qa/F{frame:03d}_four_inputs_{tone}.png')
records['exposure']={'058':2,'060':2,'062':1,'063':6,'total':11};records['sources']={n:sha(R/'sources'/n)for n in files};records['common_crop']={'native':[550,0,1320,924],'tool':[1280,1536],'uniform_scale':128/77,'inverse':'77/128+[550,0]'};records['old39_degree_scheme']='WITHDRAWN_NOT_USED';records['calls']=0;records['unknown']='No hidden prop pixels invented. Source-extraction cuts and revealed source vacancies remain full WHITE for actual coherent drawing.'
(O/'geometry/two_turn_bridge_soft_targets.json').write_text(json.dumps(records,indent=2)+'\n');(O/'README.md').write_text('Two turn-bridge input references ONLY, zero generation/git. Latest exposure058x2→060x2→062x1→063x6 =11frames. The old39degree single-mid scheme is withdrawn.060/062 are whole real063grip+torch rigid rotations corresponding to26/52degrees from058, scale1; all wrist/palm/fingers travel together. Translation/G and full arm chains are explicitly SOFT proposals; source identity/collar/skirt stay fixed. Full actual drawing must reconnect both whole sleeves/arms and verify air. Far full real palm is one whole translated source layer and remains non-contact. D identity/cloth only. Unknown source cuts/revealed material are not recovered RGB or physical cylinder necks. No077/085 prepared. See each state four inputs, short draft/request, common matrices and actual gray/dark sheets.\n')
manifest={str(p.relative_to(O)):sha(p)for p in sorted(O.rglob('*'))if p.is_file()and p.name!='manifest.json'};(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(records,indent=2))
