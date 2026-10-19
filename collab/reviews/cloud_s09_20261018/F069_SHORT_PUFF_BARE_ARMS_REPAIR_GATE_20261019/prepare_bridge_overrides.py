from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,shutil
R=Path(__file__).resolve().parent;OLD=R.parent/'F060_F062_TWO_turn_bridge_INPUTS_20261019';OUT=R/'bridge_short_sleeve_overrides';OUT.mkdir(exist_ok=True)
g=json.loads((OLD/'geometry/two_turn_bridge_soft_targets.json').read_text());font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',14)
def outline(chain,widths):
 p=np.array(chain,float);t=np.vstack([p[1]-p[0],p[2]-p[0],p[2]-p[1]]);n=np.c_[-t[:,1],t[:,0]]/np.linalg.norm(t,axis=1)[:,None];left=p+n*np.array(widths)[:,None];right=p-n*np.array(widths)[:,None]
 # Smooth the bent contour with quadratic Bezier corner transitions, not joint circles.
 pts=[];z=np.vstack([left,right[::-1]])
 for i,b in enumerate(z):
  prev=z[(i-1)%len(z)];nxt=z[(i+1)%len(z)];u=b*.75+prev*.25;v=b*.75+nxt*.25
  for q in np.linspace(0,1,12):pts.append(tuple((1-q)**2*u+2*q*(1-q)*b+q*q*v))
 return pts
records={}
for f in [60,62]:
 S=OUT/f'F{f:03d}'
 for d in ['inputs_1280x1536','reference_native','requests']:(S/d).mkdir(parents=True,exist_ok=True)
 oldA=Image.open(OLD/f'F{f:03d}/reference_native/A_F{f:03d}_770x924_NOT_ART.png').convert('RGBA');ar=np.array(oldA);sz=oldA.size
 # The old blue construction is synthetic at exact colors; erase it, not source material.
 rgb=ar[:,:,:3];blue=np.zeros(ar.shape[:2],bool)
 for c in [(100,160,198),(116,179,216),(135,192,222),(49,91,117)]:blue|=np.all(rgb==c,axis=2)
 ar[blue]=0;A=Image.fromarray(ar);d=ImageDraw.Draw(A);rec=g[str(f)]
 for name,col,widths in [('far_chain_soft',(130,188,216,255),[25,29,21]),('near_chain_soft',(151,203,226,255),[28,32,22])]:
  chain=np.array(rec[name])-np.array([550,0]);d.polygon(outline(chain,widths),fill=col,outline='#315c74',width=2)
 # Restore the approved rigid source hand+torch and whole far palm, keeping all group matrices unchanged.
 for p in ['ONE_whole_far_palm_SOFT.png','ONE_actual_full_grip_torch_scale1_SOFT.png']:
  z=Image.open(OLD/f'F{f:03d}/layers'/p).convert('RGBA').crop((550,0,1320,924));A.alpha_composite(z)
 d=ImageDraw.Draw(A);d.text((15,36),'SHORT PUFF ENDS ABOVE ELBOW / FULL BARE ARMS / NOT_ART',font=font,fill='#397694')
 C=A.copy();d=ImageDraw.Draw(C)
 for name,col in [('far_chain_soft','#d24e94'),('near_chain_soft','#925ab3')]:d.line([tuple(np.array(p)-[550,0])for p in rec[name]],fill=col,width=2)
 B=Image.open(OLD/f'F{f:03d}/reference_native/B_F{f:03d}_770x924_NOT_ART.png').convert('RGBA')
 for l,z in [('A',A),('B',B),('C',C)]:
  z.save(S/f'reference_native/{l}_F{f:03d}_SHORT_PUFF_BARE_ARMS_NOT_ART.png');z.resize((1280,1536),Image.Resampling.NEAREST if l=='B' else Image.Resampling.LANCZOS).save(S/f'inputs_1280x1536/{l}_F{f:03d}_SHORT_PUFF_BARE_ARMS_PREPARED.png')
 shutil.copyfile(R/'inputs_1280x1536/D_F069_SHORT_PUFF_IDENTITY_NO_HAND_GESTURE.png',S/f'inputs_1280x1536/D_F{f:03d}_SHORT_PUFF_IDENTITY.png')
 oldprompt=(OLD/f'F{f:03d}/requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').read_text();prompt='MANDATORY COSTUME OVERRIDE: Draw the two SHORT puff sleeves ending on the proximal upperarms, clearly above both elbows. From their gathered edges draw natural bare upperarms, elbows and tapered bare forearms into the whole source hands. No yellow cloth past the short cuffs, no wrist cuff, no sleeve folds on skin. Do not dye a long sleeve as skin or copy blue capsules/round joints. Fresh tapered technical contours are NOT_ART; redraw naturally. D shows both real short cuff edges and adjacent skin, no competing hand pose.\n\n'+oldprompt
 (S/'requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').write_text(prompt);args={'prompt':prompt,'referenced_image_paths':[str(p)for p in sorted((S/'inputs_1280x1536').glob('*.png'))],'transparent_background':True,'status':'INPUT_OVERRIDE_ONLY_NOT_CALLED'};(S/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps(args,indent=2)+'\n')
 board=Image.new('RGB',(1280,384),(35,43,52))
 for j,p in enumerate(sorted((S/'inputs_1280x1536').glob('*.png'))):
  z=Image.open(p).convert('RGBA');bg=Image.new('RGBA',z.size,(35,43,52,255));bg.alpha_composite(z);board.paste(bg.resize((320,384)).convert('RGB'),(j*320,0))
 board.save(OUT/f'F{f:03d}_four_inputs_dark_NOT_ART.png');records[str(f)]={'same_rigid_group_source':str(OLD/f'F{f:03d}/layers/ONE_actual_full_grip_torch_scale1_SOFT.png'),'same_M':rec['M'],'same_t':rec['t'],'no_group_scale_or_hand_transform_change':True,'change':'Fresh tapered bare-arm contour replaces synthetic capsule guide, correct short-puff identity D and explicit prompt. Original bridge source files unchanged.','original_B_copied_byte_identically':True}
(OUT/'README.md').write_text('Minimal F060/F062 costume reference overrides only. Old directories untouched. Whole hand/torch group matrices and noncontact action remain the existing two-state proposals. New synthetic bare-arm outlines have no circular joint disks or cloth wrinkles; correct short-puff edges and bare skin are explicit in D and prompts. Full connected natural arms still require authorized drawing and actual review. No generation.\n');(OUT/'checks.json').write_text(json.dumps(records,indent=2)+'\n')
print('two bridge override sets written')
