from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,math,json,sys
from scipy.ndimage import label
D=Path(__file__).parent;P=D.parent;R=P.parent;N=P/'G063_G069_first_clamp_inputs'
CONFIG={'G081':{'raw_anchors':[[440.,1225.],[628.,1224.],[882.,207.]],'raw_mouth':[881.,101.]}}
CONFIG['G084']={'raw_anchors':[[421.,1217.],[614.,1213.],[844.,198.]],'raw_mouth':[926.,114.]}
CONFIG['G087']={'raw_anchors':[[373.,1228.],[566.,1224.],[817.,143.]],'raw_mouth':[939.,80.]}
for key in sys.argv[1:]:
 c=CONFIG[key];raw=Image.open(D/f'{key}_complete_body_call01_original.png').convert('RGBA');p=np.array(c['raw_anchors']);q=np.array([[442.,1021.],[558.,1016.],[704.,319.]])
 a=p-p.mean(0);b=q-q.mean(0);u,z,vt=np.linalg.svd(a.T@b);rot=vt.T@u.T;assert np.linalg.det(rot)>0;s=z.sum()/(a*a).sum();M=s*rot;t=q.mean(0)-M@p.mean(0);iv=np.linalg.inv(M);tt=-iv@t
 reg=raw.transform((1254*3,1254*3),Image.Transform.AFFINE,tuple(np.c_[iv/3,tt].ravel()),Image.Resampling.BICUBIC).resize((1254,1254),Image.Resampling.LANCZOS)
 ar=np.array(reg);lab,n=label(ar[:,:,3]>0);ct=np.bincount(lab.ravel());ct[0]=0;ar[lab!=ct.argmax()]=0;reg=Image.fromarray(ar);reg.save(D/f'{key}_whole_original_SINGLE_similarity_DIAGNOSTIC.png')
 sheet=Image.open(R/'grandma_fall_inputs/G027_upper_contact_repair/G027_complete_sheet_whole_registered.png').convert('RGBA');first=Image.open(N/'G066_TRUE_disconnected_complete_closed_peg_fold_SOURCE.png').convert('RGBA');stool=Image.open(R/'grandma_throw_inputs/G000_locked_complete_rigid_work_stool.png').convert('RGBA')
 scene=Image.new('RGBA',(1254,1254),'#f1f2ed');ImageDraw.Draw(scene).line((200,277,1140,277),fill='#777b75');scene.alpha_composite(sheet);scene.alpha_composite(first);scene.alpha_composite(stool);scene.alpha_composite(reg);scene.convert('RGB').save(D/f'{key}_whole_single_registered_scene_DIAGNOSTIC.jpg',quality=94)
 target=Image.open(D/f'{key}_ONLY_complete_native_body_volume_target.png').convert('RGB');board=Image.new('RGB',(1500,1050),'#f1f2ed');font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
 for i,(im,caption)in enumerate([(target,f'{key} complete target'),(scene.convert('RGB'),f'{key} raw ONE similarity / raw shoes')]):
  board.paste(im.resize((700,700)),(i*750+25,32));ImageDraw.Draw(board).text((i*750+25,8),caption,font=font,fill='#344d57');board.paste(im.crop((585,200,770,410)).resize((265,300)),(i*750+5,740));board.paste(im.crop((360,940,660,1060)).resize((450,180)),(i*750+285,800))
 board.save(D/f'{key}_TARGET_vs_SINGLE_registered_actual_REVIEW.jpg',quality=93)
 scene.crop((570,200,780,440)).resize((630,720)).convert('RGB').save(D/f'{key}_SINGLE_registered_B_peg_3x_REVIEW.jpg',quality=94);scene.crop((360,930,660,1060)).resize((900,390)).convert('RGB').save(D/f'{key}_SINGLE_registered_two_supports_3x_REVIEW.jpg',quality=94)
 residual=(M@p.T).T+t-q;rec={'status':'ONE_COMPLETE_NATIVE_BODY_SIMILARITY_PHYSICAL_DIAGNOSTIC','scale':float(s),'rotation_deg':math.degrees(math.atan2(rot[1,0],rot[0,0])),'translation':t.tolist(),'physical_anchors':['far_sole_center','near_sole_center','B_thumb_contact'],'raw_anchors':p.tolist(),'target_anchors':q.tolist(),'residuals_xy':residual.tolist(),'actual_registered_peg_mouth':(M@c['raw_mouth']+t).tolist(),'separate_part_transforms':False,'raw_shoes_still_shown_in_diagnostic':True,'cleanup':'Disconnected alpha specks only; largest complete connected native body retained.'};(D/f'{key}_whole_raw_SINGLE_registration_DIAGNOSTIC.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec,indent=2))
