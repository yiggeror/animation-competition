#!/usr/bin/env python3
"""Prepare a uniqueF000 static input. Never invokes an image model."""
from pathlib import Path
import copy,json,math,hashlib
import sys
sys.dont_write_bytecode=True
import build_references as r
D=Path(__file__).resolve().parents[1];HERE=D/'F000';OUT=HERE/'inputs';OUT.mkdir(exist_ok=True,parents=True)
g=copy.deepcopy(r.FIGS['A_G']);g['bundle_hands']=['L','R'];g['open_hands']=[]
x=copy.deepcopy(r.FIGS['A_X']);x.update(R=[(16,120),(35,187),(60,220)],L=[(5,122),(-10,200),(25,232)],palms={'R':(80,226),'L':(45,237)},open_hands=['R','L'])
# Explicitly different fromF020: both child hands remain below/off all four shafts.
assert x['R']!=r.FIGS['A_X']['R'] and x['L']!=r.FIGS['A_X']['L']
gr=r.world(g,g['palms']['R']);gl=r.world(g,g['palms']['L'])
axes=[{'id':'TH','start':(760,520),'contact':(gr[0]-14,gr[1]-12),'owner':'G.R'}, {'id':'TS','start':(730,585),'contact':(gr[0]-10,gr[1]+2),'owner':'G.R'}, {'id':'CN','start':(760,205),'contact':(gl[0]-14,gl[1]-12),'owner':'G.L'}, {'id':'CB','start':(680,290),'contact':(gl[0]-10,gl[1]+2),'owner':'G.L'}]
body=r.figure(g,labels=False)+r.figure(x,labels=False)
for a in axes:
 a['end']=r.shaft_through(a['start'],a['contact'],14);body+=r.rod(a['start'],a['end'],a['id'])
body+=r.figure_hands(g)+r.figure_hands(x)
svg='<svg xmlns="http://www.w3.org/2000/svg" width="1672" height="941" viewBox="0 0 1672 941"><style>line[stroke-dasharray],ellipse[stroke="#71818b"]{display:none}</style><desc>F000 ONLY. GrandmaL holds2crane rods, grandmaR holds2turtle rods. Both child hands open, not touching rods. Static construction input, no generated character output.</desc><rect width="1672" height="941" fill="#f5f5f3"/><g transform="translate(200 -80) scale(.94)">'+body+'</g></svg>'
(OUT/'F000_fullbody_four_rods.svg').write_text(svg)
meta={'frame':0,'time_seconds':0,'status':'PREPARED_NOT_SUBMITTED','type':'unique full-body four-rod static construction input, not a production image','target_size':[1672,941],'pose_source':'independentF000 joint/palm definition inbuild_F000_input.py','F020_used_as_input':False,'grandma_pose':g,'child_pose':x,'rod_axes':axes,'held_rod_count':4,'holders':{'TH':['G.R'],'TS':['G.R'],'CB':['G.L'],'CN':['G.L']},'child_contact_count':0,'child_hands_open':['X.R','X.L'],'annotation_transform':{'scale':.94,'translate':[200,-80]},'rod_segment_note':'These are straight holding/registration segments. Puppet-side world projection is not claimed as verified; actual scene mechanism stays unchanged.','image_generation_calls':0}
(HERE/'F000_start_state.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print('UniqueF000 SVG prepared: granny4rods, child2open hands, noF020 input.')
