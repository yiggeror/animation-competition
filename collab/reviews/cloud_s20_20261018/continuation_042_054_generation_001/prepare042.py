from pathlib import Path
import ast,copy,json,math,hashlib,subprocess,shutil,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,binary_fill_holes,label
P=Path(__file__).resolve().parent;PACK=P.parent;ROOT=PACK.parents[2];F=P/'F042';I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
A=np.array(Image.open(PACK/'costume_036_039_zero_call_001/S20_F039_costume_corrected.png').convert('RGBA'));V=np.array(Image.open(ROOT/'collab/refs/xiaoman_turnaround_v4_draft.png').convert('RGB'));N=np.array(Image.open(PACK/'B04_B05_generation_002/F039/raw_original.png').convert('RGBA'));S=np.array(Image.open(PACK/'handoff_008_020_032_generation_002/F032/S20_F032_accepted.png').convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W));NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
def path(d,fill='#ffcfac',stroke='#644b3c',width=2.8):return ET.Element('{%s}path'%NS,{'d':d,'fill':fill,'stroke':stroke,'stroke-width':str(width),'stroke-linejoin':'round','stroke-linecap':'round'})
env={'np':np,'path':path};tree=ast.parse((PACK/'B04_B05_generation_002/prepare039.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='limb'],type_ignores=[]),'limb','exec'),env);limb=env['limb']
def poly(points,shape=(W,H)):
 im=Image.new('L',shape);ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def warp(layer,Q,t):
 inv=np.linalg.inv(Q);return np.array(Image.fromarray(layer).transform((W,H),Image.Transform.AFFINE,tuple(np.column_stack((inv,-inv@np.array(t))).ravel()),Image.Resampling.BICUBIC))
def render(root,name):
 svg=I/(name+'.svg');ET.ElementTree(root).write(svg,encoding='unicode');subprocess.run(['node',str(PACK/'handoff_008_020_032_generation_002/render_static.cjs'),str(svg)],cwd=ROOT,check=True);return np.array(Image.open(svg.with_suffix('.png')).convert('RGBA'))
def svgroot():return ET.Element('{%s}svg'%NS,{'width':str(W),'height':str(H),'viewBox':f'0 0 {W} {H}'})
def over(a,b):return np.array(Image.alpha_composite(Image.fromarray(a),Image.fromarray(b)))
def extract(roi,kind):
 vy,vx=np.indices(V.shape[:2]);x0,y0,x1,y1=roi;area=(vx>=x0)&(vx<x1)&(vy>=y0)&(vy<y1);sat=V.max(2).astype(int)-V.min(2).astype(int)
 if kind=='collar':
  core=area&(V.min(2)>227)&(sat<42);ids,n=label(core);sizes=np.bincount(ids.ravel());ks=np.flatnonzero(sizes>45);ks=ks[ks!=0];core=binary_fill_holes(np.isin(ids,ks))
 else:
  if kind=='head':area&=(vy<240)|((vx<755)&(vy<281))|((vx>=750)&(vx<805)&(vy<268));area&=(vy<267)|(V.min(2)<100)
  core=area&((sat>11 if kind=='head' else sat>17)|(V.min(2)<100 if kind=='head' else V.min(2)<120));core=binary_fill_holes(core)
 out=np.zeros((*V.shape[:2],4),np.uint8);out[:,:,:3]=V;out[:,:,3]=(binary_dilation(core,iterations=1)&area)*255;return out
root=svgroot();defs=ET.SubElement(root,'{%s}defs'%NS);pat=ET.SubElement(defs,'{%s}pattern'%NS,{'id':'dots','width':'17.8','height':'30.83','patternUnits':'userSpaceOnUse'});ET.SubElement(pat,'{%s}rect'%NS,{'width':'17.8','height':'30.83','fill':'#f2c64b'})
for x,y in [(4,4),(12.9,19.415)]:ET.SubElement(pat,'{%s}circle'%NS,{'cx':str(x),'cy':str(y),'r':'2.6','fill':'#fff8e9'})
for hip,knee,ankle,col in [([573.9,555.8],[578.55,727.85],[580.1,887.5],'#efc09f'),([626.6,560.45],[640.55,715.45],[652.95,873.55],'#ffcfac')]:root.append(limb(hip,knee,ankle,[20,17,11],col))
hands=[];wrists={};handinfo=[];fits=json.loads((PACK/'F039_whole_source_diagnostic_001/uniform_transform_and_clamps.json').read_text())['native_shaft_fits']
for side,srcside,roi,pivot,wr,dest,slope in [('R','L',[(739,379),(795,379),(807,398),(803,442),(762,445),(739,431)],[774,418.61387755],[750,419],[476,432],(432-375)/(476-245)),('L','R',[(697,323),(741,317),(764,336),(774,375),(737,387),(699,378)],[735,365.15443878],[701,360],[482,503],(503-440)/(482-230))]:
 srcfit=fits[1 if srcside=='L' else 0];theta=math.atan(slope)+math.atan(srcfit['slope']);c,s=math.cos(theta),math.sin(theta);Q=np.array([[c,-s],[s,c]])@np.diag([-1,1]);t=np.array(dest)-Q@pivot;m=poly(roi)&(N[:,:,3]>0);L=np.zeros_like(N);L[m]=N[m];hands.append(warp(L,Q,t));wrists[side]=(Q@wr+t).tolist();handinfo.append({'side':side,'guide_only_source_opposite_native_hand':srcside,'local_hand_reflection_only':True,'target_clamp':dest,'wrist':wrists[side],'matrix':np.column_stack((Q,t)).tolist()})
root.append(limb([583.2,379.1],[546,470.55],wrists['R'],[17,16,10],'#efc09f'))
old=ET.parse(PACK/'next_036_057_inputs_002/F042/inputs/01_unique_opaque_complete_target.svg').getroot();X=next(c for c in old if c.attrib.get('transform')=='translate(608 190) scale(1.55)');g=ET.SubElement(root,'{%s}g'%NS,{'transform':'translate(608 190) scale(1.55)'})
for n in [20,21,23]:
 node=copy.deepcopy(X[n]);
 if n in [20,21]:node.set('fill','url(#dots)')
 g.append(node)
root.append(path('M570 366 Q579 355 590 365 L599 386 Q599 401 585 408 L573 397 Z','#f2c64b'))
root.append(limb([629.7,383.75],[615.75,489.15],wrists['L'],[18,16,10],'#ffcfac'))
root.append(path('M616 363 Q632 352 645 367 Q658 386 646 404 Q635 415 620 405 Q610 392 616 363 Z','#f2c64b'))
child=render(root,'_new_child_contours');head=warp(extract((650,25,875,286),'head'),np.diag([-.95,.95]),[1348.05,130]);collar=warp(extract((730,233,818,301),'collar'),np.diag([-.95,.95]),[1348.05,130]);child=over(child,collar);child=over(child,head)
near=np.zeros_like(S);nm=poly([(535,853),(562,852),(582,859),(584,878),(597,889),(623,895),(632,904),(636,911),(635,916),(626,920),(601,925),(538,919),(522,908),(523,884)]);near[nm]=S[nm]
shoes=[]
for donor,p0,p1,q0,q1 in [(extract((695,873,860,969),'shoe'),[760,925],[846,956],[652.95,873.55],[577,904]),(near,[556,880],[633,918],[580.1,887.5],[504,918])]:
 p0,p1,q0,q1=[np.array(v,float) for v in [p0,p1,q0,q1]];R=np.diag([-1,1]);u=R@(p1-p0);v=q1-q0;z=complex(*v)/complex(*u);Q=np.array([[z.real,-z.imag],[z.imag,z.real]])@R;shoes.append(warp(donor,Q,q0-Q@p0))
for L in shoes+hands:child=over(child,L)
ids,n=label(child[:,:,3]>0);sizes=np.bincount(ids.ravel());child[np.isin(ids,np.flatnonzero((sizes<180)&(np.arange(len(sizes))>0)))]=0
# Approved grandma plate; clear complete old bare right arm, never near jade arm.
G=(xx>=865)&(A[:,:,3]>0);rr,gg,bb=A[:,:,:3].astype(float).transpose(2,0,1);area=poly([(869,347),(928,346),(959,372),(985,396),(1046,408),(1050,448),(1006,448),(949,429),(903,418),(867,409)]);clear=binary_dilation(area&(A[:,:,3]>40)&(rr>170)&(gg>110)&(bb>gg*.72)&(rr>gg+9),iterations=3)&area;G&=~clear;GP=np.zeros_like(A);GP[G]=A[G]
gr=svgroot();gr.append(limb([1067,285],[985.349,410.83],[913,354],[21,19,12],'#ffd0ad'))
class Helpers:
 C={'near':'#ffd0ad','ink':'#644b3c'}
 def path(self,d,fill='none',stroke='#644b3c',w=1.4,**kw):return ET.tostring(path(d,fill,stroke,w),encoding='unicode')
 def ellipse(self,x,y,rx,ry,fill,stroke='#644b3c',w=1.4,more=''):return f'<ellipse xmlns="{NS}" cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" {more}/>'
ns={'r':Helpers()};tree=ast.parse((PACK/'next_036_057_inputs_002/prepare_added_inputs.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['adult_R_CB','adult_L_CN']],type_ignores=[]),'hands','exec'),ns);gr.append(ET.fromstring(ns['adult_R_CB']()));GR=render(gr,'_new_GR_contours')
prop=Image.new('RGBA',(W*4,H*4));d=ImageDraw.Draw(prop);axes=json.loads((PACK/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods'];lines=[]
for role in ['C_N','C_B']:
 q=axes[role];lines.append((role,q['shaft_tip_master_px'],[952,q['slope']*952+q['intercept']]))
for role,tip,clamp in [('T_H',[245,375],[476,432]),('T_S',[230,440],[482,503])]:
 m=(clamp[1]-tip[1])/(clamp[0]-tip[0]);lines.append((role,tip,[clamp[0]+30,clamp[1]+30*m]))
for role,a,b in lines:d.line([tuple(v*4 for v in a),tuple(v*4 for v in b)],fill='#675034',width=16);d.line([tuple(v*4 for v in a),tuple(v*4 for v in b)],fill='#b28b52',width=10)
props=np.array(prop.resize((W,H),Image.Resampling.LANCZOS));B=over(props,GR);B=over(B,GP);B=over(B,child);Image.fromarray(B).save(I/'01_unique_complete_F042_target.png');Image.fromarray(B).crop((415,285,1015,540)).resize((1200,510),Image.Resampling.NEAREST).save(I/'02_same_view_contacts_2x.png')
edit=binary_dilation((child[:,:,3]>0)|((xx<865)&(A[:,:,3]>0))|(GR[:,:,3]>0)|clear,iterations=10)&~G
# All actual grandma left-arm pixels and fixed head/body are protected.
Image.fromarray(np.uint8(edit)*255).convert('RGB').save(I/'03_whole_child_and_GR_white_mask.png')
card=Image.new('RGB',(980,420),'#bdc1c4');src=Image.fromarray(A)
for box,xy in [((525,240,690,375),(15,15)),((1020,30,1200,220),(220,15)),((556,380,645,490),(450,15)),((530,550,680,700),(580,15)),((520,840,740,930),(15,260))]:card.paste(src.crop(box).convert('RGBA'),xy,src.crop(box).getchannel('A'))
card.save(I/'04_identity_material_patches_only.png');bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));bg.convert('RGB').save(F/'target_gray.jpg',quality=95)
info={'frame':42,'inputs_only_not_production':True,'image_calls':0,'mother':str((PACK/'costume_036_039_zero_call_001/S20_F039_costume_corrected.png').relative_to(ROOT)),'whole_body_turn':'support/feet/pelvis/chest/head neck all left profile; no whole person mirror','hand_guides':handinfo,'fixed_ownership':{'X.R':'T_H','X.L':'T_S','G.R':'C_B only first contact','G.L':['C_B','C_N']},'closed_joint_rings':False,'white_collar_dense_round_dots_open_toe_red_strap_sandals':True,'review_requires_native_output_complete_arm_and_clamp':True};(F/'input_preparation.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n');print(json.dumps(info,ensure_ascii=False))
