#!/usr/bin/env python3
"""F100 source-rigid lean proposals + complete NOT_ART approach arm; NO IMAGEGEN."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,distance_transform_edt,label
import numpy as np,json,math,shutil,hashlib
R=Path(__file__).resolve().parent;PREV=R.parents[1]/'F100_next_gate_20261019';S=PREV/'sources';size=(1960,1080);crop=(1240,0,1960,1080);s=.36410361842105265;off=np.array([627.0254537171638,402.7604324894813]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for d in ['layers','masks','reference_native','inputs_1024x1536','qa','geometry','requests']:(R/d).mkdir(exist_ok=True)
g=json.loads((S/'F095_actual_preparation_metadata.json').read_text());H=np.array(g['softH_near']);Ns=np.array(g['target_sleeve_roots095']['near']);Fs=np.array(g['target_sleeve_roots095']['far']);body=Image.open(S/'F095_body_head_blouse.png').convert('RGBA');far=Image.open(S/'F095_far_complete_arm_jade_hand.png').convert('RGBA');oldnear=Image.open(S/'F095_near_complete_arm.png').convert('RGBA');pants=Image.open(S/'F095_locked_actual_whole_trousers_ORIGINAL_COLOR.png').convert('RGBA');nearfoot=Image.open(S/'F095_near_shoe_ankle_COLLECTED_LANDED.png').convert('RGBA');farfoot=Image.open(S/'F095_far_shoe_ankle_SUPPORT_FIXED.png').convert('RGBA');prop=Image.open(PREV/'reference/existing_table_lamp_NATIVE_same_registration.png').convert('RGBA');pa=np.array(prop)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16);small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',13)
# Astra approved full waist replacement: original095 archive untouched.
# Derived guide removes ALL upper pants y<690, including old hidden-hand edge.
op=np.array(pants);disp=op.copy();disp[:690]=0;pants_display=Image.fromarray(disp)
oldcutwide=np.zeros((1080,1960),bool);oldcutwide[:690,:1672]=op[:690,:,3]>0
Image.fromarray(oldcutwide.astype('uint8')*255).save(R/'masks/REMOVED_old_upper_pants_ALL_yLT690.png')
# Broad continuous tapered waist/hips, behind leaned shirt, ending at both thighs.
# This is NOT_ART construction volume, never true navy or a lampward flap.
waist=Image.new('RGBA',size);wd=ImageDraw.Draw(waist)
wd.polygon([(1404,474),(1601,523),(1570,567),(1538,610),(1516,651),(1509,690),(1407,690),(1399,643),(1389,585),(1380,530)],fill='#bcc8da',outline='#637892',width=2)
waistmask=np.array(waist)[:,:,3]>0;waist.save(R/'layers/F100_complete_unknown_waist_VOLUME_NOT_ART.png')

def rigid(z,M,t):
 iv=M.T;it=-iv@t;return z.transform(size,Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),Image.Resampling.BICUBIC,fillcolor=0)
def rot(deg):
 r=math.radians(deg);return np.array([[math.cos(r),-math.sin(r)],[math.sin(r),math.cos(r)]])
def pad(z):
 o=Image.new('RGBA',size);o.alpha_composite(z);return o
# Keep the whole actual palm/fingers/wrist entrance source together. A temporary
# entire-R90 trial touched the true bail; final SOFTguide R-60 is recorded instead.
na=np.array(oldnear);yy,xx=np.indices(na.shape[:2]);sourcehand=(na[:,:,3]>0)&(yy>=535);hand=Image.fromarray(np.where(sourcehand[:,:,None],na,0).astype('uint8'));anchor=np.array([1471.,606.]);Fing=(np.array([1255.,515.])-off)/s;handM=rot(-60);handt=Fing-handM@anchor;handnew=rigid(hand,handM,handt);ha=np.array(handnew);W=handM@np.array([1440.,535.])+handt;handnew.save(R/'layers/F100_whole_near_palm_fingers_R60_SOFT_GUIDE_NOT_FROZEN.png');Image.fromarray(sourcehand.astype('uint8')*255).save(R/'masks/SOURCE095_whole_near_hand_wrist_entrance_SOFT_ONLY.png')
# New arm lengths are projected TECHNICAL proxies only, within visibly uncertain
# original shoulder/elbow/wrist landmarks. No source pixels are lengthened.
U,V=95.,110.
def ik(Ss,W):
 v=W-Ss;d=np.linalg.norm(v)
 if d>U+V:return None
 e=v/d;q=(U*U-V*V+d*d)/(2*d);n=np.array([-e[1],e[0]]);return Ss+e*q+n*math.sqrt(max(0,U*U-q*q))
def arm(ps,rs):
 z=Image.new('RGBA',size);d=ImageDraw.Draw(z)
 for p,q,r1,r2 in zip(ps[:-1],ps[1:],rs[:-1],rs[1:]):
  v=q-p;n=np.array([-v[1],v[0]])/np.linalg.norm(v);d.polygon([tuple(p+n*r1),tuple(q+n*r2),tuple(q-n*r2),tuple(p-n*r1)],fill='#a6cee0',outline='#3d7695',width=2)
 for p,r in zip(ps[1:-1],rs[1:-1]):x,y=p;d.ellipse((x-r,y-r,x+r,y+r),fill='#a6cee0',outline='#3d7695',width=2)
 return z
records=[];outputs={}
for deg in [8.021409131831524,16.]:
 M=rot(deg);t=H-M@H;b=rigid(body,M,t);f=rigid(far,M,t);nr=M@Ns+t;fr=M@Fs+t;E=ik(nr,W);valid=E is not None
 # Unreachable within these arbitrary2Dproxy lengths means only that this
 # particular proxy proposal cannot connect; not a physical3D reach conclusion.
 if E is None:E=(nr+W)/2+np.array([0,35])
 tech=arm([nr,E,W],[22,19,13]);base=Image.new('RGBA',size)
 for z in [pad(farfoot),waist,pad(pants_display),f,b,pad(nearfoot),prop,tech,handnew]:base.alpha_composite(z)
 for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
  bg=Image.new('RGBA',size,col);bg.alpha_composite(base);d=ImageDraw.Draw(bg);d.text((1250,14),f'F100 FULLGROUP LEAN {deg:.2f}deg PROPOSAL / arm NOT_ART',font=font,fill='#2f6178');d.text((1250,37),'New full waist / lowerpants+shoes fixed / no contact',font=small,fill='#2f6178');d.text((1250,58),'PROXY LINK '+('FEASIBLE2D / NOT bones'if valid else'EXCEEDS chosen2Dproxy / NOT3Dproof'),font=small,fill='#b75c42');bg.crop(crop).save(R/f'qa/F100_lean_{round(deg):02d}_whole_source_group_{tone}_NOT_ART.png')
 records.append({'lean_degrees_PROPOSAL':deg,'body_head_chest_same_group_scale':1,'M':M.tolist(),'t':t.tolist(),'same_far_whole_arm_affine':True,'source_pivot_hidden_proxy_not_anatomy':H.tolist(),'near_root':nr.tolist(),'far_root':fr.tolist(),'near_wrist_soft_source_entry':W.tolist(),'near_elbow_technical':E.tolist(),'technical_projected_lengths':[U,V],'actual_proxy_result_lengths':[float(np.linalg.norm(E-nr)),float(np.linalg.norm(W-E))],'chosen_proxy_link_feasible':valid,'NOT_measured_bones':True})
 if deg==16:outputs={'A':base,'body':b,'far':f,'tech':tech,'near_root':nr,'E':E,'W':W}
outputs['body'].save(R/'layers/F100_body_head_chest_whole_RIGID16.png');outputs['far'].save(R/'layers/F100_far_complete_arm_jade_whole_RIGID16.png');shutil.copyfile(S/'F095_locked_actual_whole_trousers_ORIGINAL_COLOR.png',R/'layers/F095_original_whole_trousers_FIXED_ARCHIVE.png');shutil.copyfile(S/'F095_near_shoe_ankle_COLLECTED_LANDED.png',R/'layers/F100_near_whole_shoe_FIXED.png');shutil.copyfile(S/'F095_far_shoe_ankle_SUPPORT_FIXED.png',R/'layers/F100_far_whole_shoe_FIXED.png');Image.fromarray(disp).save(R/'layers/F100_pants_DISPLAY_only_old_cut_edge_released.png');A=outputs['A'];tech=outputs['tech'];b=outputs['body'];f=outputs['far'];nt=np.array(tech)[:,:,3]>0;hm=ha[:,:,3]>0;ba=np.array(b);fa=np.array(f);pp=np.array(pad(pants_display));nf=np.array(pad(nearfoot));ff=np.array(pad(farfoot));old=np.array(pad(oldnear))[:,:,3]>0
# Full approach arm + old/new void + sleeve/waist seam domains. Actual source
# head/body behind a new foreground arm is not allowed to cut that foreground.
window=Image.new('L',size);wd=ImageDraw.Draw(window);r=outputs['near_root'];wd.ellipse((r[0]-30,r[1]-28,r[0]+34,r[1]+28),fill=255);wd.rectangle((1380,505,1650,635),fill=255);seams=np.array(window)>0
waist_envelope=np.zeros((1080,1960),bool);waist_envelope[470:691,1345:1631]=True;foreground=nt|hm;bodyguard=(ba[:,:,3]>0)&~waist_envelope&~seams&~binary_dilation(foreground,iterations=3);farguard=(fa[:,:,3]>0)&~binary_dilation(foreground,iterations=3)&~(ba[:,:,3]>0);waist_envelope=np.zeros((1080,1960),bool);waist_envelope[470:691,1345:1631]=True;pantguard=(pp[:,:,3]>0)&~(ba[:,:,3]>0)&~(fa[:,:,3]>0);nearfootguard=nf[:,:,3]>0;farfootguard=(ff[:,:,3]>0)&~(nf[:,:,3]>0)&~(pp[:,:,3]>0);propguard=pa[:,:,3]>0;hard=bodyguard|farguard|pantguard|nearfootguard|farfootguard|propguard;white=(binary_dilation(foreground|old,iterations=16)|seams|waist_envelope|waistmask|oldcutwide)&~hard
for k,z in [('WHITE_complete_near_arm_openhand_old_new_void_sleeve_waist',white),('HARD_actual_head_body_group_except_seams_and_frontarm',bodyguard),('HARD_far_visible_whole_arm_jade',farguard),('HARD_visible_original095_pants_material',pantguard),('HARD_near_original_whole_foot',nearfootguard),('HARD_far_VISIBLE_NOT_HIDDEN_foot',farfootguard),('HARD_actual_existing_lamp_material_NO_ROI',propguard)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{k}.png')
C=A.copy();d=ImageDraw.Draw(C);ps=[outputs['near_root'],outputs['E'],W];d.line([tuple(p)for p in ps],fill='#3a628c',width=2)
for x,y in ps:d.ellipse((x-5,y-5,x+5,y+5),outline='#3a628c',width=2)
d.text((1550,235),'ONLY100 / OPEN / NO CONTACT',font=small,fill='#a44c69');D=Image.new('RGBA',(720,1080),(234,240,244,255));d=ImageDraw.Draw(D);d.text((10,12),'D REAL IDENTITY/MATERIAL ONLY / NOT OLD ARM POSE',font=small,fill='#334d60');D.alpha_composite(body.crop((1320,0,1640,270)),(10,50));D.alpha_composite(oldnear.crop((1420,535,1490,610)),(450,90));d.text((370,180),'whole-palm/finger source only',font=small,fill='#334d60');D.alpha_composite(pants.crop((1430,700,1490,780)),(40,420));d.text((115,440),'locked095 ORIGINAL NAVY / no recolor',font=small,fill='#334d60');D.alpha_composite(body.crop((1430,280,1490,350)),(40,550));d.text((115,570),'actual blouse/white flowers',font=small,fill='#334d60')
D.alpha_composite(prop.crop((1630,315,1860,455)),(370,720));d.text((370,875),'actual source CUBIC bail, native1:1',font=small,fill='#334d60');B=Image.fromarray(white.astype('uint8')*255);images={'A':A.crop(crop),'B':B.crop(crop),'C':C.crop(crop),'D':D}
for k,im in images.items():
 im.save(R/f'reference_native/{k}_F100_FULL_WAIST_720x1080.png');im.resize((1024,1536),Image.Resampling.NEAREST if k=='B'else Image.Resampling.LANCZOS).save(R/f'inputs_1024x1536/{k}_F100_FULL_WAIST_NOT_CALLED.png')
for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 sheet=Image.new('RGB',(2880,1110),(235,240,245));dd=ImageDraw.Draw(sheet)
 for j,(k,z)in enumerate(images.items()):
  bg=Image.new('RGBA',(720,1080),col);bg.alpha_composite(z.convert('RGBA'));sheet.paste(bg.convert('RGB'),(720*j,30));dd.text((720*j+10,8),k+' F100 LEAN16 FULL WAIST / SHORT GATE',fill='black')
 sheet.save(R/f'qa/F100_four_inputs_{tone}_PROPOSAL.png');bg=Image.new('RGBA',size,col);bg.alpha_composite(prop);bg.alpha_composite(handnew);bg.crop((1580,250,1850,460)).resize((1080,840),Image.Resampling.NEAREST).save(R/f'qa/F100_actual_full_hand_to_actual_lamp_gap_{tone}_4x.png')
gaps={}
for threshold in [1,16,128,240]:
 pm=pa[:,:,3]>=threshold;hh=ha[:,:,3]>=threshold;dt=distance_transform_edt(~pm);gaps[str(threshold)]={'min_gap_native':float(dt[hh].min()),'overlap_pixels':int((hh&pm).sum())}
lab,ncomp=label(white);guarddiff=int((white&hard).sum());rec={'status':'F100_COMPLETE_WAIST_REPLACEMENT_ASTRA_AUTHORIZED_SHORT_GATE','F100_hold':[100,102],'calls':0,'mother095_6layer_replay_changes':0,'original095_source_archive_and_both_shoes_unchanged':True,'derived_pants_yLT690_entirely_removed':True,'waist_envelope_native':[1345,470,1630,690],'original095_pants_source_file_unchanged':True,'old_upper_pants_removed_pixels_yLT690':int(oldcutwide.sum()),'unknown_exposed_waist_RGB_drawn_as_real_cloth':False,'old_hand_negative_boundary_in_guide':False,'old_lampward_flap_removed':True,'complete_waist_NOT_ART_only':True,'source_feet_visibility_note':'Original layer files unchanged. New blouse/front-source overlap may naturally occlude rear materials; hidden far alpha is never guard.','body_lean_alternatives':records,'chosen_for_current_four_input_PROPOSAL_only':16,'source_near_whole_hand_guide':{'source_mask':'y>=535 of complete original neararm alpha>0, full palm/fingers plus wrist entrance, manual cut must be redrawn','M':handM.tolist(),'t':handt.tolist(),'rotation':-60,'scale':1,'source_lower_finger_anchor':[1471,606],'target_legacy_intent_used_as_soft_anchor':Fing.tolist(),'all_hand_pixels_one_rigid_transform':True,'old_Rminus90_trial_not_used':'touched true bail38alpha128px; discarded before input, finalRminus60 whole-hand has air.'},'real_whole_hand_to_REAL_lamp_gap_by_alpha':gaps,'near_arm_is_NOT_ART_full_new_volume':True,'proxy_length_limit':'95/110native are explicitly projected construction proposals, not actual measured bones or old64/58world lengths. No source limb pixels elongated. Root/Astra must review full neararm anatomy/proportions; this does not prove3Dreach.','cropped_native':crop,'crop_size':[720,1080],'whole_forward_scale':64/45,'whole_inverse_scale':45/64,'whole_inverse_offset':[1240,0],'tool_size':[1024,1536],'guard_white_intersection':guarddiff,'actual_prop_no_material_changes':True,'new_far_or_near_physical_contact_accepted':False,'100_only_no103or106_input':True,'limits':['Lean16 is a pending proposal; source body/head/chest and full fararm follow the same rigid transform, no head-only nod. Lean8comparison exceeds chosen2Darm proxies, not a claim of actual3D impossibility.','095 original trousers source archive unchanged. Derived upperpants yLT690 is wholly removed; new waist domain is adopted as one new drawn region and old upperpants are never restored. Lowerpants yGE690 and whole shoes stay source-fixed.','The actual raw source hand is a SOFT guide; full nearforearm/wrist/hand WHITE prevents hard-wrist patch constraints. Future generated hand must preserve open approach with all visible fingers clear of real bail.']}

# Bounds and source-core checks for the exact proposed request geometry.
a=np.array(A);ay,ax=np.where(a[:,:,3]>0);wy,wx=np.where(white);rec['active_rgba_bbox_halfopen']=[int(ax.min()),int(ay.min()),int(ax.max()+1),int(ay.max()+1)];rec['white_bbox_halfopen']=[int(wx.min()),int(wy.min()),int(wx.max()+1),int(wy.max()+1)];rec['crop_margins_L_T_R_B']=[int(ax.min()-crop[0]),int(ay.min()-crop[1]),int(crop[2]-ax.max()-1),int(crop[3]-ay.max()-1)];rec['active_material_outside_crop']=int(((a[:,:,3]>0)&((np.indices(a.shape[:2])[1]<crop[0])|(np.indices(a.shape[:2])[1]>=crop[2])|(np.indices(a.shape[:2])[0]<crop[1])|(np.indices(a.shape[:2])[0]>=crop[3]))).sum());rec['original095_pants_kept_lower_yGE690_RGBA_changes']=int(np.any(disp[690:]!=op[690:],axis=2).sum());rec['newhand_tech_outside_white_or_fixed_guard']=int(((nt|hm)&~white&~hard).sum());rec['guard_alpha0_in_actual_input']=int((hard&(a[:,:,3]==0)).sum());rec['near_whole_shoe_source_file_byte_identical']=(S/'F095_near_shoe_ankle_COLLECTED_LANDED.png').read_bytes()==(R/'layers/F100_near_whole_shoe_FIXED.png').read_bytes();rec['far_whole_shoe_source_file_byte_identical']=(S/'F095_far_shoe_ankle_SUPPORT_FIXED.png').read_bytes()==(R/'layers/F100_far_whole_shoe_FIXED.png').read_bytes();rec['D_reference_crop_pastes']={'identity':{'source':'F095_body_head_blouse','crop':[1320,0,1640,270],'paste':[10,50],'s':1},'hand_material_not_pose':{'source':'F095_near_complete_arm','crop':[1420,535,1490,610],'paste':[450,90],'s':1},'navy':{'source':'locked095wholetrousers','crop':[1430,700,1490,780],'paste':[40,420],'s':1},'blouse':{'source':'F095_body_head_blouse','crop':[1430,280,1490,350],'paste':[40,550],'s':1},'bail':{'source':'existing_lamp_NATIVE','crop':[1630,315,1860,455],'paste':[370,720],'s':1}};assert rec['active_material_outside_crop']==0 and rec['newhand_tech_outside_white_or_fixed_guard']==0
(R/'geometry/F100_full_input_proposal_checks.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'gap':gaps,'white':int(white.sum()),'chosen':records[-1]},indent=2))
