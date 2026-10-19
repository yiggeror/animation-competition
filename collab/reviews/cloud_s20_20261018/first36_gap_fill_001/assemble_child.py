from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation
P=Path(__file__).resolve().parent;PACK=P.parent;OLD=PACK/'handoff_008_020_032_generation_002';f=int(sys.argv[1]);F=P/f'F{f:03}';I=F/'inputs'
source=OLD/'F008/S20_F008_accepted.png';A=np.array(Image.open(source).convert('RGBA'));C=np.array(Image.open(F/'art/child_F020_complete_pose.png').convert('RGBA'));hand=np.array(Image.open(F/'art/closed_hand_coverage.png'))[:,:,3]>0
rod=np.array(Image.open(PACK/'F008_corrected_input_001/local_masks/protect_four_real_rods.png'))>0
M=np.array(Image.open(PACK/'handoff_008_020_032_reference_001/F020/04_edit_white.png'))>0
M&=(~rod|binary_dilation(hand,iterations=1));M[750:]=False
out=A.copy();out[M]=C[M]
Image.fromarray(out).save(I/'01_unique_complete_opaque_target.png');Image.fromarray((M*255).astype('uint8')).save(I/'04_edit_white.png')
box=(565,275,1005,515);im=Image.fromarray(out);im.crop(box).resize((1320,720),Image.Resampling.NEAREST).save(I/'02_exact_target_contact_crop_3x.png')
bg=Image.new('RGBA',im.size,'#bdc1c4');bg.alpha_composite(im);bg.convert('RGB').save(F/'qa/input_full_gray.png');bg.crop(box).resize((1320,720),Image.Resampling.NEAREST).convert('RGB').save(F/'qa/input_contact_3x.png')
stage={12:'012首次接握：孩子近R拇指与屈曲食中指真实夹住龟头签T_H；远L五指仍张开，在龟壳签T_S下方保持空气，零接触。奶奶低裸R掌仍闭合支持两签。',15:'015第二手接握：孩子近R已稳握T_H不移动，远L食中无名小指开始绕T_S屈曲，拇指尚未全压合，明确从张开走向对握。奶奶低裸R掌仍闭合支持两签。',18:'018接收双握建立：孩子近R稳握T_H、远L稳握T_S，拇指对四指真实闭合，共同承重；奶奶低裸R仍闭合支持两签，尚未撤手。'}[f]
prompt=f'''将第一张F{f:03}唯一完整不透明新姿态底，自然完稿为第三张一致的二维手绘风格。第一张已清除旧动作占位，具备正确完整新头颈、胸廓骨盆和两条肩袖—上臂—肘—前臂—腕—五指体量；不是灰影或骨架。第二张是第一张的直接同机位接触放大，第三张仅是旧实物的头部身份和内部材质裁片，无完整旧身/旧臂，第四张白可完稿、黑保持原RGBA，不能反转。严格依第一张的新整身动作，不回旧母态或双空手。\n{stage}\nX.R只接T_H=龟head[20,0]，X.L只接T_S=龟shell[0,40]；每根沿原直轴进入自己的掌内，由真实指腹与拇指相对夹住，不能让竹签透掌或只贴拳。所有手均真实五指，不能圆球假掌、多指、缺指。保持第一张完整两臂长度与肩肘腕连接，头颈胸盆整体姿态与固有色，不拉脸、不伸长骨段。\n奶奶整个人及高位唯一玉镯近L臂、两鹤签、低位供应握掌及两龟签可见轴、人物鞋踝皆原像素保护。不得提前松奶奶手或转交鹤签，不改轴端、偶、机位与灯。只在白域把简化参考体量画成自然衣褶、肤肉、关节和掌厚，透明背景，无场景、灯光烘焙、文字、线骨架、重影或其他帧。严格1672×941，不缩放、裁切、变形或移位。'''
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[I/'01_unique_complete_opaque_target.png',I/'02_exact_target_contact_crop_3x.png',I/'03_accepted008_head_materials_only.png',I/'04_edit_white.png']
rows=[{'order':n+1,'path':str(p.resolve()),'sha256':sha(p),'size':list(Image.open(p).size)} for n,p in enumerate(files)]
args={'prompt':prompt,'transparent_background':True,'referenced_image_paths':[r['path'] for r in rows]}
(F/'tool_args_prepared.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n');(F/'input_manifest.json').write_text(json.dumps({'inputs':rows,'source':str(source.resolve()),'source_sha256':sha(source),'input_only_not_generated_drawing':True},ensure_ascii=False,indent=2)+'\n')
print('Prepared',f,'4 input references, zero calls')
