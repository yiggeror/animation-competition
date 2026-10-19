from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes,binary_dilation
import numpy as np,json,hashlib,shutil,argparse
R=Path(__file__).resolve().parent;BASE=R.parent;OLD=BASE/'F060_F062_TWO_turn_bridge_INPUTS_20261019';OV=BASE/'F069_SHORT_PUFF_BARE_ARMS_REPAIR_GATE_20261019/bridge_short_sleeve_overrides';ap=argparse.ArgumentParser();ap.add_argument('--out');args=ap.parse_args();O=Path(args.out)if args.out else R
for d in ['sources','geometry','qa','requests']:(O/d).mkdir(parents=True,exist_ok=True)
files={'F069_SHORT_PUFF_LOCKED_bc64924f.png':BASE/'F069_SHORT_PUFF_NATIVE_call01_12e88f6f_20261019/candidate/F069_SHORT_PUFF_BARE_ARMS_semantic_RECONNECTED_SECOND_REVIEW.png','CLEAN_F063_head_context_ONLY.png':OLD/'sources/F063_LOCKED0abc.png','original_bridge_geometry.json':OLD/'geometry/two_turn_bridge_soft_targets.json','head_guard.png':OLD/'sources/head_guard.png','skirt_guard.png':OLD/'sources/skirt_guard.png'}
for f in [60,62]:
 for key,path in [('old_A',OV/f'F{f:03d}/reference_native/A_F{f:03d}_SHORT_PUFF_BARE_ARMS_NOT_ART.png'),('old_B',OLD/f'F{f:03d}/reference_native/B_F{f:03d}_770x924_NOT_ART.png'),('rigid_hand_torch',OLD/f'F{f:03d}/layers/ONE_actual_full_grip_torch_scale1_SOFT.png'),('whole_far_hand',OLD/f'F{f:03d}/layers/ONE_whole_far_palm_SOFT.png')]:files[f'F{f:03d}_{key}.png']=path
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,path in files.items():
 s=R/'sources'/name
 if not s.exists():shutil.copyfile(path,s)
 if O!=R:shutil.copyfile(s,O/'sources'/name)
load=lambda n:Image.open(R/'sources'/n).convert('RGBA');locked=load('F069_SHORT_PUFF_LOCKED_bc64924f.png');a=np.array(locked);sz=locked.size;yy,xx=np.indices(a.shape[:2]);assert sha(R/'sources/F069_SHORT_PUFF_LOCKED_bc64924f.png')=='bc64924feaa5331c26f8c3d0874634ec7b765295ca95ff6f729bbe2755cdf8f5'
g=json.loads((R/'sources/original_bridge_geometry.json').read_text());head=np.array(Image.open(R/'sources/head_guard.png').convert('L'))>0;skirt=np.array(Image.open(R/'sources/skirt_guard.png').convert('L'))>0
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',14);big=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
def poly(pts):
 z=Image.new('L',sz);ImageDraw.Draw(z).polygon(pts,fill=255);return np.array(z)>0
v=a.astype(int);warm=(v[:,:,0]>145)&(v[:,:,0]>v[:,:,1]+15)&(v[:,:,1]>v[:,:,2]+9)&(v[:,:,2]>65)&(v[:,:,3]>=16);lab,_=label(warm);skin=np.zeros(a.shape[:2],bool)
for seed in [(800,730),(1005,750)]:
 k=lab[seed[1],seed[0]];assert k>0;skin|=binary_dilation(binary_fill_holes(lab==k),iterations=2)
near_puff=poly([(579,480),(685,480),(725,535),(770,585),(779,626),(750,658),(714,683),(675,686),(636,664),(602,659),(583,620)])
far_puff=poly([(909,641),(983,637),(1007,661),(1018,709),(973,735),(931,730),(910,701)])
puff=(near_puff|far_puff)&(a[:,:,3]>0)&~skin&~head
pufflayer=Image.fromarray(np.where(puff[:,:,None],a,0).astype('uint8'));pufflayer.save(O/'sources/LOCKED069_actual_short_puffs_cloth_only_no_hands.png');Image.fromarray(puff.astype('uint8')*255).save(O/'geometry/LOCKED069_short_puff_material_mask.png')
# D is only locked costume and tiny adjacent skin/ink samples. It contains no complete hand/gesture.
D=Image.new('RGBA',(1280,1536));dd=ImageDraw.Draw(D);dd.text((35,25),'LOCKED069 SHORT PUFF / BARE SKIN / MATERIAL ONLY',font=big,fill='#315c74')
dcrop=[]
for b,p,s,t in [((583,480,780,690),(40,85),2.5,'NEAR: short puff edge + upperarm skin'),((909,641,1018,737),(650,85),3.6,'FAR: short cuff ends ABOVE elbow'),((792,705,845,730),(65,910),4,'Real bare skin / ink'),((800,588,829,611),(650,910),5,'Internal blouse material')]:
 z=locked.crop(b);z=z.resize((round(z.width*s),round(z.height*s)),Image.Resampling.LANCZOS);D.alpha_composite(z,p);dd.text((p[0],p[1]+z.height+12),t,font=font,fill='#315c74');dcrop.append({'source_crop':b,'paste':p,'scale':s})
dd.text((35,1370),'COSTUME ONLY. NO new069 grip, hand target or pose in D.',font=big,fill='#315c74')
def outline(chain,widths):
 p=np.array(chain,float);t=np.vstack([p[1]-p[0],p[2]-p[0],p[2]-p[1]]);n=np.c_[-t[:,1],t[:,0]]/np.linalg.norm(t,axis=1)[:,None];left=p+n*np.array(widths)[:,None];right=p-n*np.array(widths)[:,None];z=np.vstack([left,right[::-1]]);pts=[]
 for i,b in enumerate(z):
  prev=z[(i-1)%len(z)];nxt=z[(i+1)%len(z)];u=b*.75+prev*.25;v=b*.75+nxt*.25
  for q in np.linspace(0,1,16):pts.append(tuple((1-q)**2*u+2*q*(1-q)*b+q*q*v))
 return pts
# Remove both obsolete material fragments as well as the old synthetic volumes, then place locked short puffs.
clear_puffs=poly([(578,478),(696,478),(744,540),(792,618),(791,679),(753,721),(650,723),(592,687),(578,620)])|poly([(907,635),(1024,632),(1050,710),(1025,790),(923,790),(906,726)])
records={};crop=(550,0,1320,924)
for f in [60,62]:
 S=O/f'F{f:03d}'
 for d in ['reference_native','inputs_1280x1536','masks','layers','requests']:(S/d).mkdir(parents=True,exist_ok=True)
 old=load(f'F{f:03d}_old_A.png');b=Image.new('RGBA',sz);b.alpha_composite(old,(550,0));ar=np.array(b);rgb=ar[:,:,:3];blue=np.zeros(ar.shape[:2],bool)
 for col in [(130,188,216),(151,203,226),(49,92,116)]:blue|=np.all(rgb==col,axis=2)
 clear=(blue|clear_puffs)&~(head|skirt);ar[clear]=0
 # Remove inherited annotation pixels before writing the one current title.
 ar[:80]=np.array(load('CLEAN_F063_head_context_ONLY.png'))[:80]
 cyan=(ar[:,:,2].astype(int)>ar[:,:,0].astype(int)+15)&(ar[:,:,1].astype(int)>ar[:,:,0].astype(int)+15)&(yy>830);ar[cyan]=0
 A=Image.fromarray(ar);rec=g[str(f)];vol=Image.new('RGBA',sz);d=ImageDraw.Draw(vol)
 for name,col,widths in [('far_chain_soft',(130,188,216,255),[25,29,21]),('near_chain_soft',(151,203,226,255),[28,32,22])]:d.polygon(outline(rec[name],widths),fill=col,outline='#315c74',width=2)
 A.alpha_composite(vol);A.alpha_composite(pufflayer)
 for name in ['whole_far_hand','rigid_hand_torch']:A.alpha_composite(load(f'F{f:03d}_{name}.png'))
 d=ImageDraw.Draw(A);d.multiline_text((1030,20),f'F{f:03d} / NOT_ART\n+{rec["angle_from058_deg"]}deg / scale1\nSHORT PUFF / BARE ARMS',font=font,fill='#397694',spacing=4)
 C=A.copy();d=ImageDraw.Draw(C)
 for name,col in [('far_chain_soft','#d24e94'),('near_chain_soft','#925ab3')]:d.line([tuple(p)for p in rec[name]],fill=col,width=3)
 oldwhite=np.array(load(f'F{f:03d}_old_B.png'))[:,:,0]>128;whitefull=np.zeros(a.shape[:2],bool);whitefull[0:924,550:1320]=oldwhite
 white=(whitefull|binary_dilation(clear_puffs|puff|(np.array(vol)[:,:,3]>0),iterations=8))&~(head|skirt);B=Image.fromarray(white.astype('uint8')*255).convert('RGBA')
 for letter,img in [('A',A),('B',B),('C',C)]:
  img.crop(crop).save(S/f'reference_native/{letter}_F{f:03d}_SHORT_PUFF_NOT_ART_770x924.png');img.crop(crop).resize((1280,1536),Image.Resampling.NEAREST if letter=='B'else Image.Resampling.LANCZOS).save(S/f'inputs_1280x1536/{letter}_F{f:03d}_PREPARED_NOT_CALLED.png')
 D.save(S/f'inputs_1280x1536/D_F{f:03d}_LOCKED069_COSTUME_ONLY.png');Image.fromarray(white.astype('uint8')*255).save(S/'masks/COMPLETE_short_puff_bare_arm_action_band_WHITE.png')
 for name in ['whole_far_hand','rigid_hand_torch']:shutil.copyfile(R/'sources'/f'F{f:03d}_{name}.png',S/'layers'/f'UNCHANGED_{name}.png')
 prompt=f'''Draw one F{f:03d} dark turning-bridge drawing on A's exact1280x1536 transparent canvas. It is {rec['angle_from058_deg']}degrees from F058 toward F063. The one complete real torch and near wrist/palm/gripping-hand source group is placed as one rigid scale1 group. Preserve its whole axis, proportions and grip ownership; do not stretch the lamp or transform fingers separately. The complete far hand remains an approaching receiving hand in AIR, without contact or switch action. Do not replace this bridge target with the later F069 pose.

Use locked069 in D for SHORT PUFF costume and skin/material identity ONLY. Draw each short puff sleeve ending on its proximal upperarm well ABOVE the elbow, with a concrete gathered short cuff edge. Then draw a complete natural BARE upperarm, elbow, tapered bare forearm and natural wrist into the shown whole source hand. Absolutely no long sleeve, wrist cuff, elastic band, yellow cloth beyond the short cuff, or fabric wrinkles on the arm. Do not recolor a long-sleeve envelope as skin. Do not copy the blue construction as capsules, round joints, armor or finished skin. It is a fresh NOT_ART redraw direction, not measured bones.

B is one full editing-band reference: short sleeve roots and cuffs, chest-side joins, complete old/new upperarms, elbows, forearms, natural wrist entrances and vacated clothing are all editable. Draw both entire coherent chains, never pasted wrists, narrow flesh bridges, old extraction cuts or doubled outlines. The far arm must emerge from its own far sleeve behind the near arm; do not grow it from the near forearm or cross the forearm bodies. C is the exact same pose with soft chains, not an alternate action. D contains only locked short-puff edges, a little adjacent bare skin and internal materials, no competing later hand gesture.

Keep the existing real rigid hand/torch placement. Any unknown area behind an old source hand or at an extraction edge is UNKNOWN, not a physical cylinder neck or recovered hidden RGB. Reconstruct coherent newly exposed material while retaining real size and axis. Preserve source head, face, neck/collar and stable skirt. The receiving palm and every finger must visibly clear the real torch and near grip. Lamp remains OFF and dark; white reflections are not ON. Return only one transparent bridge drawing, no guide text/color, haze, extra limbs, support, switch push, light or following state.'''
 (S/'requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').write_text(prompt+'\n');paths=sorted((R/f'F{f:03d}/inputs_1280x1536').glob('*.png'));names=[f'{l}_F{f:03d}_PREPARED_NOT_CALLED.png'for l in 'ABC']+[f'D_F{f:03d}_LOCKED069_COSTUME_ONLY.png'];(S/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps({'prompt':prompt,'referenced_image_paths':[str(R/f'F{f:03d}/inputs_1280x1536'/n)for n in names],'transparent_background':True,'requested_outputs':1,'status':'INPUT_GATE_ONLY_NOT_CALLED'},indent=2)+'\n')
 for tone,col in [('gray',(215,224,231,255)),('dark',(35,43,52,255))]:
  board=Image.new('RGB',(1280,760),(231,237,243));dr=ImageDraw.Draw(board)
  for j,name in enumerate(names):
   z=Image.open(S/'inputs_1280x1536'/name).convert('RGBA');bg=Image.new('RGBA',z.size,col);bg.alpha_composite(z);board.paste(bg.resize((320,384)).convert('RGB'),(j*320,0))
  z=A.crop((585,475,1285,825));bg=Image.new('RGBA',z.size,col);bg.alpha_composite(z);board.paste(bg.resize((700,350)).convert('RGB'),(280,400));board.save(O/f'qa/F{f:03d}_four_inputs_and_arms_{tone}_NOT_ART.png')
 records[str(f)]={'original_geometry':rec,'geometry_changed':False,'rigid_group_layer_SHA_unchanged':sha(S/'layers/UNCHANGED_rigid_hand_torch.png')==sha(R/'sources'/f'F{f:03d}_rigid_hand_torch.png'),'far_whole_hand_layer_SHA_unchanged':sha(S/'layers/UNCHANGED_whole_far_hand.png')==sha(R/'sources'/f'F{f:03d}_whole_far_hand.png'),'actual_short_puff_material_source':'locked069 bc64924f, cloth only no hands','old_new_full_barearm_and_short_cuff_roots_WHITE':True,'white_head_skirt_overlap':int((white&(head|skirt)).sum()),'status':'SOFT_NOT_ART_INPUT_ONLY'}
records['source_SHA256']={n:sha(R/'sources'/n)for n in files};records['D_material_crops_and_paste']=dcrop;records['mapping']={'native_crop':crop,'tool':[1280,1536],'uniform':128/77,'inverse':'77/128+[550,0]'};records['exposure']={'058':2,'060':2,'062':1,'063':6,'total':11};records['no_change_to_locked069']=True;records['calls']=0
(O/'geometry/source_geometry_and_checks.json').write_text(json.dumps(records,indent=2)+'\n');(O/'README.md').write_text('F060/F062 short-puff bridge INPUT GATE ONLY. NO GENERATION. Original26/52degree full real hand+torch scale1 placements and complete arm targets are unchanged; do not substitute the later069 pose. Locked069bc64924f supplies only actual short-puff cloth, adjacent bare-skin and material identity. A/C remove previous puff fragments and synthetic arm guides, then show locked short cuffs with fresh tapered NOT_ART bare upperarm/elbow/forearm volumes. Full real source hand/torch and whole far hand layers remain byte-identical to the approved bridge reference. B includes complete short sleeve roots/cuffs, chest sides, full old/new arms and wrist entrances, with actual head/skirt masks subtracted; all coherent joins need actual drawing. D has no complete hand gesture. Unknown source extraction cuts remain UNKNOWN, not invented prop surface. Exposure stays058x2→060x2→062x1→063x6=11f. No073 or other state.\n')
manifest={str(p.relative_to(O)):sha(p)for p in sorted(O.rglob('*'))if p.is_file()and p.name!='manifest.json'};(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'frames':[60,62],'manifest_SHA':sha(O/'manifest.json'),'calls':0}))
