from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,json,hashlib,shutil
R=Path('astra_s07_xiaoman_release_20261018_1110'); S=Path('astra_s07_reference_prepare_20261018_1021/sources'); S1=Path('astra_s01_s04_reference_prepare_20261018_1038'); F='/workspace/scratch/f060b5601755/astra_s03b_painted_pilot_20261018/refs/NotoSansSC-VF.ttf'
def font(n):return ImageFont.truetype(F,n)
def t(d,xy,s,n=22,c='#17384a'):d.text(xy,s,font=font(n),fill=c)
for n in ['anim_01_xiaoman_prone_phone.png','anim_07_xiaoman_flop.png','xiaoman_turnaround_v4_draft.png','bg_01_room_wide_base_v2_draft.png','opening_plan.json']:
 shutil.copy2(S/n,R/'sources'/n)
shutil.copy2('astra_s07_first_gate_20261018_1105/sources/S07_d01_f000_code.jpg',R/'sources/S07_d01_f000_code.jpg')
# All originals remain byte exact. These plates are diagnostic pixel registration, not painted frames.
P=Image.open(S/'anim_01_xiaoman_prone_phone.png').convert('RGB'); U=Image.open(S/'anim_07_xiaoman_flop.png').convert('RGB'); B=Image.open(S/'bg_01_room_wide_base_v2_draft.png').convert('RGB')
world_crop=(410,525,730,730); sc=3
board=Image.new('RGB',(1920,850),'white');d=ImageDraw.Draw(board)
t(d,(20,10),'S07 小满：两份已冻母源的实际配准并排；不是生产图',32)
for i,(im,s,tx,ty,label) in enumerate([(P,.16,430,533,'F000 / F008 趴姿母源：沿 S01 0.16 + (430,533)'),(U,.18,430,560,'F039 仰躺母源：沿 S07 0.18 + (430,560)')]):
 w=Image.blend(B,Image.new('RGB',B.size,'white'),.65);r=im.resize((round(im.width*s),round(im.height*s)),Image.Resampling.LANCZOS);w.paste(r,(tx,ty));crop=w.crop(world_crop).resize((960,615),Image.Resampling.LANCZOS);board.paste(crop,(i*960,90));t(d,(i*960+16,60),label,23)
 t(d,(i*960+16,720),'原件仍是3/4；不得称已经严格侧面。' if i==0 else '原件仍是双臂摊开；不得称已经抬手扇风。',24,'#ad3843')
t(d,(20,768),'同一场景裁区 (410,525)–(730,730)，同倍率 ×3；切镜/身体转向不豁免头体连续。',24)
t(d,(20,803),'需先审实际头型与躯干厚度。相机F0/8全景，F39近景，不用近景放大掩盖世界尺度变化。',23)
board.save(R/'reference/01_registered_mothers_same_world_crop.jpg',quality=95)
# Independent actual head evidence. World-space scale is kept, no normalizing to same head size.
heads=Image.new('RGB',(1400,680),'white');d=ImageDraw.Draw(heads);t(d,(20,15),'实际原像素头部：同世界倍率 ×6，非自动量骨',30)
for i,(im,box,s,lab) in enumerate([(P,(920,170,1405,620),.16,'趴姿 .16'),(U,(1120,225,1485,545),.18,'仰躺 .18')]):
 a=im.crop(box);a=a.resize((round(a.width*s*6),round(a.height*s*6)),Image.Resampling.LANCZOS);heads.paste(a,(40+i*700,120));t(d,(40+i*700,75),lab,26)
t(d,(20,590),'趴姿既有头构造68×70场景px；仰躺旧F43构造45×48.6。',24,'#ad3843');t(d,(20,627),'头的方向/透视不同，不能只比y高；但当前图像和构造有缩头风险，须在首态门明确。',23)
heads.save(R/'reference/02_head_scale_actual_pixels.jpg',quality=95)
# Phone original crop and code counterexample; nothing below is production contact proof.
contact=Image.new('RGB',(1600,1040),'white');d=ImageDraw.Draw(contact);t(d,(20,12),'手机接触门：真实原件 / F008旧导图反证 / 拟补动作链',31)
a=P.crop((1200,475,1530,850)).resize((594,675),Image.Resampling.LANCZOS);contact.paste(a,(20,65));t(d,(25,758),'原件看到黑色后壳+摄像头；',23);t(d,(25,790),'后壳上的弯指不是屏幕侧拇指。',23,'#ad3843')
a=Image.open(R/'sources/S07_d02_f008.jpg').crop((330,410,535,520)).resize((820,440),Image.Resampling.NEAREST);contact.paste(a,(710,75));t(d,(710,535),'F008标题说落席，但实际手机仍在手前。',25,'#ad3843');t(d,(710,575),'必须以清单重画接触，不能复制这张代码图。',23)
for i,txt in enumerate(['000：指节松开，仍有最后的手缘承点；头与上身泄气。','003（拟补）：全部离指，机身短距离下落；不穿过掌心。','006（拟补）：机身近席，长边顺席面旋平；两掌已让开。','008：机背/机框贴席，黑屏向上，之后落点不动。']):t(d,(675,650+i*65),txt,24)
t(d,(20,960),'两张000/008直接换图不能证明松指→下落→落稳。003/006为必要补态提案，尚未画、尚未批准。',24,'#ad3843')
contact.save(R/'reference/03_phone_contact_and_timing_gate.jpg',quality=95)
# F39 original and proposed arm path: diagnostic centerlines only.
pose=Image.new('RGB',(1600,1080),'white');d=ImageDraw.Draw(pose);t(d,(20,15),'F039 仰躺基态：原母源及抬手构造门（手臂未成图）',30)
a=U.resize((1280,853),Image.Resampling.LANCZOS);pose.paste(a,(150,70));d=ImageDraw.Draw(pose)
# Source points map. Keep source view intact and mark movable arm separate.
M=lambda p:(150+p[0]*1280/1536,70+p[1]*853/1024)
for name,p in [('后脑',[1411,493]),('肩背',[1187,621]),('近肘原支持候选',[1243,696]),('臀区(隐藏构造)',[824,592]),('近脚跟',[222,780]),('远脚跟',[211,648])]:
 q=M(p);d.ellipse((q[0]-7,q[1]-7,q[0]+7,q[1]+7),fill='#008755',outline='white',width=2);t(d,(min(q[0]+12,1300),q[1]-28),name,20,'#008755')
t(d,(20,949),'F039先把近肘落在席上，再以它为支点抬近右前臂；远左臂保留独立支撑，不能复制近臂。',24)
t(d,(20,986),'旧F043蓝线肘高于原母源席面且掌投影落在脸区，只能当动作意图；新画必须补前后深度/避脸路径。',23,'#ad3843')
t(d,(20,1025),'掌的两次扇风由手腕、前臂和肘连续参与；F049再眼瞟，F053空掌落席，留在原位。',23)
pose.save(R/'reference/04_supine_support_and_arm_gate.jpg',quality=95)
# Baseline camera and support metadata, factual mappings not a new frozen geometry.
data={'status':'reference_gate_pending_no_imagegen_calls','repository':'yiggeror/animation-competition','source_commit':'b568a498bccb367958408f7f47adb95d23a3d789','fps':24,'scene':[1672,941],'approved_cameras':{'F000_F015':[816,482.5,1.04],'F039_F056':[605,637.5,4.18]},'mother_registrations':{'prone_F000_F008':{'scale':.16,'translate':[430,533],'inherits':'S01 S04 frozen reference','source':'anim_01_xiaoman_prone_phone.png'},'supine_F039_onward':{'scale':.18,'translate':[430,560],'inherits':'S07 frozen F043 reference','source':'anim_07_xiaoman_flop.png'}},'base_frames':[0,8,39,43,46,49,53],'proposed_extra_frames':[3,6],'pending_decisions':['Cross-pose projected head/torso continuity: 0.16 prone and 0.18 supine mother crops must not be silently mixed.','Approve two release-to-contact inbetweens F003/F006 if image review confirms required.','F039 near elbow support and F043/F046 near palm depth/clearance must be drawn, old centerline is not contact proof.'],'source_limitations':['Both pose mothers are 3/4; strict side view requires new paint.','Phone source shows rear shell, not visible screen or thumb contact.','Hip/knee points under dress are construction only.','Source F008 still holds phone despite caption; production follows plan instead.'],'generation_calls':0,'failed_generations':0,'generation_tool':'builtin image_gen only; not invoked yet'}
(R/'geometry/reference_gate.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
manifest=[]
for p in (R/'sources').glob('*'):
 if p.suffix=='.base64':continue
 raw=p.read_bytes();manifest.append({'local':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'git_blob':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'bytes':len(raw)})
(R/'sources/source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Four gate boards and metadata written. No imagegen call.')
