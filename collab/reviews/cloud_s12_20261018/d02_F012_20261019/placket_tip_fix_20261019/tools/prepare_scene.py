from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,numpy as np
O=Path(__file__).resolve().parents[1];P=O.parent;S=P.parent;BASE=P/'same_raw_fix_20261019';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert np.array_equal(np.array(Image.open(BASE/'candidate/F012.png'))[:,:,3],np.array(Image.open(O/'candidate/F012.png'))[:,:,3])
# Same-depth sibling: exact same scene JS bytes, same t=.5; only native bytes and SHA data differ.
shutil.copyfile(BASE/'scene/s12_F012_scene.js',O/'scene/s12_F012_scene.js');assert (BASE/'scene/s12_F012_scene.js').read_bytes()==(O/'scene/s12_F012_scene.js').read_bytes()
meta=json.loads((BASE/'qa/native_alpha_contacts_registration.json').read_text());meta['native_candidate_SHA256']=sha(O/'candidate/F012.png')
for c in meta['contacts']:
 c['path']=f"../../same_raw_fix_20261019/contact_masks/{c['name']}.png"
 assert ((O/'scene')/c['path']).resolve().is_file()
meta['alpha_unchanged_contact_masks_reused_exactly']=True
(O/'qa/native_alpha_contacts_registration.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
for rel in ['../../../../../../js/paint/paintshot.js','../../../../../../js/lamp/crane.js','../../../../../../js/puppet.js','../../../geometry/three_key_pose_proposal.json','../qa/native_alpha_contacts_registration.json','../candidate/F012.png']:assert ((O/'scene')/rel).resolve().is_file(),rel
shutil.copyfile(BASE/'tools/network_audit_chromium.cjs',O/'tools/network_audit_chromium.cjs')
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
def flat(path,color):
 im=Image.open(path).convert('RGBA');return Image.alpha_composite(Image.new('RGBA',im.size,(*color,255)),im).convert('RGB')
paths=[S/'first_left_grasp_inputs_20261019/inputs/locked_F000.png',BASE/'candidate/F012.png',O/'candidate/F012.png'];labels=['LOCKED MOTHER F000','PREVIOUS F012103','TIP CORRECTED F012']
board=Image.new('RGB',(1536,1604),'white');d=ImageDraw.Draw(board)
for row,color in enumerate([(205,208,211),(36,38,42)]):
 for col,(path,label) in enumerate(zip(paths,labels)):
  im=flat(path,color).resize((512,768));x=col*512;y=row*802;board.paste(im,(x,y+34));d.text((x+10,y+6),label,font=font(17),fill='black')
board.save(O/'qa/01_native_whole_three_same_scale_gray_dark.jpg',quality=95)
# Same-scale exact crop including neighboring untouched mid-placket, arm and pants.
board=Image.new('RGB',(1800,1100),'white');d=ImageDraw.Draw(board)
for i,(path,label) in enumerate(zip(paths,labels)):
 im=flat(path,(205,208,211)).crop((450,920,550,1085)).resize((600,990),Image.Resampling.NEAREST);board.paste(im,(i*600,45));d.text((i*600+10,10),label,font=font(20),fill='black')
board.save(O/'qa/02_native_complete_tip_context6x.jpg',quality=97)
base=flat(BASE/'candidate/F012.png',(205,208,211)).convert('RGBA');board=Image.new('RGB',(1500,1040),'white');d=ImageDraw.Draw(board)
for i,(name,label) in enumerate([('domain_complete_semantic_tip','Complete semantic cloth tip'),('lit_face','Lit face / shade split'),('RGB_changed','Actual RGB changes')]):
 im=base.copy();mask=np.array(Image.open(O/f'masks/{name}.png'));over=Image.new('RGBA',im.size,(25,210,105,0));over.putalpha(Image.fromarray(np.rint(mask*.48).astype(np.uint8)));im=Image.alpha_composite(im,over).convert('RGB').crop((450,920,550,1085)).resize((500,825),Image.Resampling.NEAREST);board.paste(im,(i*500,50));d.text((i*500+10,12),label,font=font(18),fill='black')
board.save(O/'qa/03_semantic_faces_and_actual_change_masks.jpg',quality=96)
(O/'qa/scene_input_preparation.json').write_text(json.dumps({'source_scene_SHA256':sha(BASE/'scene/s12_F012_scene.js'),'new_scene_SHA256':sha(O/'scene/s12_F012_scene.js'),'scene_source_byte_equal_previous_actual_passed_scene':True,'native_candidate_SHA256':sha(O/'candidate/F012.png'),'old_approved_native_SHA256':sha(BASE/'candidate/F012.png'),'old_six_actual_alpha_shadow_masks_reused_byte_exact':True,'scene_time':.5,'registration':{'scale':.7,'x':275,'y':112},'onlyF012':True},indent=2)+'\n')
print('same exact scene source copied; paths preflighted; same alpha contact masks reused; candidate',sha(O/'candidate/F012.png'))
