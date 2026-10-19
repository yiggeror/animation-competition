from pathlib import Path
import json,sys,math
import numpy as np
P=Path(__file__).resolve().parent;PACK=P.parent;OLD=PACK/'handoff_008_020_032_generation_002';f=int(sys.argv[1]);assert f in [22,24,27,30];F=P/f'F{f:03}';F.mkdir(exist_ok=True)
wp={22:([984,441],[945,448]),24:([1008,463],[968,480]),27:([1007,468],[970,483]),30:([1011,477],[976,486])};w,palm=wp[f]
S=np.array([1067,285],float);W=np.array(w,float);a,b=150,92;delta=W-S;d=np.linalg.norm(delta);t=(a*a-b*b+d*d)/(2*d);h=math.sqrt(a*a-t*t);u=delta/d;n=np.array([-u[1],u[0]]);E=max([S+t*u+h*n,S+t*u-h*n],key=lambda p:p[0]);chain=[S.tolist(),E.tolist(),w]
g={'G_R_chain':chain}
src=(OLD/'prepare_F032.py').read_text();src=src.replace("P=Path(__file__).resolve().parent;PACK=P.parent;F=P/'F032';I=F/'inputs';ART=F/'art'","P=OLD;F=NEWF;I=F/'inputs';ART=F/'art'");src=src.replace("g=json.loads((PACK/'handoff_008_020_032_reference_001/batch_geometry_and_requests.json').read_text())['frames'][2]['state']","g=NEWG")
src=src.replace("yy,xx=np.indices(M.shape);M&=xx>=885","yy,xx=np.indices(M.shape);M|=(xx>=895)&(xx<1003)&(yy>=390)&(yy<540);M&=xx>=885")
src=src.replace("w=np.array([1012,480],float);palm=np.array([978,487],float)","w=np.array(NEWW,float);palm=np.array(NEWPALM,float)")
if f==22:
 start=src.index("hand=f'<g transform=\"{mat}\">'");end=src.index("svg=f'<svg",start)
 hand='''hand=f'<g transform="{mat}">'
hand+=path('M0 -10 C10 -17 24 -19 36 -12 Q45 -7 42 7 Q39 19 27 19 L9 13 L0 10 Z',SKIN,sw=1.2)
for D in ['M27 -15 Q38 -20 43 -14 Q47 -10 42 -5 L31 -5 Q25 -7 27 -15 Z','M29 -7 Q42 -10 46 -4 Q48 1 42 4 L31 4 Q26 1 29 -7 Z','M29 2 Q41 1 44 6 Q46 11 39 13 L29 11 Q25 8 29 2 Z','M27 10 Q37 10 40 15 Q41 19 34 20 L26 17 Q23 14 27 10 Z']:
 hand+=path(D,SKIN,sw=1.0)
# Thumb opens first, four fingers retain their curled support around both ends.
hand+=path('M9 -7 Q9 -19 19 -31 Q22 -35 26 -32 Q31 -29 26 -23 L20 -11 Q17 -5 13 -3 Z',SKIN,sw=1.2)
hand+=path('M11 4 Q20 7 27 3','none','#d0a285',.8)
hand+='</g>'
'''
 src=src[:start]+hand+src[end:]
ns={'__file__':str(OLD/'prepare_F032.py'),'OLD':OLD,'PACK':PACK,'NEWF':F,'NEWG':g,'NEWW':w,'NEWPALM':palm};exec(compile(src,'isolated_release_reference','exec'),ns)
info=json.loads((F/'source_and_geometry.json').read_text());info.update({'frame':f,'G_R_release_chain':chain,'G_R_palm':palm,'stage':'thumb_first_four_fingers_still_curled' if f==22 else 'all_fingers_leave_then_whole_forearm_withdraws','input_only_not_drawing':True});(F/'source_and_geometry.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n');print('Prepared release SVG input only',f)
