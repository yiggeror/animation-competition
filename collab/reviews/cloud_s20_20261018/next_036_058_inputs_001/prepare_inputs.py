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

states=[]
for f in [36,42,47,58]:
 F=P/f'F{f:03}';I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
 G=copy.deepcopy(r.FIGS['B_G']);G.update(o=[1110,42],s=1.83,near='L',face=-1)
 G['L']=[world_local(G['o'],G['s'],p) for p in [[1160,285],[1095,435],[984,343] if f<47 else [984,325]]]
 G['palms']['L']=world_local(G['o'],G['s'],[944,325] if f<47 else [945,302])
 palmR=[970,465] if f==36 else [880,345];wR=[1005,476] if f==36 else [913,354];SR=[1067,285];ER=ik(SR,wR);G['R']=[world_local(G['o'],G['s'],q) for q in [SR,ER,wR]];G['palms']['R']=world_local(G['o'],G['s'],palmR)
 if f==36:G['open_hands']=['R']
 X=copy.deepcopy(r.FIGS['A_X'] if f==36 else r.FIGS['B_X']);X.update(o=[608,190],s=1.55,face=1 if f==36 else -1,near='R' if f==36 else 'L')
 if f==36:
  rp,lp=[820,365],[850,416];X['R']=[(16,120),(70,75),tuple(world_local(X['o'],X['s'],[786,365]))];X['L']=[(5,122),(60,173),tuple(world_local(X['o'],X['s'],[816,416]))]
 else:
  rp,lp=([476,432],[482,503]) if f<58 else ([450,448],[487,489]);wr=world_local(X['o'],X['s'],[rp[0]+34,rp[1]]);wl=world_local(X['o'],X['s'],[lp[0]+34,lp[1]]);X['R']=[(-16,122),(-40 if f<58 else -47,181),wr];X['L']=[(14,125),(5,193),wl]
 X['palms']={h:world_local(X['o'],X['s'],p) for h,p in [('R',rp),('L',lp)]}
 s=header+'<desc>INPUT ONLY: opaque full-volume reference, not a finished drawing. Frozen protocol anchors; no image model call.</desc>'
 figures=clean(r.figure(G,False))+clean(r.figure(X,False))
 # All four shafts are rigid. Crane angle is provisional pending the separate
 # official CAM20 review; no angle is propagated to accepted production frames.
 rods=''
 for role in ['C_N','C_B']:
  q=Caxes[role];p0=q['shaft_tip_master_px'];p1=[952,q['slope']*952+q['intercept']];rods+=r.line(p0,p1,'#675034',4.0)+r.line(p0,p1,'#b28b52',2.5)
 if f==36:th,ts=[787,343],[774,388]
 elif f<58:th,ts=[245,375],[230,440]
 else:th,ts=[300,465],[300,425]
 # T_S is foreground at the future X; hand/endpoint identities never swap.
 for a,b in [(th,[rp[0]+16,rp[1]+(rp[1]-th[1])*16/(rp[0]-th[0])]),(ts,[lp[0]+16,lp[1]+(lp[1]-ts[1])*16/(lp[0]-ts[0])])]:rods+=r.line(a,b,'#675034',4.0)+r.line(a,b,'#b28b52',2.5)
 s+=rods+figures
 # Receiver and giver actual pad volumes are foreground to the rod. Each hand
 # has one thumb plus four individually curled finger contours, no symbol grips.
 s+=r.figure_hands(X)
 if f==36:s+=r.figure_hands(G)
 else:
  if f==42:s+=r.grip(*r.world(G,G['palms']['L']),sc=G['s']*.95,face=-1,jade=True,bundle=True)
  else:s+=adult_L_CN()
  s+=adult_R_CB()
 s+=end;(I/'01_unique_opaque_complete_target.svg').write_text(s)
 lengths={}
 for name,d in [('G',G),('X',X)]:
  for side in ['R','L']:
   sh,el,wr=d[side];a,b=math.dist(sh,el),math.dist(el,wr);maxa,maxb=(100,90) if name=='G' else (90,80);assert a<=maxa+1e-5 and b<=maxb+1e-5,(f,name,side,a,b);lengths[name+'.'+side]={'world_chain':[list(r.world(d,p)) for p in [sh,el,wr]],'projected_upper_in_own_H':a/100,'projected_forearm_in_own_H':b/100,'construction_limits_in_own_H':[maxa/100,maxb/100]}
 contract={'frame_anchor':f,'status':'INPUT_PENDING_ASTRA_SHORT_REVIEW','not_new_exposure_schedule':True,'image_model_calls':0,'generation_authorized':False,'source':'Frozen S20 protocol B04/B05/B06 and approvedCB strip036/042/047; firstactivecross sampling058','ownership':{'T_H':['X.R'],'T_S':['X.L'],'C_B':['G.L'] if f==36 else ['G.L','G.R'] if f==42 else ['G.R'],'C_N':['G.L']},'hand_chain_construction':lengths,'child_face':X['face'],'child_near_arm':X['near'],'G_R_CB_thumb_index_opposition_world':[875,321.5] if f!=36 else None,'G_L_CN_opposition_world':[929,317.54],'pending_crane_axis_gate':'445d2921 officialCAM20 candidate; angle provisional in these INPUTS ONLY','fixed_cues_seconds':{'active_entangle':[2.4,4.6],'flip_complete':5.5,'CAMG_cut':6.0},'no_endpoint_swap':True,'T_S_front_T_H_back_at_crossing':f==58,'not_production_character_drawing':True}
 (F/'contact_contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n');states.append(contract)
(P/'batch_status.json').write_text(json.dumps({'states':[s['frame_anchor'] for s in states],'status':'INPUT_PENDING_ASTRA_SHORT_REVIEW','new_image_calls':0,'new_raws':0,'independent_production_drawings':0,'frame_holds_assigned':False,'sound_story_table_modified':False},ensure_ascii=False,indent=2)+'\n')
print('4 review-only complete opaque SVG targets; projected bones within construction limits; no new exposure schedule or model calls')
