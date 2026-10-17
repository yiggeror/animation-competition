from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,subprocess
p=Path('/tmp/laidian-s01-rigs/audit_motion');root=Path('/workspace/animation-competition')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
# Actual decoded video pixels: wrist/bangle, no optical stabilization or synthetic animation.
fs=[0,7,16,22,66,74]
out=Image.new('RGB',(6*240,346),(245,245,245));d=ImageDraw.Draw(out)
for i,f in enumerate(fs):
 im=Image.open(p/'frames'/f'{f:05d}.png').crop((250,410,370,570)).resize((240,320))
 out.paste(im,(i*240,26));d.text((i*240+5,4),f'F{f} {f/24:.3f}s',font=font,fill='black')
out.save(p/'wrist_bangle_actual_frames.png')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p/'source/rig_test_grandma_beans.mp4')]))
(p/'probe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n')
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
files={str(f.relative_to(p)): {'sha256':sha(f),'bytes':f.stat().st_size} for f in sorted((p/'source').iterdir()) if f.name!='g01_rgba.bin'}
framehash=[{'frame':i,'t':i/24,'path':str(f.relative_to(p)),'sha256':sha(f)} for i,f in enumerate(sorted((p/'frames').glob('*.png')))]
manifest={
 'reviewer':'Astra / audio_audit; read-only independent motion audit',
 'repository':'/workspace/animation-competition','observed_head':'90f8a45ce7b2c098d404d1a2f1c523f4831eb341',
 'scope':'Opus-delivered six-second rig_test_grandma_beans.mp4; no new animation rendering, no repo modifications, no S31 changes',
 'clip_source_commit':'66ea5f7 (git log --follow result; source-production manifest was not supplied)',
 'source_code_scope':'Source files copied from observed HEAD; binds/poses sampled from these exact frozen bytes. This is not a claim that a new current-S01 shot was rendered.',
 'video':{'width':600,'height':1000,'fps':'24/1','frames':144,'duration_seconds':6,'audio_streams':0},
 'original_image':{'size':[779,1355],'mode':'RGBA'},
 'inspection':'Viewed source full image and crops, all 144 hand/pod/bowl crops in six chronological sheets, 12 full-body frames, six enlarged wrist crops. No normal-speed audiovisual playback claimed.',
 'source_files':files,'decoded_frames':framehash,
 'calculation':'inspect_mesh.cjs uses original copied warp.bind/boneMatrices and test_anim.grandmaBeans; an OffscreenCanvas stub supplies actual RGBA for bind only. No GL drawing or scene rendering.'
}
(p/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# Review-only local coordinate deltas. This is deliberately not a replacement production rig.
suggestions={
 'kind':'review-only coordinate suggestions; NOT applied; must rerender and check before adoption',
 'base_rig_sha256':files['source/g01_beans.rig.json']['sha256'],
 'source_image_sha256':files['source/g01_beans.png']['sha256'],
 'coordinate_space':'source image pixel xy, 779x1355',
 'bones_by_name':{
 'upperarm_far':{'tail_candidate':[225,596]},
 'forearm_far':{'head_candidate':[225,596],'tail_candidate':[166,525]},
 'hand_far':{'head_candidate':[166,525],'tail_candidate':[170,483]},
 'forearm_near':{'tail_candidate':[394,616]},
 'hand_near':{'head_candidate':[394,616]}
 },
 'confidence':{
 'elbow_far':'Visible bent-arm contour supports this area; joint center remains an anatomical estimate, allow +/-10 px, do not use sleeve point [300,510].',
 'wrist_far':'Narrow forearm/hand transition near [166,525], +/-8 px; current [190,480] lies inside hand.',
 'wrist_near':'Green-bangle wrist center about [394,616], +/-10 px; current [400,640] is too low on bangle/hand.',
 'shoulders_hips_knees':'Cloth and bowl obscure joints. No new exact coordinates or IK support pins asserted.'
 },
 'region_changes':[
 {'target':'regions[0] bowl','action':'Retrace visible basin only; exclude green bangle lower edge [390,660],[400,650] and near forearm [450,650],[460,660]. Add visible rim-only guard where required; do not use one broad enclosing polygon crossing over an occluder. Review character_audit basin candidate separately.'},
 {'target':'near wrist bangle','action':'Bind visible bangle as one wrist rigid component following near/anatomical-left forearm; do not let bowl or hand/thumb blend bend it.'},
 {'target':'held pod and isolated pea','action':'Keep near-held pod with near hand contact group; isolated round pea follows far pinch. Releasing a pea into bowl needs an explicit prop/occlusion event, not deformation of the existing texture.'}
 ],
 'constraints':'No replacement rig written. No image generation, no hidden finger reconstruction, no edits to implementation.'
}
(p/'g01_coordinate_suggestions.json').write_text(json.dumps(suggestions,ensure_ascii=False,indent=2)+'\n')
print('manifest',sha(p/'manifest.json'))
print('suggestions',sha(p/'g01_coordinate_suggestions.json'))
