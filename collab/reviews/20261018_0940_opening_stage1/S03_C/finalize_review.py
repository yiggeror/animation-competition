from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
B=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def white(im):
 bg=Image.new('RGBA',im.size,(245,245,245,255));bg.alpha_composite(im.convert('RGBA'));return bg.convert('RGB')
for frame in [76]:
 p=B/'analysis'/f'F{frame:03d}_repair_manifest.json';d=json.loads(p.read_text());d['manual_review']='Pass as final candidate: both eyes half reopened, visually close to F074, same left/down-left gaze. Eyelids/eye whites clear after resampling, glasses line continuous; mask edge clean. All outside-mask pixels exactly preceding accepted F075.';d['repair']['generator_scale_native_to_output']=1254/512;p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
paths=[B/'inputs/k06_rightpad_1672x941.png']+[B/f'F{f:03d}_candidate.png' for f in [65,74,75,76]]+[B/'inputs/k07_rightpad_1672x941.png']
labels=['k06 F058-064 | 7f','F065-073 | 9f','F074 | 1f HALF','F075 | 1f CLOSED','F076-078 | 3f HALF','k07 F079-095 | 17f']
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
canvas=Image.new('RGB',(1140,640),(245,245,245));draw=ImageDraw.Draw(canvas)
for i,(p,label) in enumerate(zip(paths,labels)):
 im=white(Image.open(p));x=(i%3)*380;y=(i//3)*320;canvas.paste(im.crop((640,150,1020,430)),(x,y+32));draw.text((x+8,y+7),label,fill=(20,20,20),font=font)
canvas.save(B/'analysis/C_sequence_eyes_review.jpg',quality=95)
base=np.array(Image.open(paths[0]));union=np.zeros(base.shape[:2],bool)
for f in [65,74,75,76]:union|=np.array(Image.open(B/'analysis'/f'F{f:03d}_repair_mask.png'))>0
checks=[]
for f in [65,74,75,76]:
 p=B/f'F{f:03d}_candidate.png';a=np.array(Image.open(p));outside=~union
 checks.append({'frame':f,'dimensions':list(Image.open(p).size),'alpha_exact_k06':bool(np.array_equal(a[:,:,3],base[:,:,3])),'outside_brow_eye_union_changed_px':int(np.any(a[outside]!=base[outside],axis=1).sum()),'whole_body_below_y400_changed_px':int(np.any(a[400:]!=base[400:],axis=2).sum()),'sha256':sha(p)})
# Adjacent 50% onion, never registered/rescaled source pixels.
sheet=Image.new('RGB',(1200,420),(245,245,245));draw=ImageDraw.Draw(sheet)
for i in range(5):
 on=Image.blend(white(Image.open(paths[i])),white(Image.open(paths[i+1])),.5);on.save(B/'analysis'/f'C_onion50_pair_{i+1:02d}.png');thumb=on.crop((650,190,890,370));x=i*240;sheet.paste(thumb,(x,35));draw.text((x+7,8),f'{i+1}: {labels[i].split()[0]} > {labels[i+1].split()[0]}',fill=(20,20,20),font=font)
 # Fixed hand/fruit visual, same native crop except review thumbnail reduction.
 sheet.paste(on.crop((175,625,575,800)).resize((240,105)),(x,260))
sheet.save(B/'analysis/C_adjacent_onions50_review.jpg',quality=95)
source_records=json.loads((B/'source_manifest.json').read_text());source_check=[]
for r in source_records:
 p=Path(r['source']);source_check.append({'path':str(p),'sha256':sha(p),'matches_initial':sha(p)==r['source_sha256']})
records=[json.loads((B/'analysis'/f'F{f:03d}_repair_manifest.json').read_text()) for f in [65,74,75,76]]
manifest={'shot':'S03','segment':'C waiting/blink','status':'FOUR_LOCAL_CANDIDATES_READY_FOR_INDEPENDENT_REVIEW_NOT_IMPLEMENTED','call_count':4,'tool':'built-in image_gen','chain':['k06','F065','F074','F075','F076','old k07'],'new_exposure':[{'frame':65,'end_inclusive':73,'hold':9},{'frame':74,'end_inclusive':74,'hold':1},{'frame':75,'end_inclusive':75,'hold':1},{'frame':76,'end_inclusive':78,'hold':3}],'existing_endpoint':{'frame':79,'end_inclusive':95,'hold':17,'anchor':'old k07 unchanged'},'canvas':[1672,941],'source_padding_only':True,'source_full_frame_scaling':False,'local_donor_mapping':{'calls':[2,3,4],'source_crop':[600,120,1112,632],'native_crop_size':[512,512],'generated_donor_size':[1254,1254],'s_native_to_donor':1254/512,'s_donor_to_native':512/1254,'resampler':'Lanczos','limit':'only generated eye donor pixels; original full-frame base never scaled'},'frames':records,'static_checks':checks,'original_source_byte_checks':source_check,'closed_eye_white_check':json.loads((B/'analysis/F075_closure_check.json').read_text()),'review_images':['analysis/C_sequence_eyes_review.jpg','analysis/C_adjacent_onions50_review.jpg'],'lighting':'neutral base inherited; no new baked light, downstream once by Opus','legacy_endpoint_warning':'old k07 retains its known native pixel/alpha/line differences; no endpoint compensation or global registration applied','writes_scope':'local independent waiting folder only, no GitHub/docs/assets/main implementation writes'}
(B/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(B/'REVIEW_BRIEF.md').write_text('''# S03 C段候选交审\n\n- 4次内置image_gen，逐张按k06→065→074→075→076→旧k07；4张候选在本目录根，均1672×941 RGBA。\n- 065眉毛微抬并保持朝左下等待；074半闭，075全闭无瞳孔/眼白（双眼白色阈值计数各0），076重新半闭。每步已实际查看原件、接回前后和50%洋葱皮。\n- 初次F065全图输出静止区发生重绘，因此未直接作母源。按已确认的局部接回许可，用两眉显式mask接回k06；生成眉层向下7px，得到约3–4px微抬。母源是修后合格F065。\n- 074/075/076只生成512原位脸裁片；工具实际返回1254方图。仅生成供体等比逆映到512，s=1254/512=2.44921875，原位(600,120)。仅眼区mask接回上一合格整帧，原人物整底从不缩放。每张mask/坐标/SHA/源/原件/提示词见manifest及analysis。\n- 4张alpha与k06完全相同；眉眼mask联合范围外、y400以下身体/手瓜/盆盘所有像素均与k06完全相同。原k06/k07字节复核未变。眼镜线和采样后眼睑已实看，没有可见接缝。\n- 审片先看analysis/C_sequence_eyes_review.jpg及C_adjacent_onions50_review.jpg；后者第5列衔接旧k07，旧锚固有衣扣/线条等残差未掩盖，未配准、未重画。\n- 曝光不改：065–073=9f；074=1f；075=1f；076–078=3f；079–095仍旧k07=17f。未写GitHub/docs/assets/主实现。\n\n以上为作者逐张核验和交审材料，不替代Opus最终成片验收。\n''')
print(json.dumps({'call_count':4,'static_checks':checks,'source_checks':source_check},indent=2))
