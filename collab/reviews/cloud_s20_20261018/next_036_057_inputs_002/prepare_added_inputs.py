"""Review-only opaque volume/contact inputs from the frozen action protocol.
Zero image calls; not production character art or a new exposure schedule.
"""
from pathlib import Path
import importlib.util,json,math,re,copy
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;PACK=P.parent
spec=importlib.util.spec_from_file_location('approved_ref',PACK/'tools/build_references.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
r.C.update(ink='#644b3c',near='#ffd0ad',far='#efc09f',shirt='#7ba5cc',dress='#f2c64b')
_original_tube=r.tube
def solid_tube(a,b,r0,r1,col):
 return r.ellipse(a[0],a[1],r0,r0,col,'none',0)+r.ellipse(b[0],b[1],r1,r1,col,'none',0)+_original_tube(a,b,r0,r1,col)
r.tube=solid_tube
header='<svg xmlns="http://www.w3.org/2000/svg" width="1672" height="941" viewBox="0 0 1672 941">';end='</svg>'
Caxes=json.loads((PACK/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods']
def world_local(o,s,p):return [(p[0]-o[0])/s,(p[1]-o[1])/s]
def ik(S,W,a=150,b=92):
 S=np.array(S,float);W=np.array(W,float);v=W-S;d=np.linalg.norm(v);u=v/d;t=(a*a-b*b+d*d)/(2*d);h=math.sqrt(a*a-t*t);n=np.array([-u[1],u[0]]);return max([S+t*u+h*n,S+t*u-h*n],key=lambda q:q[1]).tolist()
def clean(s):
 s=re.sub(r'<line[^>]*stroke-dasharray[^>]*/>','',s)
 s=re.sub(r'<ellipse[^>]*stroke="#71818b"[^>]*/>','',s)
 return s

def adult_R_CB():
 p=r.path;skin=r.C['near'];ink=r.C['ink'];s=''
 s+=p('M915 342 Q902 333 888 333 C876 329 863 332 860 342 Q857 352 868 361 Q881 367 900 364 L915 363 Z',skin,w=1.35)
 for D in ['M864 335 Q863 325 870 322 Q877 320 882 325 Q885 331 878 335 L871 341 Q864 343 864 335 Z','M860 341 Q858 336 864 333 Q873 330 878 336 Q882 342 875 346 L866 349 Q861 348 860 341 Z','M864 350 Q863 344 870 342 Q880 339 884 345 Q887 352 880 355 L871 358 Q866 357 864 350 Z','M872 358 Q869 352 875 349 Q884 346 888 352 Q891 357 885 361 L879 364 Q874 364 872 358 Z']:s+=p(D,skin,w=1.0)
 s+=p('M892 344 C895 334 890 320 882 316 Q876 313 872 318 Q870 323 875 327 L881 338 Q882 345 887 349 Z',skin,w=1.2)
 s+=p('M880 348 Q884 354 895 354','none','#cc9e80',.85)
 return '<g transform="translate(875 321.5) scale(1.12) translate(-875 -321.5)">'+s+'</g>'

def adult_L_CN():
 p=r.path;skin=r.C['near'];s=p('M985 314 C970 308 966 294 951 288 Q937 284 927 294 Q922 303 935 311 L956 322 L977 337 Z',skin,w=1.4)
 for D in ['M937 285 Q923 280 915 286 Q913 291 923 294 L935 300 Q941 298 937 292 Z','M943 284 Q932 278 926 283 Q924 288 933 291 L944 296 Q949 292 943 284 Z','M932 295 Q922 286 915 292 Q912 299 922 304 L934 309 Q940 304 932 295 Z','M924 298 Q916 301 917 310 Q918 317 929 321 Q936 321 940 314 Q944 308 939 305 Q934 310 930 317 L926 315 Q924 311 928 307 Z']:s+=p(D,skin,w=1.0)
 s+=p('M949 300 Q940 301 932 311 Q929 316 926 316 Q921 313 925 307 L936 294 Q944 291 950 296 Z',skin,w=1.15)
 s+=p('M957 304 Q957 312 966 319','none','#cc9e80',.85)
 s+=r.ellipse(982,326,7,18,'#6fa787','#35624e',1.4,more='transform="rotate(-44 982 326)"')
 return s


_original_head=r.head
_original_torso=r.torso
FNUM=None
def head_for_batch(k,x=0,y=0,face=-1,laugh=False):
 if k=='X' and FNUM==39:
  p=r.path;e=r.ellipse
  z=p('M-32 66 C-57 69 -57 107 -39 125 Q-42 94 -25 86 Z','#5c5149')+p('M29 66 C51 69 54 110 38 123 Q40 96 23 86 Z','#5c5149')
  z+=p('M-34 29 Q-39 8 -14 0 Q14 -8 32 11 Q42 26 36 51 L31 80 Q16 104 -2 102 Q-27 99 -34 75 Z','#ffd0ad')
  z+=p('M-35 52 Q-49 27 -30 6 Q-8 -8 18 0 Q40 6 38 31 Q16 14 -2 20 Q-13 44 -35 52 Z','#5c5149')
  z+=e(-22,55,6,10,'#fff',w=1.2)+e(13,54,4.8,8.5,'#fff',w=1.2)+e(-24,56,3.1,6,'#433b35',w=.5)+e(11,55,2.6,5.5,'#433b35',w=.5)
  z+=p('M-10 61 l-7 8 9 3 M-13 85 Q-2 89 8 83','none',w=1.2)+e(-31,83,6,6,'#ce5f51',w=1)+e(30,82,5.5,5.5,'#ce5f51',w=1)
  return '<g transform="translate(%s %s)">'%(x,y)+z+'</g>'
 out=_original_head(k,x,y,face,laugh)
 if k=='X' and FNUM==54:return '<g transform="translate(%s %s) rotate(-3 0 95)">'%(3/1.55,2/1.55)+out+'</g>'
 return out
def torso_for_batch(k,bent=False):
 if k!='X':return _original_torso(k,bent)
 p=r.path;e=r.ellipse
 if FNUM==36:
  shirt='M-22 114 Q-40 128 -37 159 L-27 202 Q7 216 36 202 L34 147 Q27 121 17 116 Z';skirt='M-27 199 Q7 216 36 201 L69 330 Q10 355 -62 332 Z';collar='M-18 116 Q-7 143 1 127 Q18 145 22 118';fold='M10 216 Q25 270 30 330'
 elif FNUM==39:
  shirt='M-25 114 Q-43 127 -42 157 L-32 203 Q0 215 33 203 L42 151 Q40 124 23 114 Z';skirt='M-32 200 Q0 215 33 201 L67 330 Q0 353 -67 332 Z';collar='M-22 116 Q-12 139 -3 127 Q6 140 23 116';fold='M-12 216 Q-10 275 -9 340 M12 216 Q15 275 19 340'
 else:
  shirt='M-25 114 Q-41 128 -39 159 L-34 202 Q-6 216 29 203 L36 150 Q30 124 14 116 Z';skirt='M-34 199 Q-6 216 29 201 L60 330 Q-2 355 -71 332 Z';collar='M-24 116 Q-13 139 -7 129 Q4 140 20 118';fold='M-12 216 Q-23 275 -25 340 M10 216 Q14 275 17 338'
 out=p(skirt,r.C['dress'])+p(shirt,r.C['dress'])+p(collar,'none','#fff8e6',4)+p(fold,'none','#d5a63b',1)
 for x,y in [(-17,156),(17,178),(-12,245),(32,280),(-30,313)]:out+=e(x,y,3.5,3.5,'#f6f4e8','none',0)
 return '<g transform="translate(%s %s)">'%(3/1.55,2/1.55)+out+'</g>' if FNUM==54 else out
r.head=head_for_batch;r.torso=torso_for_batch


def figure_for_batch(d,labels=True):
 k=d['k'];near=d['near'];far='R' if near=='L' else 'L';p=r.path;e=r.ellipse
 s='<g transform="translate(%s %s) scale(%s)">'%(d['o'][0],d['o'][1],d['s'])
 if k=='G':
  hips=[(-16,260),(18,262)];knees=[(-23,364),(32,365)]
  ankles=[world_local(d['o'],d['s'],[1069.8,866.4]),world_local(d['o'],d['s'],[1173.8,883.4])]
 else:
  hips=[(-16,235),(18,238)] if FNUM==36 else [(-18,236),(17,239)] if FNUM==39 else [(-22,236),(12,239)]
  knees=[(-14,345),(24,347)] if FNUM==36 else [(-19,345),(24,341)] if FNUM==39 else [(-19,347),(21,339)]
  ankles=[(-18,450),(29,441)]
  if FNUM==54:hips=[(x+3/1.55,y+2/1.55) for x,y in hips];knees=[(x+1/1.55,y+1/1.55) for x,y in knees]
 for i in range(2):
  if k=='G':s+=p(f'M{hips[i][0]-20} {hips[i][1]} Q{knees[i][0]-24} {knees[i][1]} {ankles[i][0]-23} {ankles[i][1]} L{ankles[i][0]+26} {ankles[i][1]+3} Q{knees[i][0]+21} {knees[i][1]} {hips[i][0]+19} {hips[i][1]} Z','#929eaf' if i==0 else '#555f76')
  else:s+=r.tube(hips[i],knees[i],18,13,'#efc09f' if i==0 else r.C['near'])+r.tube(knees[i],ankles[i],13,8,'#efc09f' if i==0 else r.C['near'])
  ax,ay=ankles[i];shape='M-12 -1 Q-27 5 -43 10 Q-55 14 -49 20 L23 20 Q29 9 12 1 Z'
  if k=='X' and FNUM==36:shape='M12 -1 Q27 5 43 10 Q55 14 49 20 L-23 20 Q-29 9 -12 1 Z'
  if k=='X' and FNUM==39:shape='M-12 -1 Q-24 5 -24 16 Q0 22 24 16 Q24 5 12 -1 Z'
  s+='<g transform="translate(%s %s)">'%(ax,ay)+p(shape,'#333c47' if k=='G' else '#c56653')+'</g>'
 s+=r.arm(d[far],r.C['far'])+r.torso(k,False)+p('M-9 94 L-15 120 L8 133 L17 116 L12 95 Z',r.C['near'])+r.head(k,0,0,d['face'])+r.arm(d[near],r.C['near'])
 for side in ['R','L']:
  sh=d[side][0];s+=e(sh[0],sh[1],19,16,r.C['shirt'] if k=='G' else r.C['dress'],w=1.8)
 d['input_leg_landmarks']={'hips_world':[list(r.world(d,v)) for v in hips],'knees_world':[list(r.world(d,v)) for v in knees],'ankles_world':[list(r.world(d,v)) for v in ankles],'ankles_are_fixed_between_batch_states':True,'foot_turn':'profile_right -> foreshortened_front -> profile_left' if k=='X' else 'fixed original standing support'}
 return s+'</g>'
r.figure=figure_for_batch

states=[]
for f in [36,39,42,45,47,54]:
 FNUM=f
 F=P/f'F{f:03}';I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
 G=copy.deepcopy(r.FIGS['B_G']);G.update(o=[1110,42],s=1.83,near='L',face=-1)
 G['L']=[world_local(G['o'],G['s'],p) for p in [[1160,285],[1095,435],[984,343] if f in [36,39,42] else [984,333] if f==45 else [984,325]]]
 G['palms']['L']=world_local(G['o'],G['s'],[944,325] if f in [36,39,42] else [945,302])
 palmR=[970,465] if f==36 else [920,390] if f==39 else [880,345];wR=[1005,476] if f==36 else [954,409] if f==39 else [913,354];SR=[1067,285];ER=ik(SR,wR);G['R']=[world_local(G['o'],G['s'],q) for q in [SR,ER,wR]];G['palms']['R']=world_local(G['o'],G['s'],palmR)
 if f in [36,39]:G['open_hands']=['R']
 X=copy.deepcopy(r.FIGS['A_X'] if f in [36,39] else r.FIGS['B_X']);X.update(o=[608,190],s=1.55,face=1 if f in [36,39] else -1,near='R' if f in [36,39] else 'L')
 if f==39:
  rp,lp=[740,380],[765,430];X['R']=[(-8,121),(55,99),world_local(X['o'],X['s'],[706,380])];X['L']=[(14,122),(60,170),world_local(X['o'],X['s'],[731,430])]
 elif f==36:
  rp,lp=[820,365],[850,416];X['R']=[(16,120),(70,75),tuple(world_local(X['o'],X['s'],[786,365]))];X['L']=[(5,122),(60,173),tuple(world_local(X['o'],X['s'],[816,416]))]
 else:
  rp,lp=([479,435],[487,504]) if f==54 else ([476,432],[482,503]);wr=world_local(X['o'],X['s'],[rp[0]+34,rp[1]]);wl=world_local(X['o'],X['s'],[lp[0]+34,lp[1]]);X['R']=[(-16,122),(-40 if f<58 else -47,181),wr];X['L']=[(14,125),(5,193),wl]
 if f==54:
  for side in ['R','L']:
   X[side]=[(q[0]+3/1.55,q[1]+2/1.55) if j<2 else q for j,q in enumerate(X[side])]
 X['palms']={h:world_local(X['o'],X['s'],p) for h,p in [('R',rp),('L',lp)]}
 s=header+'<desc>INPUT ONLY: opaque full-volume reference, not a finished drawing. Frozen protocol anchors; no image model call.</desc>'
 figures=clean(r.figure(G,False))+clean(r.figure(X,False))
 # All four shafts are rigid. Crane angle is provisional pending the separate
 # official CAM20 review; no angle is propagated to accepted production frames.
 rods=''
 for role in ['C_N','C_B']:
  q=Caxes[role];p0=q['shaft_tip_master_px'];p1=[952,q['slope']*952+q['intercept']];rods+=r.line(p0,p1,'#675034',4.0)+r.line(p0,p1,'#b28b52',2.5)
 if f==39:th,ts=[650,350],[630,400]
 elif f==36:th,ts=[787,343],[774,388]
 elif f<58:th,ts=[245,375],[230,440]
 else:th,ts=[300,465],[300,425]
 # T_S is foreground at the future X; hand/endpoint identities never swap.
 for a,b in [(th,[rp[0]+16,rp[1]+(rp[1]-th[1])*16/(rp[0]-th[0])]),(ts,[lp[0]+16,lp[1]+(lp[1]-ts[1])*16/(lp[0]-ts[0])])]:rods+=r.line(a,b,'#675034',4.0)+r.line(a,b,'#b28b52',2.5)
 s+=rods+figures
 # Receiver and giver actual pad volumes are foreground to the rod. Each hand
 # has one thumb plus four individually curled finger contours, no symbol grips.
 s+=r.figure_hands(X)
 if f in [36,39]:s+=r.figure_hands(G)
 else:
  if f in [36,39,42]:s+=r.grip(*r.world(G,G['palms']['L']),sc=G['s']*.95,face=-1,jade=True,bundle=True)
  else:
   lh=adult_L_CN()
   if f==45:lh=lh.replace('M943 284 Q932 278 926 283 Q924 288 933 291 L944 296 Q949 292 943 284 Z','M949 307 Q942 315 934 326 Q930 331 933 334 Q938 338 944 331 L952 319 Q955 311 949 307 Z')
   s+=lh
  s+=adult_R_CB()
 s+=end;(I/'01_unique_opaque_complete_target.svg').write_text(s)
 lengths={}
 for name,d in [('G',G),('X',X)]:
  for side in ['R','L']:
   sh,el,wr=d[side];a,b=math.dist(sh,el),math.dist(el,wr);maxa,maxb=(100,90) if name=='G' else (90,80);assert a<=maxa+1e-5 and b<=maxb+1e-5,(f,name,side,a,b);lengths[name+'.'+side]={'world_chain':[list(r.world(d,p)) for p in [sh,el,wr]],'projected_upper_in_own_H':a/100,'projected_forearm_in_own_H':b/100,'construction_limits_in_own_H':[maxa/100,maxb/100]}
 contract={'frame_anchor':f,'status':'INPUT_PENDING_ASTRA_SHORT_REVIEW','not_new_exposure_schedule':True,'image_model_calls':0,'generation_authorized':False,'source':'Frozen S20 protocol B04/B05/B06 and approvedCB strip036/042/047; firstactivecross sampling058','ownership':{'T_H':['X.R'],'T_S':['X.L'],'C_B':['G.L'] if f in [36,39] else ['G.L','G.R'] if f in [42,45] else ['G.R'],'C_N':['G.L']},'hand_chain_construction':lengths,'full_support_to_pelvis_chest_head':{'G':G.get('input_leg_landmarks'),'X':X.get('input_leg_landmarks'),'no_whole_old_body_as_reference':True},'child_face':X['face'],'child_near_arm':X['near'],'G_R_CB_thumb_index_opposition_world':[875,321.5] if f not in [36,39] else None,'G_L_CN_opposition_world':[929,317.54],'pending_crane_axis_gate':'445d2921 officialCAM20 candidate; angle provisional in these INPUTS ONLY','fixed_cues_seconds':{'active_entangle':[2.4,4.6],'flip_complete':5.5,'CAMG_cut':6.0},'no_endpoint_swap':True,'T_S_front_T_H_back_at_crossing':f==58,'not_production_character_drawing':True}
 (F/'contact_contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n');states.append(contract)
(P/'batch_status.json').write_text(json.dumps({'states':[s['frame_anchor'] for s in states],'status':'INPUT_PENDING_ASTRA_SHORT_REVIEW','new_image_calls':0,'new_raws':0,'independent_production_drawings':0,'frame_holds_assigned':False,'sound_story_table_modified':False},ensure_ascii=False,indent=2)+'\n')
print('6 complete B04/B05 input SVGs; support/pelvis/chest/head linked; no image calls')
