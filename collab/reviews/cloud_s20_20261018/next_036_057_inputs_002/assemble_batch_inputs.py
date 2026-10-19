from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation
P=Path(__file__).resolve().parent;PACK=P.parent;source=PACK/'handoff_008_020_032_generation_002/F032/S20_F032_accepted.png';A=Image.open(source).convert('RGBA');fontpath=PACK.parents[2]/'assets/fonts/NotoSansSC-VF.ttf';font=ImageFont.truetype(str(fontpath),21);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
card=Image.new('RGB',(900,600),'#e7ebee');d=ImageDraw.Draw(card);d.text((15,12),'已锁032实物：仅头部身份及内部材质，无完整旧身／旧臂',font=font,fill='#263743')
for box,xy,size in [((997,38,1219,224),(18,70),(350,294)),((510,165,690,350),(390,65),(315,324))]:
 im=A.crop(box);bg=Image.new('RGBA',im.size,'#c6ccd0');bg.alpha_composite(im);card.paste(bg.convert('RGB').resize(size),xy)
for k,(name,box) in enumerate([('肤色内部',(1045,390,1070,403)),('蓝布／白花',(1125,468,1157,501)),('黄裙／点纹',(605,570,640,608)),('头发内部',(558,214,588,244))]):
 x=18+k*220;d.text((x,398),name,font=font,fill='#263743');im=A.crop(box);bg=Image.new('RGBA',im.size,'#c6ccd0');bg.alpha_composite(im);card.paste(bg.convert('RGB').resize((190,160)),(x,435))
card.save(P/'shared_identity_internal_materials_only.png')
stages={39:'039转身中间：支撑脚先立稳并短转，骨盆、胸肩和完整头颈转到中间三分之四视角；双手仍握原T_H/T_S不换绑，奶奶R张开靠近C_B、接触数0，L仍并持双鹤签。',45:'045先接后放中间：G.R已牢夹C_B，G.L拇指/食指继续夹C_N，小指仍短时支持C_B，其余指已上收；不得在R未握牢前就让L全离C_B。整条近L前臂和腕同步抬起。',54:'054短稳后起势：双手仍各握一杆，孩子支撑脚固定，骨盆/胸肩/整头颈共同微前沉并看龟，双腕随完整前臂起势；两根杆尚未成X，不能提前到2.4秒前绞签。奶奶R仅C_B、L仅C_N。',36:'036原握：孩子双手持续实握T_H/T_S，完整头颈胸盆随支撑脚开始转幕；奶奶R仍张开靠近，接触数0，L继续闭合并持C_B+C_N。',42:'042接握：孩子已整身转幕。奶奶R从下方由拇指对屈曲食指夹住C_B，另外三指自然闭合；G.R与上方C_N留空气，不得误接C_N。G.L仍支持两鹤签，先共同承重，不先松。',47:'047放握：G.R继续实握C_B；G.L抬整腕/前臂并改成拇指对食指只夹C_N，余三指上收，完全离开C_B；两条杆身份和硬直轴保持，不把手掌在原处揉扁。',58:'058首次绞签：只在原2.4秒cue之后开始。孩子肩—肘—前臂—腕一起内收，前臂不互绕，两杆在手前成首次X；T_S近遮T_H远，R始终T_H、L始终T_S，不因交叉换偶端。奶奶R持C_B、L持C_N。'}
full=Image.new('RGB',(1672,3*505),'#bdc1c4');df=ImageDraw.Draw(full);contacts=[]
for i,f in enumerate([36,39,42,45,47,54]):
 F=P/f'F{f:03}';I=F/'inputs';p=I/'01_unique_opaque_complete_target.png';im=Image.open(p).convert('RGBA');C=np.array(im);assert im.size==(1672,941)
 box=(830,270,1040,500);im.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3),Image.Resampling.NEAREST).save(I/'02_exact_same_view_contacts_3x.png');shutil.copyfile(P/'shared_identity_internal_materials_only.png',I/'03_heads_internal_materials_only.png')
 # Draft single-mask input. Both full new bodies are editable; old full pose is
 # never supplied as an image reference. This mask is not a production freeze.
 white=binary_dilation((C[:,:,3]>0)|(np.array(A)[:,:,3]>180),iterations=12);Image.fromarray((white*255).astype('uint8')).save(I/'04_single_edit_white.png')
 prompt=f'''将第一张唯一完整、不透明的新F{f:03}姿态自然完稿为第三张实物的二维手绘角色风格。第一张只是一张完整体量施工输入，不是曝光成品；模型须按该完整新姿态画真实人物，不能直接把技术体块当成最终画稿。第二张从第一张接触区同机位直接放大，第三张只含已锁032的两个人物头部身份与内部材质，不含完整旧身或旧臂；第四张白可完稿、黑不变，唯一单mask不反转。\n{stages[f]}\n所有手必须真实一拇四指，掌厚、指腹对握和完整腕臂连接成立。R/L按角色自身，奶奶仅近L戴玉镯，R腕不添任何饰物。人物头颈、胸廓、骨盆、两腿和支撑脚整体转动，不能只扭脸或只摆手；完整肩袖—上臂—肘—前臂—腕可追，骨长用短缩和体量表达，禁止拉长。四根硬杆分别对应turtle.head[20,0]、turtle.shell[0,40]、crane.body[-75,6]、crane.neck3[10,0]，不能合成软绳或换绑。只修施工线为自然关节、衣褶与中性固有色，场景灯光后接入。输出单张1672×941透明人物层，无骨架、圆圈假掌、文字、灰影、场景、额外帧；不缩放裁切。'''
 paths=[I/'01_unique_opaque_complete_target.png',I/'02_exact_same_view_contacts_3x.png',I/'03_heads_internal_materials_only.png',I/'04_single_edit_white.png'];rows=[{'order':j+1,'path':str(q.resolve()),'sha256':sha(q),'size':list(Image.open(q).size)} for j,q in enumerate(paths)];args={'prompt':prompt,'transparent_background':True,'referenced_image_paths':[q['path'] for q in rows]};(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n');(F/'prompt_prepared_zh.txt').write_text(prompt+'\n');(F/'input_manifest.json').write_text(json.dumps({'inputs':rows,'status':'INPUT_PENDING_ASTRA_SHORT_REVIEW','model_calls':0,'submitted':False,'generation_authorized':False,'source_actual032_sha256':sha(source),'new_full_old_pose_competition':False,'manual_construction_only_not_production_art':True,'crane_angles_technical_occlusion_accepted_by_Astra':True,'whole_body_mask_is_draft_not_immutable_production_contract':True},ensure_ascii=False,indent=2)+'\n')
 bg=Image.new('RGBA',im.size,'#bdc1c4');bg.alpha_composite(im);bg=bg.convert('RGB');x=(i%2)*836;y=(i//2)*505;full.paste(bg.resize((836,470),Image.Resampling.LANCZOS),(x,y+35));df.text((x+12,y+6),f'INPUT F{f:03} · B04/B05整批短核 / 0生图',font=font,fill='#263743');contacts.append((f,bg.crop(box)))
full.save(P/'batch_036_057_complete_targets_REVIEW_ONLY.png');board=Image.new('RGB',(2520,660),'#bdc1c4');db=ImageDraw.Draw(board)
for i,(f,im) in enumerate(contacts):
 im.thumbnail((410,605));board.paste(im.resize((int(im.width*1.6),int(im.height*1.6)),Image.Resampling.NEAREST) if im.width*1.6<=410 else im,(i*420,45));db.text((i*420+8,8),f'INPUT F{f:03} 接触',font=font,fill='#263743')
board.save(P/'batch_036_057_contacts_REVIEW_ONLY.png');print('4 sets x4 actual input files, full prepared prompts and SHA; 0 calls/submissions. No production frame created.')
