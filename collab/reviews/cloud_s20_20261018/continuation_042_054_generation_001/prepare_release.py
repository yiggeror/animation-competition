from pathlib import Path
import ast,sys,json,copy,subprocess,hashlib,shutil,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,binary_fill_holes
P=Path(__file__).resolve().parent;PACK=P.parent;ROOT=PACK.parents[2];f=int(sys.argv[1]);assert f in [45,47];F=P/f'F{f:03}';I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
mother=P/'F042/S20_F042_semantic_closed.png' if f==45 else P/'F045/S20_F045_accepted.png';A=np.array(Image.open(mother).convert('RGBA'));B=np.array(Image.open(PACK/'costume_036_039_zero_call_001/S20_F039_costume_corrected.png').convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W));NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
def path(d,fill='#ffd0ad',stroke='#644b3c',width=2.8):return ET.Element('{%s}path'%NS,{'d':d,'fill':fill,'stroke':stroke,'stroke-width':str(width),'stroke-linejoin':'round','stroke-linecap':'round'})
def poly(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
ns={'np':np,'path':path};tree=ast.parse((PACK/'B04_B05_generation_002/prepare039.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='limb'],type_ignores=[]),'limb','exec'),ns)
class Helpers:
 C={'near':'#ffd0ad','ink':'#644b3c'}
 def path(self,d,fill='none',stroke='#644b3c',w=1.4,**kw):return ET.tostring(path(d,fill,stroke,w),encoding='unicode')
 def ellipse(self,x,y,rx,ry,fill,stroke='#644b3c',w=1.4,more=''):return f'<ellipse xmlns="{NS}" cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" {more}/>'
handns={'r':Helpers()};tree=ast.parse((PACK/'next_036_057_inputs_002/prepare_added_inputs.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='adult_L_CN'],type_ignores=[]),'hand','exec'),handns)
root=ET.Element('{%s}svg'%NS,{'width':str(W),'height':str(H),'viewBox':f'0 0 {W} {H}'});root.append(ns['limb']([1160,285],[1095,435],[984,333 if f==45 else 325],[24,23,12],'#ffd0ad'));hand=handns['adult_L_CN']()
if f==45:hand=hand.replace('M943 284 Q932 278 926 283 Q924 288 933 291 L944 296 Q949 292 943 284 Z','M949 307 Q942 315 934 326 Q930 331 933 334 Q938 338 944 331 L952 319 Q955 311 949 307 Z')
root.append(ET.fromstring('<g xmlns="%s">'%NS+hand+'</g>'));svg=I/'new_complete_GL_guide.svg';ET.ElementTree(root).write(svg,encoding='unicode');subprocess.run(['node',str(PACK/'handoff_008_020_032_generation_002/render_static.cjs'),str(svg)],cwd=ROOT,check=True);L=np.array(Image.open(svg.with_suffix('.png')).convert('RGBA'))
region=poly([(892,268),(955,266),(986,319),(1030,349),(1154,343),(1185,369),(1191,412),(1150,457),(1100,458),(983,378),(958,375),(931,358),(908,351),(892,328)])
if f==45:
 r,g,b=B[:,:,:3].astype(float).transpose(2,0,1);skin=(B[:,:,3]>30)&(r>170)&(g>110)&(b>g*.72)&(r>g+9);jade=(B[:,:,3]>30)&(g>r*1.05)&(g>b*1.05);oldR=poly([(869,347),(928,346),(959,372),(985,396),(1046,408),(1050,448),(1006,448),(949,429),(903,418),(867,409)]);oldL=binary_dilation((skin|jade)&region&~oldR,iterations=3)&region
else:oldL=np.array(Image.open(P/'F045/native_GL_layer.png').convert('RGBA'))[:,:,3]>0;oldL=binary_dilation(oldL,iterations=3)&region
ar,ag,ab=A[:,:,:3].astype(float).transpose(2,0,1);blue=(A[:,:,3]>30)&(ar<180)&(ag>ar*1.03)&(ab>ag*.95);blue=binary_fill_holes(blue);oldL&=~blue;forefront=poly([(967,323),(997,312),(1116,417),(1093,459),(1069,449),(972,348)]);blue&=~forefront
base=A.copy();base[oldL]=0;props=Image.new('RGBA',(W*4,H*4));d=ImageDraw.Draw(props);C=json.loads((PACK/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods']
for role in ['C_N','C_B']:
 q=C[role];a=q['shaft_tip_master_px'];b=[952,q['slope']*952+q['intercept']];d.line([tuple(v*4 for v in a),tuple(v*4 for v in b)],fill='#675034',width=16);d.line([tuple(v*4 for v in a),tuple(v*4 for v in b)],fill='#b28b52',width=10)
T=Image.alpha_composite(props.resize((W,H),Image.Resampling.LANCZOS),Image.open(P/'F042/semantic_closed_native_GR.png').convert('RGBA'));T=Image.alpha_composite(T,Image.fromarray(base));T=Image.alpha_composite(T,Image.fromarray(L));target=np.array(T);target[blue]=A[blue];Image.fromarray(target).save(I/'01_unique_complete_release_target.png');Image.fromarray(target).crop((840,270,1195,465)).resize((1065,585),Image.Resampling.NEAREST).save(I/'02_same_view_native_contact_3x.png');edit=binary_dilation(oldL|(L[:,:,3]>0),iterations=8)&region&~blue
GR=np.array(Image.open(P/'F042/semantic_closed_native_GR.png').convert('RGBA'))[:,:,3]>100;edit&=~(GR&~oldL&(L[:,:,3]==0));edit&=~((xx<898)&(yy>290)&(yy<375));Image.fromarray(np.uint8(edit)*255).convert('RGB').save(I/'03_complete_GL_only_white_mask.png');shutil.copyfile(P/'F042/inputs/04_identity_material_patches_only.png',I/'04_material_identity_patches.png');bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(target));bg.convert('RGB').save(F/'target_gray.jpg',quality=96)
action='左手仅开始松开下方C_B：拇指/食指仍牢夹上方C_N(929,317.54)，中指/无名指向上卷起；只有小指尚以指垫在(934,331)轻托下方C_B，属于过渡支撑，不能误成全掌又夹两杆。' if f==45 else '左手完全释放下方C_B：拇指/食指仍牢夹上方C_N(929,317.54)，另外三指全部朝掌内上方自然卷起，与下杆保持明确可见空隙，没有任何指尖还托下杆。下杆C_B现在只由裸腕右手在(875,321.5)夹持。'
prompt=f'''把第一张唯一完整F{f:03}新动作施工target自然手绘完稿，只画第三张唯一mask白域的奶奶带玉镯左整臂/腕/五指掌。第二张同机位接触放大，第四张只作局部身份材质；不能取旧姿。新前臂、腕和掌自然连续，玉镯在左腕，不可断腕/双掌/球关节。{action}\n腕随完整前臂一起轻轻上提，肩约(1160,285)、肘约(1095,435)、腕(984,{333 if f==45 else 325})；只参考连续体积，不照抄平色折线。左手在裸右臂之前，自然负空间保留，不把两臂之间灰隙填成皮肤。原右掌及右整臂刚性位置和(875,321.5)拇指食指对夹C_B严格保持，裸右腕没有镯，右手不碰上方C_N。两根鹤签保持同一原直轴，不折不漂：C_N y=.2348760341x+99.34370423，C_B y=.1635724171x+178.40816867；左手拇指/食指的新对夹必须真夹C_N，不可夹到C_B或仅悬在杆旁。\n小满完整左向头颈/全身/两原生握掌/白圆领/密白圆点/红搭带露趾凉鞋、两根龟签、奶奶头眼镜蓝花宽袖全身和原生裸右整臂掌都在黑域逐像素保护。不能移动、重画或更换角色造型。只清除旧左掌/臂残影，把新完整左臂接回原蓝袖下，最多补原左臂腾出后的真实遮挡小区，保已有原生右掌/臂。不得给右手加镯。\n输出单张1672×941透明人物层，同画布同站位，不缩放裁切，不加文字/骨架/背景/地影/额外帧，灯光由场景接入。圆形肩/肘是施工体积，不得照抄成球；奶奶保持真实蓝花宽短袖，只有小满是黄泡袖。'''
(F/'prompt_submitted_zh.txt').write_text(prompt);paths=[(I/n).resolve() for n in ['01_unique_complete_release_target.png','02_same_view_native_contact_3x.png','03_complete_GL_only_white_mask.png','04_material_identity_patches.png']];sn=F/'actual_input_snapshots';sn.mkdir(exist_ok=True);rec=[]
for n,p in enumerate(paths,1):q=sn/(f'{n:02}_'+p.name);shutil.copyfile(p,q);rec.append({'path':str(p),'snapshot':str(q),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()})
args={'prompt':prompt,'transparent_background':True,'referenced_image_paths':[str(p) for p in paths]};(F/'tool_args_exact.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n');(F/'input_receipt.json').write_text(json.dumps({'frame':f,'mother':str(mother),'mother_sha256':hashlib.sha256(mother.read_bytes()).hexdigest(),'inputs':rec,'image_calls_yet':0},ensure_ascii=False,indent=2)+'\n');print(f'F{f:03} inputs ready')
