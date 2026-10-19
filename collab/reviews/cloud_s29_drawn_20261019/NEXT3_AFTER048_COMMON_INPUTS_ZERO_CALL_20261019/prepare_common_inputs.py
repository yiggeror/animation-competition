from pathlib import Path
from PIL import Image,ImageDraw
import shutil,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent
LOCK=B/'F036_COMPLETE_OLD_HAND_HOLE_RAW_RESTORE_ZERO_CALL_20261019'
G=B/'F042_F048_NATIVE_call01_each_from_bd309770_20261019/single_group_reintegration_TRIAL/geometry/ONE_GROUP_PER_STATE_SOURCE_MATRIX_CHECKS.json'
P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019/geometry/COMMON_ACTUAL030_COORDINATES_AND_TRUE_PART_REFERENCE.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources=[('01_LOCKED048_COMPLETE_START_RGBA.png',LOCK/'F048/CURRENT_FINGER_ALPHA_OVER_COMPLETE_CLOTH_RGBA.png'),('02_ONLY_LOCKED_COMPLETE_CLOTH_MASTER_RGBA.png',LOCK/'ONE036_COMPLETE_OLD_HOLE_CLOTH_MASTER_RGBA.png'),('04_ACTUAL_CAMERA_LIGHT_LOCKED048_CANVAS.png',LOCK/'keys/S29_F048_CANVAS.png')]
index=[]
for name,p in sources:
 shutil.copyfile(p,R/name);assert (R/name).read_bytes()==p.read_bytes();index.append({'input':name,'source_commit':'baf6d568','source_path':str(p),'SHA256':sha(p),'bytes':p.stat().st_size})
geo=json.loads(P.read_text());arm=next(v for v in json.loads(G.read_text())['reports']if v['frame']==48)
c1=geo['near_palm_true_neck3_point_common030'];c2=arm['mapped_anchors'][2]
contacts={'status':'LOCKED048_START_ONLY_NOT_NEXT3_TARGETS','coordinate_canvas':[1024,1536],'C1':{'xy':c1,'physical_role':'near bare right hand supports actual crane neck3, not an invented second cloth pinch','true_part':'neck3','original_group_point':geo['near_palm_true_neck3_point_original'],'true_original_props_to_common_M':geo['single_similarity_original_props_to_actual030']},'C2':{'xy':c2,'physical_role':'far left bangle hand pinches the raised cotton lip','same_native_hand_point':arm['manual_source_cuff_endpoints_and_pinch'][2],'whole_arm_source_M_UNCHANGED':arm['single_similarity_complete_arm_hand_and_cloth'],'measurement_note':'native visible contact readpoint has manual +/-3px uncertainty; exact matrix number is not a measured3D bone claim'},'one_clean_cloth_master_SHA256':sha(R/'02_ONLY_LOCKED_COMPLETE_CLOTH_MASTER_RGBA.png'),'layer_order':'current finger foreground alpha -> continuous cotton lip -> actual feather intersection T -> lower cotton/lap; retain original puppets/four rods','old_hand_hole_reclip_forbidden':True,'future_new_contact_targets':'must come from missing original frozen next3 table; none invented'}
(R/'LOCKED048_TRUE_TWO_CONTACTS.json').write_text(json.dumps(contacts,indent=2)+'\n')
im=Image.open(R/'01_LOCKED048_COMPLETE_START_RGBA.png').convert('RGBA');bg=Image.new('RGBA',im.size,(236,239,242,255));bg.alpha_composite(im)
bg.convert('RGB').save(R/'LOCKED048_COMPLETE_START_ON_GRAY.png')
annot=bg.convert('RGB');d=ImageDraw.Draw(annot)
for xy,col,label in [(c1,(210,45,40),'C1 NEAR HAND / TRUE NECK3'),(c2,(220,125,15),'C2 FAR LEFT HAND / SAME COTTON')]:
 x,y=xy;d.ellipse((x-8,y-8,x+8,y+8),outline=col,width=2);d.line([(x-12,y),(x+12,y)],fill=col,width=1);d.line([(x,y-12),(x,y+12)],fill=col,width=1)
 tx,ty=(410,775)if xy==c1 else(520,640);d.text((tx,ty),label,fill=col)
annot.crop((100,400,870,850)).save(R/'03_LOCKED048_COMPLETE_ARMS_TRUE_CONTACTS_TECHNICAL.png')
sheet=Image.new('RGB',(880,270),(236,239,242));draw=ImageDraw.Draw(sheet)
for i,f in enumerate([36,48]):
 a=Image.open(LOCK/f'F{f:03d}/CURRENT_FINGER_ALPHA_OVER_COMPLETE_CLOTH_RGBA.png').convert('RGBA');g=Image.new('RGBA',a.size,(236,239,242,255));g.alpha_composite(a);draw.text((i*440+8,8),f'LOCKED{f:03d} ONLY | NO NEXT-STATE TARGET',fill='black')
 for xy,col in [(c1,(210,45,40)),(next(v for v in json.loads(G.read_text())['reports']if v['frame']==48)['mapped_anchors'][2]if f==48 else[725.78751656,663.66135947],(220,125,15))]:
  x,y=xy;draw2=ImageDraw.Draw(g);draw2.ellipse((x-5,y-5,x+5,y+5),outline=col,width=2)
 sheet.paste(g.crop((440,620,860,850)).convert('RGB'),(i*440,30))
sheet.save(R/'LOCKED036_TO048_TWO_CONTACTS_REFERENCE_1TO1.png')
index.insert(2,{'input':'03_LOCKED048_COMPLETE_ARMS_TRUE_CONTACTS_TECHNICAL.png','derived_from':'01_LOCKED048_COMPLETE_START_RGBA.png','role':'annotations of two real locked contacts only; not a future pose or new drawing','SHA256':sha(R/'03_LOCKED048_COMPLETE_ARMS_TRUE_CONTACTS_TECHNICAL.png')})
(R/'SOURCE_INDEX.json').write_text(json.dumps({'generation_calls':0,'inputs':index,'actual_geometry_sources':[{'path':str(P),'SHA256':sha(P)},{'path':str(G),'SHA256':sha(G)}]},indent=2)+'\n')
(R/'EXPOSURE_AND_ACTION_COUNT_PENDING_TABLE.json').write_text(json.dumps({'status':'MISSING_ORIGINAL_FROZEN_NEXT3_TABLE__NO_FRAME_OR_ACTION_INVENTED','verified_locked_states':[{'frame':36,'exposure_proven_in_prior13f':[36,41],'new_action_count':0,'reason':'repair of already existing036'},{'frame':42,'exposure_proven_in_prior13f':[42,47],'new_action_count':1},{'frame':48,'exposure_proven_in_prior13f':[48,48],'new_action_count':1,'end_frame_not_proven':True}],'locked_new_action_count':2,'next_three':[{'slot':i,'frozen_start_frame':None,'frozen_end_frame':None,'action':None,'C1_target':None,'C2_target':None,'reason':'await original frozen table commit:path or exact text'}for i in [1,2,3]],'new_targets_or_generation_requests':0,'do_not_infer':['054/060/066','048 final exposure','20261017 old six-state table','old code human action']},indent=2)+'\n')
(R/'READ_ONLY_FROZEN_TABLE_LOOKUP.json').write_text(json.dumps({'own_source_HEAD':'baf6d568','latest_shared_checked_readonly':'8157d9f279dad5b97bd219b9b210d37eb9c9e557','search_scope':['current S29 review directory text/JSON/CSV/TSV','latest shared Git tree','collab/partner.md relevant S29 decisions','existing cloud helper retained original messages'],'finding':'only finite024/030/036 and042/048 groups; no current048+ frozen frame/exposure/action table; latest original task says288f/about36states but is not a time sheet','old_tables_rejected':'20261017 six-state/AB8.1-8.42/F240 history explicitly superseded','personal_context_lookup':'unavailable for this conversation','clarification_requested':'original frozen next3 table commit:path or exact text'},indent=2)+'\n')
print(json.dumps({'status':'COMMON_INPUTS_READY_PENDING_FROZEN_NEXT3_TABLE','generation_calls':0,'master_SHA256':contacts['one_clean_cloth_master_SHA256'],'C1':c1,'C2':c2,'inputs':len(sources)+1},indent=2))
