#!/usr/bin/env python3
"""Reversible source-pixel compositing of imagegen edits; never paints anatomy.
Only returns actual generated pixels inside explicit edit scopes and locks accepted pixels outside.
"""
from PIL import Image,ImageDraw,ImageFilter,ImageFont
from pathlib import Path
import hashlib,json,numpy as np,sys
P=Path(__file__).resolve().parents[1]
ROOT=P.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,a):p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
def comp(im,c=(245,245,245,255)):
 a=Image.new('RGBA',im.size,c);a.alpha_composite(im);return a.convert('RGB')

def d02():
 basepath=ROOT/'d01_first_candidate/candidates/S13_d01_uniform_registered_rgba.png'
 rawpath=P/'originals/S13_d02_call_002_raw.png'
 base=Image.open(basepath).convert('RGBA');raw=Image.open(rawpath).convert('RGBA')
 assert base.size==raw.size==(1024,1536)
 mask=Image.new('L',base.size,0);d=ImageDraw.Draw(mask)
 # Both complete eye interiors and their existing lid outlines, excluding eyebrows/nose.
 d.ellipse((577,582,707,725),fill=255)
 d.ellipse((764,568,835,704),fill=255)
 mask=mask.filter(ImageFilter.GaussianBlur(2))
 mask.save(P/'masks/d02_eye_edit_scope.png')
 final=Image.composite(raw,base,mask)
 # Eye edits cannot change character silhouette or alpha anywhere.
 final.putalpha(base.getchannel('A'))
 output=P/'approved_local/F018_d02_eyes_up.png';final.save(output)
 a=np.array(base);b=np.array(final);m=np.array(mask)
 report={'pose':'d02','status':'author_self_accepted_pending_Astra_segment_review',
 'base':str(basepath.relative_to(ROOT)),'base_sha256':sha(basepath),'raw':str(rawpath.relative_to(P)),
 'raw_sha256':sha(rawpath),'output':str(output.relative_to(P)),'output_sha256':sha(output),
 'method':'Actual imagegen RGB through two explicit eye-scope masks; accepted mother elsewhere; original mother alpha everywhere.',
 'mask':'masks/d02_eye_edit_scope.png','mask_sha256':sha(P/'masks/d02_eye_edit_scope.png'),
 'generated_pixels_not_drawn_by_code':True,'raw_registration':'identity, no geometric warp',
 'outside_scope_RGBA_changed_pixels':int(np.any(a!=b,axis=2)[m==0].sum()),
 'alpha_changed_pixels':int((a[:,:,3]!=b[:,:,3]).sum()),
 'self_review':'真实眼内视线由右下抬到右上，两眼一致；头/耳/发/颈/领/嘴不动；眼白、睫毛及皮肤接缝实看。'}
 assert report['outside_scope_RGBA_changed_pixels']==0 and report['alpha_changed_pixels']==0
 put(P/'qa/d02_validation.json',report)
 s=Image.new('RGB',(1500,970),'#f5f3ed');draw=ImageDraw.Draw(s)
 f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',24)
 for x,im,t in [(20,base,'d01 已锁母态 / 眼向右下'),(770,final,'d02 自审候选 / 只抬眼到右上')]:
  crop=comp(im).crop((535,530,855,800)).resize((640,540));s.paste(crop,(x,80));draw.text((x,22),t,font=f,fill='#23333e')
 draw.text((25,690),'眼区外 RGBA 0 改；整张 alpha 0 改。新眼睛来自真实生成，不用代码画眼珠。',font=f,fill='#23333e')
 draw.text((25,760),'原始工具整图另保全；仅接回两眼区，未从原始整图的衣纹/头发漂移继续扩链。',font=f,fill='#23333e')
 s.save(P/'qa/d01_d02_actual_eyes.jpg',quality=96)
 comp(final).save(P/'qa/d02_final_on_light.jpg',quality=95)
 print(json.dumps(report,ensure_ascii=False,indent=2))

def d03():
 basepath=P/'approved_local/F018_d02_eyes_up.png';rawpath=P/'originals/S13_d03_call_003_raw.png'
 base=Image.open(basepath).convert('RGBA');raw=Image.open(rawpath).convert('RGBA')
 assert base.size==raw.size==(1024,1536)
 mask=Image.new('L',base.size,0);d=ImageDraw.Draw(mask)
 # Whole head, pigtails, real neck AND its collar junction stay one native generated unit.
 # Lock lower chest; forcing the old collar border over the new neck produced double lines.
 d.rectangle((0,0,1023,1110),fill=255)
 # Keep the entire native collar/upper-shoulder unit. Color-based protection of old
 # yellow/white edges clipped its new silhouette and was rejected on actual inspection.
 mask=mask.filter(ImageFilter.GaussianBlur(1.5))
 mask.save(P/'masks/d03_whole_head_neck_scope.png')
 final=Image.composite(raw,base,mask);output=P/'approved_local/F024_d03_whole_head_right.png';final.save(output)
 a=np.array(base);bb=np.array(final);m=np.array(mask)
 report={'pose':'d03','status':'author_self_accepted_pending_Astra_segment_review',
 'base':str(basepath.relative_to(P)),'base_sha256':sha(basepath),'raw':str(rawpath.relative_to(P)),
 'raw_sha256':sha(rawpath),'output':str(output.relative_to(P)),'output_sha256':sha(output),
 'method':'Actual imagegen complete head/hair/ears/neck/collar/upper-shoulder pixels as one native unit; accepted lower chest retained; no local geometric deformation.',
 'mask':'masks/d03_whole_head_neck_scope.png','mask_sha256':sha(P/'masks/d03_whole_head_neck_scope.png'),
 'raw_registration':'identity, no geometric warp','outside_scope_RGBA_changed_pixels':int(np.any(a!=bb,axis=2)[m==0].sum()),
 'lower_body_RGBA_changed_pixels':int(np.any(a[1120:]!=bb[1120:],axis=2).sum()),
 'head_alpha_changed_pixels':int((a[:1070,:,3]!=bb[:1070,:,3]).sum()),
 'self_review':'整头轮廓、近耳、发根、花与两尾、远眼短缩及鼻颌一起右转；保留原生颈领连续面，清醒上视、小开口；白领接口有真实新像素，不能称白领0改。'}
 assert report['outside_scope_RGBA_changed_pixels']==0 and report['lower_body_RGBA_changed_pixels']==0
 put(P/'qa/d03_validation.json',report)
 f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',25)
 sheet=Image.new('RGB',(1536,1110),'#f5f3ed');draw=ImageDraw.Draw(sheet)
 for x,im,t in [(15,base,'d02 眼先到 / 原头向'),(783,final,'d03 整头右转 / 同尺度')]:
  crop=comp(im).crop((90,185,920,1085));crop.thumbnail((740,900));sheet.paste(crop,(x,85));draw.text((x,20),t,font=f,fill='#23333e')
 draw.text((25,955),'头发外轮廓、耳花、发根、鼻颌和颈领一起重画；下胸衣料0改。',font=f,fill='#23333e')
 draw.text((25,1010),'头向为视觉增转；不以像素差声称精确7°。下胸仍继承唯一母态。',font=f,fill='#23333e')
 sheet.save(P/'qa/d02_d03_same_scale_whole_head.jpg',quality=96)
 comp(final).save(P/'qa/d03_final_on_light.jpg',quality=96)
 onion=Image.blend(comp(base),comp(final),.5);onion.crop((100,180,920,1090)).save(P/'qa/d02_d03_onion.jpg',quality=96)
 print(json.dumps(report,ensure_ascii=False,indent=2))

def d04():
 basepath=P/'approved_local/F024_d03_whole_head_right.png';rawpath=P/'originals/S13_d04_call_004_raw.png'
 base=Image.open(basepath).convert('RGBA');raw=Image.open(rawpath).convert('RGBA')
 assert base.size==raw.size==(1024,1536)
 # Whole output zoomed despite the prompt. Only the actual closed-lip patch is adopted.
 dx,dy=-23,21
 aligned=raw.transform(raw.size,Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),Image.Resampling.NEAREST)
 mask=Image.new('L',base.size,0);ImageDraw.Draw(mask).ellipse((733,743,833,815),fill=255)
 mask=mask.filter(ImageFilter.GaussianBlur(4));mask.save(P/'masks/d04_mouth_edit_scope.png')
 final=Image.composite(aligned,base,mask);final.putalpha(base.getchannel('A'))
 output=P/'approved_local/F030_d04_awake_closed_mouth.png';final.save(output)
 a=np.array(base);b=np.array(final);m=np.array(mask)
 report={'pose':'d04','status':'author_self_accepted_pending_Astra_segment_review','base':str(basepath.relative_to(P)),
 'base_sha256':sha(basepath),'raw':str(rawpath.relative_to(P)),'raw_sha256':sha(rawpath),
 'output':str(output.relative_to(P)),'output_sha256':sha(output),
 'method':'Actual generated closed mouth/skin patch translated back into accepted d03; all other pixels inherited. No code-painted lip or face deformation.',
 'raw_to_d03_patch_transform':[1,0,dx,0,1,dy],'mask':'masks/d04_mouth_edit_scope.png',
 'mask_sha256':sha(P/'masks/d04_mouth_edit_scope.png'),
 'outside_scope_RGBA_changed_pixels':int(np.any(a!=b,axis=2)[m==0].sum()),
 'alpha_changed_pixels':int((a[:,:,3]!=b[:,:,3]).sum()),
 'raw_full_image_adopted':False,
 'self_review':'闭合自然小唇线，无口腔/舌残留；双眼仍清醒上视；嘴外头、耳发、颈领、身体和alpha不动；原整图缩放漂移已拒用。'}
 assert report['outside_scope_RGBA_changed_pixels']==0 and report['alpha_changed_pixels']==0
 put(P/'qa/d04_validation.json',report)
 f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',24)
 s=Image.new('RGB',(1500,1000),'#f5f3ed');d=ImageDraw.Draw(s)
 for x,im,t in [(20,base,'d03 已自审 / 整头转后仍小开口'),(770,final,'d04 清醒收口 / 嘴外像素保持')]:
  crop=comp(im).crop((370,490,900,920));crop.thumbnail((700,730));s.paste(crop,(x,85));d.text((x,20),t,font=f,fill='#23333e')
 d.text((25,780),'真实闭口生成区域以(-23,+21)整数平移接回；没有缩放或挤压嘴部。',font=f,fill='#23333e')
 d.text((25,845),'原始整图放大漂移保全，不用于后续链；新母图仍为同尺度d03。',font=f,fill='#23333e')
 s.save(P/'qa/d03_d04_same_scale_closed_mouth.jpg',quality=97)
 comp(final).save(P/'qa/d04_final_on_light.jpg',quality=96)
 print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
 {'d02':d02,'d03':d03,'d04':d04}[sys.argv[1] if len(sys.argv)>1 else 'd02']()
