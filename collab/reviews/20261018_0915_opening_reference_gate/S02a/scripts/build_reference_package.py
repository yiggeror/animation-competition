"""Analytical contact sheets and line guides only. Never modifies source PNGs, generates art, or writes repository files."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,math
ROOT=Path(__file__).resolve().parents[1]
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def font(n): return ImageFont.truetype(FONT,n,index=2)
FG='#d8e4ee';BLUE='#64d2ff';GOLD='#f2c66b';RED='#ff807c';GREEN='#88dbaf'
measure=json.loads((ROOT/'qa/measurements.json').read_text())
assets=measure['assets']
manual={
 'focus':{'eye_L':[736,558],'eye_R':[940,558],'chin':[838,730],'nose':[836,620],'mouth_L':[813,664],'mouth_R':[864,664],'collar_junction':[842,810],'shoulder_L':[583,780],'shoulder_R':[1070,780],'head_top':[839,148],'cowlick_top':[884,77]},
 'tense':{'eye_L':[734,617],'eye_R':[936,617],'chin':[835,776],'nose':[835,677],'mouth_L':[811,719],'mouth_R':[861,718],'collar_junction':[838,829],'shoulder_L':[592,778],'shoulder_R':[1058,778],'head_top':[838,217],'cowlick_top':[883,137]},
 'relief':{'eye_L':[734,598],'eye_R':[934,598],'chin':[835,756],'nose':[834,658],'mouth_L':[826,693],'mouth_R':[880,681],'collar_junction':[838,823],'shoulder_L':[586,786],'shoulder_R':[1068,786],'head_top':[838,199],'cowlick_top':[882,115]}
}
# Landmarks below are visually inspected tracking estimates. They are not anatomical bone lengths.
starts=[0,13,14,15,16,23,25,41,44,46];ends=starts[1:]+[60]
names=['专注','半闭·合','全闭','半闭·开','专注复用','一惊中间','紧张','紧张稍松','松开中间','松口气']
statuses=['have','new','new','new','reuse','new','have','new','new','have']
new_prompts=[None,'头/眉/嘴/肩及衣纹均锁 focus，只落上睑至约半闭。','双眼全闭，瞳孔与眼白完全遮住；保留睫毛与眼裂弧。','重新张眼至半闭，上睑回升；与 d02 分列，不擅自合并状态。',None,'focus 到 tense 的收颏缩颈中间；眉开始抬、瞳孔仍朝画外下方，嘴刚抿。',None,'tense 到 relief 的早期松动，眉与肩略松；闭嘴口角极轻变化。','继续松开，头颈回升但不越过 relief；单侧口角刚开始轻撇。',None]
rows=[]
for i,(s,e,n,status) in enumerate(zip(starts,ends,names,statuses)):
 if i<=4:lo=hi='focus';a=0
 elif i==5:lo,hi,a='focus','tense',.55
 elif i==6:lo=hi='tense';a=0
 elif i==7:lo,hi,a='tense','relief',.25
 elif i==8:lo,hi,a='tense','relief',.70
 else:lo=hi='relief';a=0
 pts={k:[round(manual[lo][k][j]*(1-a)+manual[hi][k][j]*a,2) for j in (0,1)] for k in manual[lo]}
 source={'focus':'S02a_k01_focus.png','tense':'S02a_k02_tense.png','relief':'S02a_k03_relief.png'}[lo]
 row={'drawing':f'S02a_d{i+1:02}','start_frame':s,'end_frame_exclusive':e,'hold_frames':e-s,'state':n,'status':status,'source_reference':source,'planned_line_guide_points':pts,'new_art_instruction':new_prompts[i], 'hand_phone':'out_of_frame; no new visible contact','gaze':'down toward phone, except closed-lid d03'}
 if i==4:row['reuse_exact']='S02a_d01 / S02a_k01_focus.png';row['keep_exposure_entry']=True
 if status=='new':row['requires_opus_reference_approval']=True
 if lo!=hi:row['endpoint_interpolation']={'from':lo,'to':hi,'guide_fraction':a,'status':'proposed 2D tracking guide, not generated pixels or a 3D/bone-length claim'}
 rows.append(row)
out={'scope':'REFERENCE PROPOSAL ONLY; zero image-generation calls; no production asset or implementation edits', 'source_commit':'280c1e25533b76cc5e44e954b45cc98297a36b46','fps':24,'duration_frames':60,'source_canvas':[1672,941], 'counts':{'exposure_states':10,'existing_source_images':3,'non_have_plan_entries':7,'exact_reuse_entries':1,'new_independent_art_states':6}, 'coordinate_note':'Native source pixel centers, top-left origin. Manual facial/neck/shoulder tracking points estimated from actual source images, approximate +/-3 to 6 pixels. Lower-chest A/B/H are independently rerun threshold-component measurements in qa/measurements.json. No shoulder point is a fixed registration anchor.', 'fixed_new_art_guidance':'Keep source canvas and lower-chest clothing stable; do not globally resize to force A/B. Existing sources remain byte-identical. Head/neck/shoulders are allowed to act.', 'manual_source_landmarks':manual,'states':rows}
(ROOT/'S02a_reference_proposal.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
# Actual three original frames over neutral grey; native pixel positions, no registration or recolor.
canvas=Image.new('RGB',(1950,950),'#20262d');d=ImageDraw.Draw(canvas)
d.text((25,15),'S02a 三原件实像 / 同画布直接对照 / 未配准、未改色',font=font(28),fill=FG)
for i,(key,meta) in enumerate(zip(manual,assets)):
 im=Image.open(ROOT/'originals'/meta['file']).convert('RGBA');bg=Image.new('RGBA',im.size,(128,128,128,255));bg.alpha_composite(im)
 # Readability crop is explicitly QA only and all panels share same rectangle.
 crop=(450,60,1220,941);panel=bg.crop(crop).convert('RGB');panel.thumbnail((625,720));x=i*650+12;y=62;canvas.paste(panel,(x,y));scale=panel.width/(crop[2]-crop[0])
 for k,v in meta['lower_chest_points'].items():
  xx=x+(v['xy'][0]-crop[0])*scale;yy=y+(v['xy'][1]-crop[1])*scale
  d.ellipse((xx-5,yy-5,xx+5,yy+5),outline=GOLD,width=3);d.text((xx+7,yy-17),k,font=font(20),fill=GOLD)
 for k in ['eye_L','eye_R','chin','collar_junction']:
  p=manual[key][k];xx=x+(p[0]-crop[0])*scale;yy=y+(p[1]-crop[1])*scale
  d.line((xx-6,yy,xx+6,yy),fill=BLUE,width=2);d.line((xx,yy-6,xx,yy+6),fill=BLUE,width=2)
 d.text((x,795),meta['file'],font=font(21),fill=FG)
 d.text((x,826),f"1672×941 RGBA   alpha 主体顶 y={meta['alpha']['main_component_bbox_alpha_ge_128'][1]}",font=font(19),fill=FG)
 d.text((x,858),f"A/B 拟合 H 残差 {meta['AB_similarity_to_k01']['H_residual_native_pixels']:.2f}px",font=font(19),fill=GOLD)
d.text((20,903),'黄：衣纹 A/B + 独立 H；蓝：人工脸/领跟踪点（约 ±3–6px）。肩可动，不作固定锚。',font=font(23),fill=FG)
canvas.save(ROOT/'qa/S02a_originals_landmark_contact.jpg',quality=94)
# Ten-state line guides from measured original face/neck structure. These are analytical diagrams, not animation cels.
W,H=2300,1230;im=Image.new('RGB',(W,H),'#172029');d=ImageDraw.Draw(im)
d.text((22,15),'S02a 60 帧 / 10 态参考门：3 have + 6 新独立态 + f16 精确复用',font=font(30),fill=FG)
d.text((22,58),'线图仅拟定头眼眉嘴/颈肩路径；造型看三原件。13 半闭 → 14 全闭 → 15 半闭 → 16 原 focus。',font=font(23),fill=GOLD)
for idx,row in enumerate(rows):
 x=(idx%5)*460;y=110+(idx//5)*540;d.rounded_rectangle((x+8,y,x+451,y+525),10,fill='#25313c',outline='#45515d')
 p=row['planned_line_guide_points'];sx=.50;cx=x+230;cy=y+30
 def P(pt):return(cx+(pt[0]-836)*sx,cy+(pt[1]-200)*sx)
 chin=P(p['chin']);left=P([648,p['eye_L'][1]-50]);right=P([1028,p['eye_R'][1]-50]);top=P(p['head_top'])
 # Hair/skull plus lower-face contour, fixed face transverse width. No whole-image scale change between panels.
 d.ellipse((cx-145,top[1],cx+145,chin[1]-25),outline=FG,width=3)
 d.line([left,P([650,p['chin'][1]-90]),P([705,p['chin'][1]-35]),chin,P([965,p['chin'][1]-35]),P([1025,p['chin'][1]-90]),right],fill=FG,width=3)
 d.line((cx,top[1]+5,cx,chin[1]),fill='#576878',width=1)
 closed=idx==2;half=idx in [1,3]
 for side in ['L','R']:
  ex,ey=P(p['eye_'+side]);brow=-13 if idx<=4 else -16 if idx in [5,6] else -13
  if closed:d.arc((ex-22,ey-9,ex+22,ey+8),0,180,fill=BLUE,width=4)
  elif half:
   d.arc((ex-22,ey-6,ex+22,ey+14),0,180,fill=BLUE,width=3);d.line((ex-22,ey+2,ex+22,ey+2),fill=BLUE,width=4);d.ellipse((ex-7,ey+2,ex+7,ey+13),fill=BLUE)
  else:
   d.ellipse((ex-22,ey-16,ex+22,ey+20),outline=BLUE,width=3);d.ellipse((ex-8,ey+1,ex+8,ey+17),fill=BLUE)
  d.arc((ex-25,ey+brow-17,ex+25,ey+brow),185,350,fill=GOLD,width=3)
 d.ellipse((P(p['nose'])[0]-2,P(p['nose'])[1]-1,P(p['nose'])[0]+2,P(p['nose'])[1]+1),fill=FG)
 d.line([P(p['mouth_L']),P(p['mouth_R'])],fill=RED,width=4)
 collar=P(p['collar_junction']);d.line((chin[0]-27,chin[1]-4,collar[0]-30,collar[1]-15),fill=FG,width=3);d.line((chin[0]+27,chin[1]-4,collar[0]+30,collar[1]-15),fill=FG,width=3)
 d.line([P(p['shoulder_L']),collar,P(p['shoulder_R'])],fill=GREEN,width=3)
 for k,v in assets[0]['lower_chest_points'].items():
  xx,yy=P(v['xy']);d.ellipse((xx-4,yy-4,xx+4,yy+4),outline=GOLD,width=2)
 d.text((x+22,y+405),f"d{idx+1:02}  f{row['start_frame']:02}–{row['end_frame_exclusive']-1:02}  ({row['hold_frames']} 帧)",font=font(23),fill=FG)
 d.text((x+22,y+443),row['state']+'  / '+row['status'],font=font(23),fill=GOLD if row['status']=='new' else GREEN)
 desc=['原 focus 不动','只落睑；头肩不动','眼白/瞳孔全遮','开睑，非额外头跳','状态保留，原件复用','缩颈中点，仍看手机','原 tense，不强配','眉肩略松；闭嘴','不越过 relief 端点','原 relief 单侧轻撇'][idx]
 d.text((x+22,y+485),desc,font=font(20),fill=FG)
d.text((20,1201),'提案待 Opus 审；没有新增人物画。脸/颈点为 2D 跟踪估计，不能当三维骨长；衣纹漂移必须另审。',font=font(20),fill=FG)
im.save(ROOT/'qa/S02a_10state_reference_overview.jpg',quality=94)
# Close-up composition/contact diagram: drawing assets are untouched; no visible hand/chin support invented.
src=Image.open(ROOT/'originals/S02a_k01_focus.png').convert('RGBA');bg=Image.new('RGBA',src.size,(74,79,85,255));bg.alpha_composite(src);diagram=bg.convert('RGB');dd=ImageDraw.Draw(diagram)
for k,v in assets[0]['lower_chest_points'].items():
 xx,yy=v['xy'];dd.ellipse((xx-10,yy-10,xx+10,yy+10),outline=GOLD,width=4);dd.text((xx+14,yy-23),k,font=font(28),fill=GOLD)
dd.text((30,35),'S02a 构图 / 接触边界',font=font(34),fill='white')
dd.text((30,90),'正面低机位，只保留头肩。',font=font(27),fill='white')
dd.text((30,132),'手、手机、肘支点在画外。',font=font(27),fill='white')
dd.text((30,174),'不画托腮，不新增可见手掌。',font=font(27),fill='white')
dd.line((50,929,1620,929),fill=RED,width=4)
dd.text((1120,817),'画外接触',font=font(27),fill=RED)
dd.text((1120,860),'手 ↔ 手机；肘 ↔ 席',font=font(25),fill=RED)
dd.text((30,820),'肩可动：不用于配准',font=font(26),fill=GREEN)
dd.text((30,863),'A/B + H：测衣纹，不强配',font=font(25),fill=GOLD)
diagram.save(ROOT/'qa/S02a_composition_contact_boundary.jpg',quality=94)
# Fresh byte/image verification after producing all QA.
m=json.loads((ROOT/'sources/remote_image_manifest.json').read_text())
for a in m:
 p=ROOT/a['dest'];raw=p.read_bytes();assert len(raw)==a['size'];assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==a['sha']
 with Image.open(p) as im:im.verify()
(ROOT/'qa/verification.json').write_text(json.dumps({'source_images':len(m),'all_png_jpeg_decodes_verified':True,'all_git_blob_hashes_match_frozen_tree':True,'all_file_sizes_match':True,'60_frame_coverage':sum(x['hold_frames'] for x in rows),'exposure_states':len(rows),'new_states':sum(x['status']=='new' for x in rows),'reuse_states':sum(x['status']=='reuse' for x in rows),'image_generation_calls':0,'production_or_remote_writes':False},indent=2))
print('Built line guides, actual-source contact sheets, contact boundary, and manifest. Sources unchanged.')
