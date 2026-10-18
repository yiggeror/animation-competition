#!/usr/bin/env python3
"""Unadopted whole-native-arm source-pixel trials. One rigid transform per complete arm, no drawing."""
from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,binary_fill_holes,binary_closing,label
R=Path(__file__).resolve().parent;D=R/'whole_arm_trial';D.mkdir(exist_ok=True)
pre=Image.open(R/'reference/F042_hand_torch_contact_PREPOSITION_NOT_ART.png').convert('RGBA');a=np.array(pre);size=pre.size
raw=Image.open(R/'originals/F042_call01_raw.png').convert('RGBA');n=np.array(raw);assert raw.size==size
prev=Image.open(R.parent/'whole_far_puff_zero_call/candidate/F037_whole_native_far_puff_PENDING.png').convert('RGBA');old=np.array(prev)
def poly(points):
 z=Image.new('L',size);ImageDraw.Draw(z).polygon(points,fill=255);return np.array(z)>0
roi=poly([(724,619),(837,675),(1024,590),(1048,654),(979,718),(853,773),(821,776),(734,731),(679,690),(679,673),(699,643)])
rgb=n[:,:,:3].astype(int);skin=(rgb[:,:,0]>155)&(rgb[:,:,0]>rgb[:,:,1]+15)&(rgb[:,:,1]>rgb[:,:,2]+12)&(rgb[:,:,2]>70)&(n[:,:,3]>20)
seed=skin&roi
lab,num=label(seed);identity=lab[720,840];assert identity>0
skinbody=lab==identity
mask=binary_dilation(binary_fill_holes(binary_closing(skinbody,iterations=2)),iterations=2)&roi&(n[:,:,3]>0)
# Remove actual cloth/ruffle linework from the source arm before one rigid transform.
yy,xx=np.indices(mask.shape);cuff_roi=(xx>=635)&(xx<=788)&(yy>=603)&(yy<=720)
raw_yellow=(rgb[:,:,0]>180)&(rgb[:,:,1]>130)&(rgb[:,:,2]<100)&(n[:,:,3]>20)
raw_cuff=binary_dilation(binary_fill_holes(binary_closing(raw_yellow&cuff_roi,iterations=1)),iterations=2)&cuff_roi
mask &= ~raw_cuff
Image.fromarray(mask.astype(np.uint8)*255).save(D/'native_complete_near_arm_source_mask.png')
z=n.copy();z[~mask]=0;layer=Image.fromarray(z);layer.save(D/'native_complete_near_arm_source.png')
# Visible generated arm continues outside chosen source ROI into its generated
# gripping hand. This diagnostic includes no generated hand in the adoption.
raw_arm_all=binary_dilation(skinbody,iterations=4)
edit=np.array(Image.open(R/'masks/near_arm_and_vacated_WHITE_EDIT.png'))>0
hardnames=['whole_rigid_hand_torch','head_neck_collar','near_cuff_root','stable_receiver_palm_lower_forearm']
hards={name:np.array(Image.open(R/f'masks/{name}.png'))>0 for name in hardnames}
# Wrist extraction boundary is not a physical transparent moat. Protect actual original material, not the1px dilated empty strip.
original_rigid=np.array(Image.open(R.parent/'reference/F031_rigid_whole_torch_and_grip.png').convert('RGBA'));material=np.zeros_like(original_rigid[:,:,3]);material[59:]=original_rigid[:-59,:,3];hards['whole_rigid_hand_torch']=material>0
oldrgb=old[:,:,:3].astype(int);oldskin=(oldrgb[:,:,0]>155)&(oldrgb[:,:,0]>oldrgb[:,:,1]+15)&(oldrgb[:,:,1]>oldrgb[:,:,2]+12)&(oldrgb[:,:,2]>70)
oldyellow=(oldrgb[:,:,0]>180)&(oldrgb[:,:,1]>130)&(oldrgb[:,:,2]<100)&(old[:,:,3]>20)
complete_cuff=binary_dilation(binary_fill_holes(binary_closing(oldyellow&cuff_roi,iterations=1)),iterations=2)&cuff_roi&~oldskin&(old[:,:,3]>0)
hards['near_cuff_root']=complete_cuff
hards['complete_source_near_cuff_visible']=complete_cuff
Image.fromarray(complete_cuff.astype(np.uint8)*255).save(D/'source_complete_near_cuff_material_guard.png')
hard=np.logical_or.reduce(list(hards.values()))
far=np.array(Image.open(R/'masks/far_puff_complete_source_material.png'))>0
# Fixed-coordinate native garment/clear-air donor, never use its displaced
# hand, flashlight or raw near arm. Fill only the previously authorized domain.
hsv=np.array(raw.convert('RGB').convert('HSV'));yellow=(rgb[:,:,0]>180)&(rgb[:,:,1]>140)&(rgb[:,:,2]<100)&(n[:,:,3]>20)
cloth=binary_dilation(binary_fill_holes(binary_closing(yellow,iterations=2)),iterations=1)&(n[:,:,3]>0)
clear=n[:,:,3]<128
oldarm=np.array(Image.open(R.parent/'independent_recompose/arm_raw_dy30_mask.png'))>0
oldroi_im=Image.open(R.parent/'masks/rigid_whole_torch_and_grip_source.png').convert('L');oldroi_canvas=Image.new('L',size);oldroi_canvas.paste(oldroi_im,(0,-32));oldroi=np.array(oldroi_canvas)>0
# Native garment is adopted only where the old source arm/hand actually vacates;
# do not import its altered long far sleeve into previous transparent background.
restore_domain=binary_dilation(oldarm,iterations=4)|oldroi
fixed_take=edit&restore_domain&(cloth|clear)&~raw_arm_all
base=a.copy();base[fixed_take]=n[fixed_take]
# Candidate missing-underlay check compares source old near arm with true new arm.
oldarm=np.array(Image.open(R.parent/'independent_recompose/arm_raw_dy30_mask.png'))>0
sourceC=np.array([704.5,652.5]);sourceW=np.array([1032.5,628.5]);targetW=np.array([1030.,598.])
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
sheet=Image.new('RGB',(1800,810),(239,243,246));dr=ImageDraw.Draw(sheet);rows=[]
for i,angle in enumerate([-4.,-6.,-8.]):
 rad=math.radians(angle);rot=np.array([[math.cos(rad),-math.sin(rad)],[math.sin(rad),math.cos(rad)]]);delta=np.array([1052.,617.])-rot@np.array([1048.,654.]);inverse=rot.T;it=-inverse@delta
 moved=layer.transform(size,Image.Transform.AFFINE,(inverse[0,0],inverse[0,1],it[0],inverse[1,0],inverse[1,1],it[1]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));ma=np.array(moved);mm=ma[:,:,3]>0
 c=base.copy();c[far&~binary_dilation(mm,iterations=1)]=a[far&~binary_dilation(mm,iterations=1)]
 comp=Image.alpha_composite(Image.fromarray(c),moved);c=np.array(comp);c[hard]=a[hard]
 path=D/f'F042_whole_arm_{int(-angle):02d}deg_UNPASSED.png';Image.fromarray(c).save(path)
 # Any old skin not overwritten by valid fixed donor/new arm is flagged, never assumed repaired.
 residual=oldarm&edit&~fixed_take&~mm&~hard
 Image.fromarray(residual.astype(np.uint8)*255).save(D/f'old_arm_residual_{int(-angle):02d}deg.png')
 bg=Image.new('RGBA',size,(212,222,230,255));bg.alpha_composite(Image.fromarray(c));panel=bg.crop((640,520,1240,850)).resize((600,330));sheet.paste(panel.convert('RGB'),(i*600,35));dr.text((i*600+5,5),f'全臂{angle:.0f}度 / 同一刚体 / 未通过',font=font,fill='#26343e')
 # Root and wrist pixels at3x show the actual complete attachment cross sections.
 for j,box in enumerate([(665,610,775,725),(980,540,1090,655)]):
  q=bg.crop(box).resize((330,345),Image.Resampling.NEAREST);sheet.paste(q.convert('RGB'),(i*600+(0 if j==0 else 270),420))
 rows.append({'angle_degrees':angle,'whole_arm_translation':delta.tolist(),'one_scale':1,'new_root_center':(rot@sourceC+delta).tolist(),'target_wrist_proxy':targetW.tolist(),'source_wrist_proxy':sourceW.tolist(),'old_arm_residual_pixels':int(residual.sum()),'path':path.name,'status':'UNPASSED_SOURCE_PIXEL_TRIAL_NOT_DRAWING_GATE'})
sheet.save(D/'three_whole_arm_trials_actual_attachments.png')
(D/'trial_checks.json').write_text(json.dumps({'status':'WHOLE_NATIVE_ARM_RIGID_TRIALS_NOT_ADOPTED','raw_size':list(raw.size),'source_arm_pixels':int(mask.sum()),'source_root_and_wrist_are_manual_proxy_not_measurement':True,'fixed_coordinate_native_cloth_or_air_take':int(fixed_take.sum()),'trials':rows,'no_new_requests':True},ensure_ascii=False,indent=2)+'\n');print(json.dumps(rows,ensure_ascii=False))
