from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,subprocess,shutil
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;src=R/'F009_result_nominal/candidates/S08_F009_eyes_only_candidate_RGBA.png';original=R/'F005_FINAL_LOCKED/S08_F005_grandma_match_box_RGBA.png';a=np.array(Image.open(src));b=np.array(Image.open(original));m=np.array(Image.open(R/'F006_F009_F012_reference_gate/masks/eyes_scene_white_permission.png'))>0;out=a.copy();out[m]=b[m];dest=O/'candidates/S08_F012_original_eye_reopen_RGBA.png';Image.fromarray(out,'RGBA').save(dest);shutil.copy2(R/'F006_F009_F012_reference_gate/masks/eyes_scene_white_permission.png',O/'masks/exact_reopen_eye_permission.png');change=np.any(out!=a,2)
paths={'F000':R/'F000_FINAL_LOCKED/S08_F000_grandma_match_box_RGBA.png','F003':R/'F003_FINAL_LOCKED/S08_F003_grandma_match_box_RGBA.png','F005':original,'F006':R/'F006_FINAL_LOCKED/S08_F006_grandma_match_box_RGBA.png','F009':src,'F012':dest};dur={'F000':3,'F003':2,'F005':1,'F006':3,'F009':3,'F012':2};font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
for label,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 comps={}
 for n,p in paths.items():
  im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,col);bg.alpha_composite(im);comps[n]=bg.convert('RGB')
 comps['F012'].save(O/'qa'/f'F012_{label}.png');comps['F012'].crop((625,310,1215,910)).resize((1180,1200)).save(O/'qa'/f'F012_head_to_match_{label}.png');comps['F012'].crop((806,488,970,571)).resize((984,498)).save(O/'qa'/f'F012_eyes_{label}.png')
 board=Image.new('RGB',(3*700,2*850),col[:3]);d=ImageDraw.Draw(board)
 for i,(n,c) in enumerate(comps.items()):
  x=(i%3)*700;y=(i//3)*850;d.text((x+16,y+12),f'{n}: hold {dur[n]} frames at24fps',fill='black' if label=='light' else 'white',font=font);board.paste(c.crop((550,300,1240,1080)),(x+5,y+60))
 board.save(O/'qa'/f'F000_to_F012_actual_exposure_board_{label}.png')
 eyes=Image.new('RGB',(3*984,550),col[:3]);d=ImageDraw.Draw(eyes)
 for i,n in enumerate(['F006','F009','F012']):
  d.text((i*984+16,10),n+(' - exact005 original-eye reuse' if n=='F012' else ''),fill='black' if label=='light' else 'white',font=font);eyes.paste(comps[n].crop((806,488,970,571)).resize((984,498)),(i*984,52))
 eyes.save(O/'qa'/f'F006_F009_F012_eyes_comparison_{label}.png')
 target=O/'qa'/f'S08_F000_F013_24fps_{label}_NO_FIRE_REFERENCE.mp4';cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(target)];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for n,c in comps.items():
  for _ in range(dur[n]):proc.stdin.write(c.tobytes())
 proc.stdin.close();rc=proc.wait();assert rc==0
j={'status':'F012_ZERO_CALL_REOPEN_CANDIDATE_SEQUENCE_GATE_PENDING','native_calls_total':7,'new_calls':0,'actual_source_F009':str(src),'eye_donor':str(original),'method':'Exact original approved005 eye RGBA copied only through approved eye semantic mask; no painting, deformation, recolor or new image generation. Original005 eye equals000 mother eye, at current005 hand/match position.','sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'changed_vs009':int(change.sum()),'outside_eye_white_changed':int((change&~m).sum()),'RGBA_difference_vs_original005_entire_scene':int(np.any(out!=b,2).sum()),'fps':24,'exposure_frames':dur,'total_frames':sum(dur.values()),'actual_duration_seconds':sum(dur.values())/24,'source_timing':'Current opening_plan text says24fps, per-shot zero start.','fire_note':'These are character-only reference clips; no flame/light code overlay included or approved.'};(O/'geometry/checks.json').write_text(json.dumps(j,indent=2));print(json.dumps(j,indent=2))
