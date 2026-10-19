from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes,binary_dilation
import numpy as np,json,hashlib,shutil
R=Path(__file__).resolve().parent;B=R.parent
NEW=B/'F069_SHORT_PUFF_NATIVE_call01_12e88f6f_20261019'
G=B/'F069_SHORT_PUFF_BARE_ARMS_REPAIR_GATE_20261019'
PAIR=B/'F069_F073_NATIVE_batch_13e696e9_20261019'
HEAD=B/'F077_F085_on_APPROVED073_c8aa20f8_20261019'
for d in ['sources','source_head_pack','candidate','masks','layers','qa']:(R/d).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
copies={
 'F063_LOCKED0abc.png':HEAD/'sources/F063_LOCKED_body.png',
 'F069_LOCKED_bc64924f.png':NEW/'candidate/F069_SHORT_PUFF_BARE_ARMS_semantic_RECONNECTED_SECOND_REVIEW.png',
 'F073_accepted_action_light_costume_revoked.png':PAIR/'candidate/F073_ACTUAL_scene_FIRST_ON.png',
 'F073_native_drawing_before_light.png':PAIR/'layers/F073_ACTUAL_whole_uniform_scene.png',
 'F073_original_lens_emission.png':PAIR/'layers/F073_ON_actual_lens_emission_only.png',
 'F073_original_beam.png':PAIR/'layers/F073_ON_soft_beam_BEHIND_actual_drawing.png',
}
for n,p in copies.items():shutil.copyfile(p,R/'sources'/n)
for p in (HEAD/'source_head_pack').iterdir():
 if p.is_file():shutil.copyfile(p,R/'source_head_pack'/p.name)
assert sha(R/'sources/F069_LOCKED_bc64924f.png')=='bc64924feaa5331c26f8c3d0874634ec7b765295ca95ff6f729bbe2755cdf8f5'
load=lambda p:Image.open(p).convert('RGBA')
im69=load(R/'sources/F069_LOCKED_bc64924f.png');a69=np.array(im69)
native73=load(R/'sources/F073_native_drawing_before_light.png');a73=np.array(native73)
yy,xx=np.indices(a73.shape[:2]);vis=a73[:,:,3]>0
v=a73.astype(int);warm=(v[:,:,0]>145)&(v[:,:,0]>v[:,:,1]+15)&(v[:,:,1]>v[:,:,2]+9)&(v[:,:,2]>65)&(v[:,:,3]>=16)
labs,_=label(warm)
near=binary_dilation(binary_fill_holes(labs==labs[585,1040]),iterations=2)&vis
far=binary_dilation(binary_fill_holes(labs==labs[650,1210]),iterations=2)&vis
near=near&(((xx-982)*.84-(yy-638)*.54)>=0)
mask=lambda p:np.array(Image.open(p).convert('L'))>0
release_wrist=mask(NEW/'masks/RELEASE_old_long_sleeve_far_wrist_cuff_ink_AA.png')
release_cap=mask(NEW/'masks/RELEASE_old_sleeve_occlusion_false_prop.png')
hands=(near|far)&~release_wrist
prop=mask(NEW/'masks/KEEP_actual_prop_slider.png')&~release_cap
head=mask(G/'masks/KEEP_actual069_head_collar.png')
# One locked complete body; only the already accepted native073 action palm/digit
# and real prop materials are restored at their original common registration.
keep=hands|prop|head
a=a69.copy();a[keep]=a73[keep]
base=Image.fromarray(a);base.save(R/'layers/F073_same_LOCKED069_whole_body_own_action_before_light.png')
beam=load(R/'sources/F073_original_beam.png');lens=load(R/'sources/F073_original_lens_emission.png')
f73=beam.copy();f73.alpha_composite(base);f73.alpha_composite(lens)
f73.save(R/'candidate/F073_SHORT_PUFF_BARE_ARMS_own_push_FIRST_ON.png')
for n,m in [('KEEP_073_complete_palms_all_digits',hands),('KEEP_073_true_prop_slider',prop),('KEEP_073_original_head_collar',head),('KEEP_073_all_action_head',keep)]:Image.fromarray((m*255).astype('uint8')).save(R/'masks'/f'{n}.png')
for n in ['077','085']:
 src=load(R/f'source_head_pack/F{n}_registered_source.png')
 m=Image.open(R/f'source_head_pack/F{n}_whole_head_neck_mask.png').convert('L')
 Image.composite(src,f73,m).save(R/f'candidate/F{n}_SHORT_PUFF_073_body_original_head_state.png')
imgs={63:load(R/'sources/F063_LOCKED0abc.png'),69:im69,73:f73,77:load(R/'candidate/F077_SHORT_PUFF_073_body_original_head_state.png'),85:load(R/'candidate/F085_SHORT_PUFF_073_body_original_head_state.png')}
checks={'state':'ZERO_CALL_LOCKED069_BODY_TAIL_PENDING_ACTUAL_REVIEW','locked069_SHA256':sha(R/'sources/F069_LOCKED_bc64924f.png'),'calls':0,'same_whole_body_source':True,'part_translation_rotation_scale_or_new_RGB':False,'light_layers_unchanged':True,'original073_action_guards_before_light_RGBA_changes':{'whole_palms_digits':int(np.any(a[hands]!=a73[hands],axis=1).sum()),'true_torch_slider':int(np.any(a[prop]!=a73[prop],axis=1).sum())},'complete_locked069_body_outside_action_head_changes':int(np.any(a[~keep]!=a69[~keep],axis=1).sum()),'heads':{}}
for n in [77,85]:
 z=np.array(imgs[n]);m=mask(R/f'source_head_pack/F{n:03d}_whole_head_neck_mask.png');diff=np.any(z!=np.array(f73),axis=2)
 checks['heads'][str(n)]={'outside_whole_head_neck_RGBA_changes':int((diff&~m).sum()),'below540_RGBA_changes':int((diff&(yy>=540)).sum())}
for k,q in checks['original073_action_guards_before_light_RGBA_changes'].items():assert q==0
assert checks['complete_locked069_body_outside_action_head_changes']==0
for q in checks['heads'].values():assert not any(q.values())
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16)
for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 full=Image.new('RGB',(2310,954),(231,238,244));dr=ImageDraw.Draw(full)
 close=Image.new('RGB',(2160,1140),(231,238,244));dc=ImageDraw.Draw(close)
 for j,n in enumerate([69,73,77,85]):
  bg=Image.new('RGBA',imgs[n].size,col);bg.alpha_composite(imgs[n]);bg.save(R/f'qa/F{n:03d}_complete_scene_{tone}.png')
  c=bg.crop((550,0,1320,924)).resize((462,554));full.paste(c.convert('RGB'),(j*570,30));dr.text((j*570+10,8),f'F{n:03d} actual locked069 whole short-puff body',font=font,fill='#36536b')
  c=bg.crop((575,475,1295,825)).resize((1080,525));x=j%2*1080;y=j//2*570+30;close.paste(c.convert('RGB'),(x,y));dc.text((x+8,y-25),f'F{n:03d} real complete sleeves/arms/palms/torch',font=font,fill='#36536b')
 full.crop((0,0,2280,600)).save(R/f'qa/F069_F073_F077_F085_full_actual_{tone}.png')
 close.save(R/f'qa/F069_F073_F077_F085_complete_twoarms_grip_light_{tone}.png')
checks['candidate_SHA256']={p.name:sha(p) for p in sorted((R/'candidate').glob('*.png'))}
(R/'qa/static_source_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,ensure_ascii=False,indent=2))
