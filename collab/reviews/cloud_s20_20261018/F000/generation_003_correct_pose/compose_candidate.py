"""Use only frozen binary white mask; no resampling, padding, color or alpha fix."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,struct
import numpy as np

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'generation_001/S20_F000_call001_raw.png'
RAW=ROOT/'S20_F000_call003_correct_pose_raw.png'
GATE=ROOT.parent/'arm_correction_002_no_oldarms'
MASK=GATE/'inputs/04_edit_white.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(RAW)=='6eb8ed6145da4cf9a053993c383ae66f80b474d1a4f8b131a89cfd9e3fd6b204'
assert sha(SOURCE)=='de1aec591119393f7f99a61a166f62e9af456ce24ffd718fec0429b20fe2e330'
assert sha(MASK)=='d6bff7856fedde907529b454f884d84bf2870e7d55fc28c2887d3d9c6c22ee2f'
assert struct.unpack('>II',RAW.read_bytes()[16:24])==(1672,941)
source=Image.open(SOURCE).convert('RGBA');raw=Image.open(RAW).convert('RGBA')
assert source.size==raw.size==(1672,941)
a=np.array(source);b=np.array(raw);mask=np.array(Image.open(MASK))
assert mask.shape==(941,1672) and set(np.unique(mask))=={0,255}
c=a.copy();c[mask==255]=b[mask==255]
candidate=Image.fromarray(c)
out=ROOT/'S20_F000_call003_white_composite_candidate.png'
candidate.save(out)
delta=np.any(c!=a,axis=2)
assert not delta[mask==0].any()
assert np.array_equal(c[mask==255],b[mask==255])

def gray(im):
    bg=Image.new('RGBA',im.size,(140,140,140,255));bg.alpha_composite(im)
    return bg.convert('RGB')

matte=gray(candidate);matte.save(ROOT/'qa/composite_full_gray_QA.png')
regions={
    'composite_shoulders_to_palms':(875,235,1220,485),
    'composite_near_L_wrist_jade':(935,315,1045,405),
    'composite_near_L_sleeve_elbow':(1070,270,1205,460),
    'composite_far_R_wrist_seam':(925,405,1050,480),
    'composite_rod_contacts':(885,275,1005,483),
}
for name,box in regions.items():
    matte.crop(box).resize(((box[2]-box[0])*4,(box[3]-box[1])*4),Image.Resampling.NEAREST).save(ROOT/'qa'/(name+'_4x_QA.png'))

fontpath=ROOT.parents[4]/'assets/fonts/NotoSansSC-VF.ttf'
font=ImageFont.truetype(str(fontpath),26);small=ImageFont.truetype(str(fontpath),22)
board=Image.new('RGB',(2140,700),'#f2f4f5');d=ImageDraw.Draw(board);crop=(875,235,1220,485)
target=Image.open(GATE/'inputs/01_F000_only_correct_pose.png').convert('RGBA')
for i,(title,im) in enumerate([
    ('已审正确target：仅姿态/体量',target),
    ('call003原件：实际肩袖—肘—腕',raw),
    ('冻结白域回贴候选：须再审接缝',candidate),
]):
    x=20+i*705;d.text((x,20),title,font=small,fill='#263743')
    board.paste(gray(im).crop(crop).resize((690,500),Image.Resampling.NEAREST),(x,75))
d.text((20,594),'1672×941，无缩放/补列/裁切；双掌、单镯、四前杆和孩子从call001原像素保留。',font=font,fill='#263743')
d.text((20,644),'保护点零差仅是像素合同；成品须另看完整臂链、布袖、腕掌接回及旧臂残边。',font=small,fill='#263743')
board.save(ROOT/'qa/target_raw_composite_comparison.png')

checks={
    'size':[1672,941],'white_pixels':int((mask==255).sum()),
    'changed_pixels':int(delta.sum()),'outside_white_changed_pixels':int((delta&(mask==0)).sum()),
    'child_changed_pixels':int(delta[:,:835].sum()),
    'head_upper_changed_pixels':int(delta[:247,:].sum()),
    'waist_legs_changed_pixels':int(delta[485:,:].sum()),
    'raw_unmodified':True,'resized':False,'padded':False,'cropped':False,
    'neck_or_alpha_cleanup_applied':False,'composite_candidate_sha256':sha(out),
    'source_sha256':sha(SOURCE),'raw_sha256':sha(RAW),'mask_sha256':sha(MASK),
    'not_visual_acceptance_by_itself':True,
}
for name in ['protect_L_palm_bracelet.png','protect_R_palm.png','protect_four_front_rods.png']:
    p=np.array(Image.open(GATE/'masks_local'/name))>0
    checks['changed_'+name]=int(delta[p].sum());assert not delta[p].any()
assert checks['child_changed_pixels']==checks['head_upper_changed_pixels']==checks['waist_legs_changed_pixels']==0
(ROOT/'composite_pixel_verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,ensure_ascii=False,indent=2))
