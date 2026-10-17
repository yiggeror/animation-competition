from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,subprocess,math
root=Path('/workspace/animation-competition'); out=Path('/tmp/laidian-s18-pilot-audit/character')
commit='81b78a53e6e2a72f1649380cdd4d3e7d04dcb99d'
paths=['assets/chars/x18_laugh.png','renders/keyframes/S18/sheet.jpg','renders/keyframes/S18/k01.png','renders/keyframes/S18/k04.png','renders/keyframes/S18/k06.png','renders/keyframes/S18/k07.png','docs/keyframes/S18.json','tools/keyframe_refs.py','collab/claude.md','js/lamp/shots/s18.js']
files=[]
for p in paths:
    b=subprocess.check_output(['git','show',commit+':'+p],cwd=root)
    dest=out/'source'/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
    files.append({'path':p,'sha256':hashlib.sha256(b).hexdigest(),'matches_worktree_read':b==(root/p).read_bytes()})
font=ImageFont.truetype(str(root/'assets/fonts/NotoSansSC-VF.ttf'),20)
small=ImageFont.truetype(str(root/'assets/fonts/NotoSansSC-VF.ttf'),16)
master=Image.open(out/'source/assets/chars/x18_laugh.png').convert('RGB')
manifest={'review_base_commit':commit,'head_at_final_read':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'scope':'Static source/pose-guide review only; no generated keyframe or motion acceptance.','master_size':list(master.size),'files':files}
(out/'source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
# Source-pixel extracts only, no generated/repainted character output.
box=(130,100,550,810)
strip=Image.new('RGB',(420*5,755),'white');d=ImageDraw.Draw(strip)
for i,(label,path) in enumerate([('母版：捂嘴终态','assets/chars/x18_laugh.png'),('k01：未抬手','renders/keyframes/S18/k01.png'),('k04：噗笑','renders/keyframes/S18/k04.png'),('k06：抬手途中','renders/keyframes/S18/k06.png'),('k07：捂嘴','renders/keyframes/S18/k07.png')]):
    im=Image.open(out/'source'/path).convert('RGB');strip.paste(im.crop(box),(420*i,42));d.text((420*i+8,8),label,font=font,fill='black')
strip.save(out/'evidence/master_key_upperbody_strip.png')
# Full uncropped master with three proposed stationary stool landmarks.
anchors={'stool_seat_lower_left':[22,899],'stool_left_foot_outer_bottom':[22,1142],'stool_near_right_foot_outer_bottom':[312,1142]}
overlay=master.copy();d=ImageDraw.Draw(overlay)
for i,(name,p) in enumerate(anchors.items(),1):
    x,y=p;d.ellipse((x-7,y-7,x+7,y+7),outline=(0,180,200),width=3);d.text((x+9,y-28),f'S{i} ({x},{y})',font=small,fill=(0,90,100))
d.text((12,4),'诊断：木凳不动时的候选锚点',font=font,fill=(0,90,100))
overlay.save(out/'evidence/master_registration_candidates.png')
(out/'registration_candidates.json').write_text(json.dumps({'coordinate_space':'source x18_laugh.png, 635x1175; origin top-left; manually estimated, +/- 3px','anchors':anchors,'condition':'Valid only if the stool remains rigid and stationary in this fixed seated shot. Fit a global similarity transform; use an independent third point/edge to reject stool deformation. Do not warp the body to force these matches.','dynamic_nonanchors':['head/hair','collar/shoulder','near wrist/fingers','far hand if shoulders move'],'proposal_only':True},ensure_ascii=False,indent=2))
# Key coordinates computed with exact frozen reference algorithm for diagnosis, not proposed corrected poses.
spec=json.loads((out/'source/docs/keyframes/S18.json').read_text());J=spec['joints'];lens=[math.dist(J[a],J[b]) for a,b in [('sh_n','el_n'),('el_n','wr_n'),('wr_n','hd_n')]]
data=[]
for idx in [1,4,6,7]:
    k=spec['keys'][idx-1];sh=(J['sh_n'][0],J['sh_n'][1]-k['shoulder_lift']);wr=k['wr_n'];l1,l2,l3=lens;dx,dy=wr[0]-sh[0],wr[1]-sh[1];dist=min(math.hypot(dx,dy),l1+l2-1e-3);a=math.atan2(dy,dx);b=math.acos(max(-1,min(1,(l1*l1+dist*dist-l2*l2)/(2*l1*dist))));el=[sh[0]+l1*math.cos(a+b),sh[1]+l1*math.sin(a+b)];ang=math.radians(k['hand_deg_n']);tip=[wr[0]+l3*math.cos(ang),wr[1]+l3*math.sin(ang)]
    data.append({'key':idx,'t':k['t'],'near_shoulder':sh,'near_elbow':[round(v,2) for v in el],'near_wrist':wr,'hand_axis_end':[round(v,2) for v in tip]})
(out/'pose_diagnostics.json').write_text(json.dumps({'projected_near_lengths':lens,'keys':data,'note':'Numerical source diagnostics only. The head is only a circle/orientation guide; hand-axis endpoints are not fingertips/anatomical contact guarantees.'},ensure_ascii=False,indent=2))
print(json.dumps({'source_matches':all(x['matches_worktree_read'] for x in files),'master_sha256':files[0]['sha256'],'pose_diagnostics':data},ensure_ascii=False,indent=2))
