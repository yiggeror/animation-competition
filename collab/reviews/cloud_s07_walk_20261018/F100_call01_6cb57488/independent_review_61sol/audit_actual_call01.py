from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,distance_transform_edt
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;P=R.parent;ROOT=P.parent;F=ROOT/'F100_103_106_closing_batch_20261019/F100_input';OLD=ROOT/'F100_next_gate_20261019';raw=Image.open(P/'originals/F100_call01_RAW.png').convert('RGBA');a=np.array(raw);A=Image.open(F/'inputs_1024x1536/A_F100_FULL_WAIST_NOT_CALLED.png').convert('RGBA');inv=45/64;size=(1960,1080);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',15)
# ONE whole inverse only. No image fit, body fit, hand shift, lamp shift or candidate.
registered=raw.resize((720,1080),Image.Resampling.LANCZOS);registered.save(R/'qa/F100_RAW_whole_inverse_720x1080_DIAGNOSTIC_ONLY.png')
prop_native=Image.open(OLD/'reference/existing_table_lamp_NATIVE_same_registration.png').convert('RGBA');fixedprop=prop_native.crop((1240,0,1960,1080)).resize((1024,1536),Image.Resampling.LANCZOS);pa=np.array(fixedprop);ll,n=label(a[:,:,3]>=128);person=ll==ll[450,650];newlamp=ll==ll[900,700]
pm=Image.fromarray(np.where(person[:,:,None],a,0).astype('uint8'));overlay=Image.alpha_composite(fixedprop,pm)
# Mark actual source overlap in a separate diagnostic overlay, never edited candidate.
clash=person&(pa[:,:,3]>=128);ov=np.array(overlay);ov[clash]=[255,55,80,255];overlay=Image.fromarray(ov)
for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 sheet=Image.new('RGB',(1440,1110),(235,240,245));d=ImageDraw.Draw(sheet)
 for j,(name,z)in enumerate([('FROZEN A (exact6cb input)',A),('ACTUAL RAW (same whole inverse)',raw)]):
  bg=Image.new('RGBA',raw.size,col);bg.alpha_composite(z);sheet.paste(bg.resize((720,1080)).convert('RGB'),(j*720,30));d.text((j*720+10,8),name,font=font,fill='#354e65')
 sheet.save(R/f'qa/frozen_vs_actual_whole_{tone}.png')
 connections=Image.new('RGB',(1560,620),(235,240,245));d=ImageDraw.Draw(connections)
 for j,(name,z,crop)in enumerate([('RAW complete neararm/whole fingers',raw,(300,420,755,620)),('RAW waist / missing farhand',raw,(190,670,590,1010)),('FIXED true lamp + actual hand; RED=overlap',overlay,(560,400,855,605))]):
  bg=Image.new('RGBA',raw.size,col);bg.alpha_composite(z);im=bg.crop(crop);im.thumbnail((500,565));connections.paste(im.convert('RGB'),(520*j+8,45));d.text((520*j+8,10),name,font=font,fill='#354e65')
 connections.save(R/f'qa/arm_waist_fixed_bail_connections_{tone}.png')
 bg=Image.new('RGBA',raw.size,col);bg.alpha_composite(overlay);bg.crop((560,400,855,605)).resize((1180,820),Image.Resampling.NEAREST).save(R/f'qa/actual_hand_against_FIXED_original_bail_{tone}_4x.png')
# Material gap: keep thresholds explicit. Alpha1 includes weak-matting bridges.
gaps={}
for th in [1,16,128]:
 la,_=label(a[:,:,3]>=th);pc=la[450,650];lc=la[900,700];same=pc==lc
 rec={'person_component':int(pc),'lamp_component':int(lc),'joined_through_alpha_threshold':bool(same)}
 if not same:
  pm=la==pc;pr=la==lc;dt,inds=distance_transform_edt(~pr,return_indices=True);iy,ix=np.unravel_index(np.argmin(np.where(pm,dt,np.inf)),dt.shape);rec.update({'min_pixel_center_distance_raw':float(dt[iy,ix]),'min_pixel_center_distance_native':float(dt[iy,ix]*inv),'actual_hand_point_raw':[int(ix),int(iy)],'actual_lamp_point_raw':[int(inds[1,iy,ix]),int(inds[0,iy,ix])]})
 gaps[str(th)]=rec
fixedoverlap={}
for th in [16,128]:
 la,_=label(a[:,:,3]>=th);pc=la[450,650];ov=(la==pc)&(pa[:,:,3]>=th);yy,xx=np.where(ov);fixedoverlap[str(th)]={'overlap_tool_pixels':len(xx),'bbox_tool_inclusive':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],'bbox_native_inclusive':[(float(xx.min())*inv)+1240,float(yy.min())*inv,(float(xx.max())*inv)+1240,float(yy.max())*inv],'source_original_lamp_file':str((OLD/'reference/existing_table_lamp_NATIVE_same_registration.png').relative_to(ROOT)),'source_original_lamp_sha256':sha(OLD/'reference/existing_table_lamp_NATIVE_same_registration.png')}
# Existing far hand material in frozen placement. Threshold only classifies source
# skin evidence; not a new extracted hand or a production matte.
far=np.array(Image.open(F/'layers/F100_far_complete_arm_jade_whole_RIGID16.png').convert('RGBA'));guard=np.array(Image.open(F/'masks/HARD_far_visible_whole_arm_jade.png'))>0;yy,xx=np.indices(guard.shape);warm=(far[:,:,0]>180)&(far[:,:,1]>105)&(far[:,:,2]>60)&(far[:,:,0]>far[:,:,1]+25)&guard&(yy>550)
actual_native=Image.new('RGBA',size);actual_native.alpha_composite(registered,(1240,0));aa=np.array(actual_native);stayswarm=(aa[:,:,0]>180)&(aa[:,:,1]>105)&(aa[:,:,2]>60)&(aa[:,:,0]>aa[:,:,1]+25)&(aa[:,:,3]>=128);y,x=np.where(warm)
farrec={'frozen_actual_visible_far_skin_sample_pixels':int(warm.sum()),'source_native_bbox_inclusive':[int(x.min()),int(y.min()),int(x.max()),int(y.max())],'same_positions_actual_raw_warm_visible_pixels':int((warm&stayswarm).sum()),'interpretation':'Frozen far LEFT palm/fingers under blouse are replaced by native navy/empty material, not preserved as requested. Full original fararm cannot be claimed present in raw.'}
# Shoes: no independent fitting. Compare source-fixed whole-foot alpha bottoms
# to the raw person sole; not enough to prove complete shoe topology unchanged.
feet=[]
for nm in ['F100_near_whole_shoe_FIXED.png','F100_far_whole_shoe_FIXED.png']:
 src=Image.open(F/'layers'/nm).convert('RGBA');padded=Image.new('RGBA',size);padded.alpha_composite(src);tool=padded.crop((1240,0,1960,1080)).resize((1024,1536),Image.Resampling.LANCZOS);ta=np.array(tool);y,x=np.where(ta[:,:,3]>=128);feet.append({'source':nm,'sha256':sha(F/'layers'/nm),'tool_alpha128_bbox_inclusive':[int(x.min()),int(y.min()),int(x.max()),int(y.max())],'native_true_source_sole':1022})
# Manual readings are declared, not silently optimized into a different fit.
readings={'fixed_lamp_bail_top_tool_approx':[717,476],'actual_lamp_bail_top_tool_approx':[729,506],'reading_uncertainty_tool_px':3,'actual_lamp_vs_fixed_approx_delta_tool':[12,30],'actual_lamp_vs_fixed_approx_delta_native':[12*inv,30*inv],'interpretation':'Whole inverse is held fixed. New lamp moved relative to true original; no independent lamp or hand registration allowed.'}
rec={'status':'HOLD_FIXED_PROP_CONTACT_AND_MISSING_FAR_PALM','raw_sha256':sha(P/'originals/F100_call01_RAW.png'),'raw_size':list(raw.size),'only_inverse':{'scale':inv,'offset':[1240,0],'native_crop':[1240,0,1960,1080]},'actual_viewed':['originals/F100_call01_RAW.png','frozen6cb A','qa/frozen_vs_actual_whole_gray.png','qa/frozen_vs_actual_whole_dark.png','qa/arm_waist_fixed_bail_connections_gray.png','qa/arm_waist_fixed_bail_connections_dark.png','qa/actual_hand_against_FIXED_original_bail_gray_4x.png','qa/actual_hand_against_FIXED_original_bail_dark_4x.png'],'visible_raw_facts':['Near RIGHT sleeve→upperarm→elbow→forearm→wrist→whole open hand is visually continuous; no old narrow wrist patch seam visible.','New broad waist/hip cloth is continuous, without visible old hanging-hand cutout or narrow bridge. This does not approve new cloth/palette against mother.','At alpha16/128 raw hand and RAW new bail have air, but the raw lamp shifted downward. Restoring actual frozen lamp creates finger/bail material overlap.','Original far LEFT palm/fingers under blouse are visibly omitted in raw. Small skin sliver at upper side is not a complete far chain.'],'alpha_counts':{'zero':int((a[:,:,3]==0).sum()),'one_through15':int(((a[:,:,3]>0)&(a[:,:,3]<16)).sum()),'16through127':int(((a[:,:,3]>=16)&(a[:,:,3]<128)).sum()),'maximum':int(a[:,:,3].max())},'correction_of_initial_preview_claim':'Initial preview-only statement of full opaque haze background is withdrawn. Most haze is hiddenRGB at alpha0/weak AA. Only correctly alpha-composited diagnostic gray/dark images are evidence; original raw unchanged.','actual_hand_to_actual_new_lamp_gap':gaps,'actual_hand_to_fixed_original_lamp':fixedoverlap,'far_left_palm_source_check':farrec,'source_shoe_anchors':feet,'manual_lamp_registration_readings':readings,'adoption_feasibility':'Neararm+waist are coherent source material, but NOT legal final fixed-prop combination: actual hand overlaps original bail at fixed common registration. Do not independently move hand/lamp, shrink grip, bridge wrist, or reattach far hand/shoes to claim whole chain passed. Only a clearly marked diagnostic is produced; no adopted candidate.','limits':['Finger count/topology partly occluded; visible open-hand silhouette is not an automatic five-finger pass.','Rawbody/shoes/lamp dimensions and palette are not production mother approval. Preserve original layers only after real registered joins pass.','103/106 four-input gate/calls not authorized here.'],'imagegen_calls':0,'git_operations':0}
(R/'geometry/F100_actual_measurements.json').write_text(json.dumps({'gaps':gaps,'fixed_source_overlap':fixedoverlap,'far_source_check':farrec,'manual_readings':readings},ensure_ascii=False,indent=2)+'\n');(R/'qa/61sol_F100_actual_review_HOLD.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'far':farrec,'gaps':gaps,'overlap':fixedoverlap},ensure_ascii=False,indent=2))
