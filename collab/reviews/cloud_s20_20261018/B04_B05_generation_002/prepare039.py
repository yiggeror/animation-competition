"""One corrected next-state input; real grip/shaft pairs, no closed joint rings."""
from pathlib import Path
import xml.etree.ElementTree as ET,copy,json,math,subprocess,hashlib,shutil,datetime
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation
P=Path(__file__).resolve().parent;PACK=P.parent;ROOT=PACK.parents[2];F=P/'F039';I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
assert json.loads((P/'F036/status.json').read_text())['state']=='AUTHOR_ACCEPTED'
A=np.array(Image.open(P/'F036/S20_F036_accepted.png').convert('RGBA'));S=np.array(Image.open(PACK/'handoff_008_020_032_generation_002/F032/S20_F032_accepted.png').convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W));NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
root=ET.Element('{%s}svg'%NS,{'width':str(W),'height':str(H),'viewBox':f'0 0 {W} {H}'})
def path(d,fill='#ffcfac',stroke='#644b3c',width=2.8):return ET.Element('{%s}path'%NS,{'d':d,'fill':fill,'stroke':stroke,'stroke-width':str(width),'stroke-linejoin':'round','stroke-linecap':'round'})
def limb(S,E,W,widths,skin):
 S,E,W=[np.array(v,float) for v in [S,E,W]];u=(E-S)/np.linalg.norm(E-S);v=(W-E)/np.linalg.norm(W-E);n=np.array([-u[1],u[0]]);m=np.array([-v[1],v[0]]);a,b,c=widths;f=lambda p:f'{p[0]:.3f} {p[1]:.3f}'
 w=(n+m)*b/(1+float(n@m));turn=float(u[0]*v[1]-u[1]*v[0])
 plus=f'L{f(E+n*b)} Q{f(E+w)} {f(E+m*b)}' if turn<0 else f'L{f(E+w)}'
 minus=f'L{f(E-m*b)} Q{f(E-w)} {f(E-n*b)}' if turn>0 else f'L{f(E-w)}'
 return path(f'M{f(S+n*a)} {plus} L{f(W+m*c)} L{f(W-m*c)} {minus} L{f(S-n*a)} Z',skin)
def poly(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def rigid(data,mask,pivot,dest,angle):
 layer=np.zeros_like(data);layer[mask]=data[mask];c=math.cos(angle);s=math.sin(angle);px,py=pivot;dx,dy=dest
 inv=(c,s,px-c*dx-s*dy,-s,c,py+s*dx-c*dy)
 return np.array(Image.fromarray(layer).transform((W,H),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC))
raw_rods=json.loads((PACK/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods'];r,g,b=S[:,:,:3].astype(float).transpose(2,0,1);wood=(S[:,:,3]>80)&(r>g+10)&(g>b+10)&(b<g*.76)
handR=poly([(789,363),(798,348),(813,340),(825,335),(841,341),(849,353),(850,379),(837,390),(812,391),(793,386)])
handL=poly([(823,416),(831,402),(847,394),(861,394),(878,402),(882,432),(870,446),(847,448),(832,440),(824,431)])
shafts={};fits={}
for role in ['T_H','T_S']:
 q=raw_rods[role];distance=np.abs(yy-q['slope']*xx-q['intercept'])/np.hypot(1,q['slope']);band=(distance<13)&(xx>=773)&(xx<951)&(yy>320)&(yy<461);shafts[role]=binary_dilation(wood&band&~handR&~handL,iterations=1)&band&~handR&~handL
 # Fit the real output pigment before rotating; never infer a new axis from a fist.
 samples=[]
 for x in range(878,912):
  ys=np.flatnonzero(wood[:,x]&band[:,x]);split=(raw_rods['T_H']['slope']*x+raw_rods['T_H']['intercept']+raw_rods['T_S']['slope']*x+raw_rods['T_S']['intercept'])/2
  ys=ys[ys<split] if role=='T_H' else ys[ys>=split]
  if len(ys):samples.append((x,float(np.mean(ys))))
 fits[role]=np.polyfit(np.array(samples)[:,0],np.array(samples)[:,1],1).tolist()
old_turtle=shafts['T_H']|shafts['T_S']
for role,limit in [('T_H',861),('T_S',900)]:
 m,b0=fits[role];other='T_S' if role=='T_H' else 'T_H';mo,bo=fits[other];distance=np.abs(yy-m*xx-b0)/np.hypot(1,m);do=np.abs(yy-mo*xx-bo)/np.hypot(1,mo)
 ownwood=wood&(distance<=do)&(distance<5)&(xx>=773)&(xx<=limit)&~handR&~handL
 shafts[role]=binary_dilation(ownwood,iterations=1)&(distance<=do)&(xx>=773)&(xx<=limit)&~handR&~handL
grips=[];wrists={};rows=[]
for side,role,hand,pivot,dest,tip,wr in [('R','T_H',handR,[820,365.1323396567299],[740,380],[650,350],[797,377.1323396567299]),('L','T_S',handL,[850,416.6729900632339],[765,430],[630,400],[827,428.6729900632339])]:
 theta=math.atan2(dest[1]-tip[1],dest[0]-tip[0])-math.atan(fits[role][0]);area=hand|shafts[role];mask=area&(S[:,:,3]>5)&binary_dilation(area&(S[:,:,3]>180),iterations=1);layer=rigid(S,mask,pivot,dest,theta);grips.append(layer)
 c,s=math.cos(theta),math.sin(theta);Q=np.array([[c,-s],[s,c]]);wrists[side]=(Q@(np.array(wr)-pivot)+dest).tolist();rows.append({'hand':'X.'+side,'rod':role,'pivot':pivot,'new_grip':dest,'rotation_deg':math.degrees(theta),'scale':1,'new_real_wrist':wrists[side]})
 # Whole scene shaft is behind the child; only the true short segment is protected.
 ms,bs=fits[role];anchor=Q@(np.array([pivot[0],ms*pivot[0]+bs])-pivot)+dest;mt=(dest[1]-tip[1])/(dest[0]-tip[0]);bt=anchor[1]-mt*anchor[0];tail=Q@(np.array([944,ms*944+bs])-pivot)+dest;front=[tip[0],mt*tip[0]+bt]
 root.append(path(f'M{front[0]} {front[1]} L{tail[0]} {tail[1]}','none','#675034',4))
 root.append(path(f'M{front[0]} {front[1]} L{tail[0]} {tail[1]}','none','#b28b52',2.5))
rod_count=len(root)
# New whole child legs, pelvis/chest, and two-eyed intermediate head from039.
for hip,knee,ankle,col in [([580.1,555.8],[578.55,724.75],[580.1,887.5],'#efc09f'),([634.35,560.45],[645.2,718.55],[652.95,873.55],'#ffcfac')]:root.append(limb(hip,knee,ankle,[20,17,10],col))
old=ET.parse(PACK/'next_036_057_inputs_002/F039/inputs/01_unique_opaque_complete_target.svg').getroot();X=next(c for c in old if c.attrib.get('transform')=='translate(608 190) scale(1.55)')
for n in [6,13]:g1=ET.Element('{%s}g'%NS,{'transform':'translate(608 190) scale(1.55)'});g1.append(copy.deepcopy(X[n]));root.append(g1)
root.append(limb([654,387],[701,453.5],wrists['L'],[17,16,10],'#efc09f'))
g1=ET.Element('{%s}g'%NS,{'transform':'translate(608 190) scale(1.55)'})
for n in range(20,31):g1.append(copy.deepcopy(X[n]))
root.append(g1)
root.append(path('M643 363 Q657 357 670 369 L680 389 Q681 407 664 412 L649 399 Z','#f2c64b'))
root.append(limb([564,382],[673,391],wrists['R'],[18,16,10],'#ffcfac'))
root.append(path('M552 357 Q565 348 578 361 Q591 377 583 393 L572 408 Q554 413 545 395 Q538 374 552 357 Z','#f2c64b'))
child=ET.ElementTree(root);svg=I/'_child_tmp.svg';child.write(svg,encoding='unicode');subprocess.run(['node',str(PACK/'handoff_008_020_032_generation_002/render_static.cjs'),str(svg)],cwd=ROOT,check=True);CH=np.array(Image.open(svg.with_suffix('.png')).convert('RGBA'));svg.unlink();svg.with_suffix('.png').unlink()
# Separate the four background shaft lines from the actual editable child.
for element in list(root)[:rod_count]:root.remove(element)
ET.ElementTree(root).write(svg,encoding='unicode');subprocess.run(['node',str(PACK/'handoff_008_020_032_generation_002/render_static.cjs'),str(svg)],cwd=ROOT,check=True);C=np.array(Image.open(svg.with_suffix('.png')).convert('RGBA'));svg.unlink();svg.with_suffix('.png').unlink()
G=((xx>=995)|((xx>=889)&(yy>=285)&(yy<=440))|((xx>=922)&(yy>=440)&(yy<=527)))&~binary_dilation(old_turtle,iterations=1)&(A[:,:,3]>0)
# Remove only the old bare R hand and its exposed forearm; keep blue blouse/near L.
ar,ag,ab=A[:,:,:3].astype(float).transpose(2,0,1);oldR=(xx>=922)&(xx<1031)&(yy>=440)&(yy<530)&(A[:,:,3]>80)&(ar>ag+12)&(ar>160)&(ag>110);clear=binary_dilation(oldR,iterations=2)&(xx<1031)&(yy>=440)&(yy<532);G&=~clear
high=Image.new('RGBA',(W*4,H*4));dC=ImageDraw.Draw(high)
for role in ['C_N','C_B']:
 q=raw_rods[role];points=[tuple(v*4 for v in q['shaft_tip_master_px']),(952*4,(q['slope']*952+q['intercept'])*4)];dC.line(points,fill=(103,80,52,255),width=16);dC.line(points,fill=(178,139,82,255),width=10)
base=np.array(high.resize((W,H),Image.Resampling.LANCZOS));base[G]=A[G]
# The original bare R palm moves rigidly upward to approach C_B, still no contact.
openmask=poly([(929,476),(932,469),(950,463),(966,447),(984,446),(1009,460),(1018,485),(1017,501),(991,511),(965,522),(939,519),(927,509)])&(S[:,:,3]>5)
angle=math.radians(40.8);openlayer=rigid(S,openmask,[978,487],[920,390],angle);wrist=(np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])@np.array([34,-7])+[920,390]).tolist();Sg=np.array([1067,285]);Wg=np.array(wrist);v=Wg-Sg;d=np.linalg.norm(v);u=v/d;t=(150**2-92**2+d*d)/(2*d);h=math.sqrt(150**2-t*t);n=np.array([-u[1],u[0]]);Eg=max([Sg+t*u+h*n,Sg+t*u-h*n],key=lambda q:q[1]).tolist()
back=ET.Element('{%s}svg'%NS,{'width':str(W),'height':str(H)});back.append(limb(Sg,Eg,wrist,[21,19,12],'#ffd0ad'));ET.ElementTree(back).write(svg,encoding='unicode');subprocess.run(['node',str(PACK/'handoff_008_020_032_generation_002/render_static.cjs'),str(svg)],cwd=ROOT,check=True);GR=np.array(Image.open(svg.with_suffix('.png')).convert('RGBA'));svg.unlink();svg.with_suffix('.png').unlink()
under=np.array(Image.alpha_composite(Image.fromarray(GR),Image.fromarray(base)));under[G]=base[G]
B=Image.alpha_composite(Image.fromarray(under),Image.fromarray(CH));protected=np.zeros((H,W),bool)
for L in grips+[openlayer]:B=Image.alpha_composite(B,Image.fromarray(L));protected|=L[:,:,3]>0
B=np.array(B);Image.fromarray(B).save(I/'01_unique_corrected_F039_target.png');Image.fromarray(B).crop((610,270,1015,490)).resize((1215,660),Image.Resampling.NEAREST).save(I/'02_same_view_grips_3x.png')
edit=binary_dilation((C[:,:,3]>0)|(GR[:,:,3]>0)|clear|((A[:,:,3]>80)&(xx<890)&(yy>145)),iterations=10)&~G&~protected
# No old C shafts are part of the old child cleanup domain.
for role in ['C_N','C_B']:
 q=raw_rods[role];dist=np.abs(yy-q['slope']*xx-q['intercept'])/np.hypot(1,q['slope']);edit&=~((dist<6)&(C[:,:,3]==0)&(xx>=670)&(xx<953))
Image.fromarray((edit*255).astype('uint8')).convert('RGB').save(I/'03_child_and_bare_R_edit_white.png')
shutil.copyfile(PACK/'next_036_057_inputs_002/F036/inputs/03_heads_internal_materials_only.png',I/'04_identity_heads_internal_only.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));bg.convert('RGB').save(F/'target_gray.jpg',quality=96)
info={'frame':39,'new_image_calls':0,'not_production_art':True,'source_actual036':str((P/'F036/S20_F036_accepted.png').relative_to(ROOT)),'real_child_grip_pairs':rows,'bare_G_R_open_palm':{'position':[920,390],'rotation_deg':40.8,'contact_count':0,'wrist':wrist,'chain':[Sg.tolist(),Eg,wrist]},'whole_child_turn':'support feet become foreshortened front; pelvis/chest front; full two-eyed head/neck intermediate; no mirrored old person','mask_scope':'whole child plus bareG.R whole arm only; real endpoint layers / rest ofG / C axes protected','G_L_ownership':['C_B','C_N']};(F/'input_preparation.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n');print(json.dumps(info,ensure_ascii=False))
