from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
import numpy as np,json,hashlib
P=Path(__file__).parent;R=P.parent;X=R/'x197_x208_zero_call';Y,XX=np.indices((1254,1254));font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def masks(a):
 r,g,b=a[:,:,:3].astype(float).transpose(2,0,1);ok=a[:,:,3]>245
 return {'arm_skin':ndimage.binary_erosion(ok&(Y>455)&(Y<755)&(XX>500)&(XX<1030)&(r>180)&(g>120)&(b>105)&(r-g>22)&(g-b>9)&(g-b<72),iterations=2),'yellow_cloth':ndimage.binary_erosion(ok&(Y>395)&(Y<940)&(XX>420)&(XX<995)&(r>190)&(g>150)&(b<130)&(r-g>6),iterations=2)}
b=np.array(Image.open(R/'refs/assets/chars/x15/F000.png').convert('RGBA'));ref={k:b[m,:3].mean(0) for k,m in masks(b).items()};out={'status':'POST_LOCK_MINIMAL_COLOR_DELTA_NO_NEW_GENERATION','historical_gate':'Same-mother semantic-region mean RGB difference within +/-4 per channel, parent supplied 2026-10-18 16:45 gate.','mother':str((R/'refs/assets/chars/x15/F000.png').resolve()),'mother_sha256':sha(R/'refs/assets/chars/x15/F000.png'),'mother_region_mean_srgb':{k:v.tolist() for k,v in ref.items()},'method':'Same registered original native complete yellow-cloth region only. A small constant G/B offset is smoothly reduced near low-chroma highlight and dark ink. White dot cores/edges, black contour, skin, hair, alpha and geometry unchanged. No histogram reshaping or global frame grade. Source originals, frozen requests, old final files and previous manifest untouched.','frames':[]}
page=Image.new('RGB',(1200,980),'#f7f5ed');d=ImageDraw.Draw(page)
for i,f in enumerate([197,200,203,206]):
 src=X/f'X{f}_complete_registered_candidate.png';a=np.array(Image.open(src).convert('RGBA'));z=a.copy();off=np.array([0,4,5] if f==203 else [0,0,3] if f==206 else [0,0,0],float)
 if off.any():
  r,g,bl=a[:,:,:3].astype(float).transpose(2,0,1);w=np.clip((g-bl-55)/30,0,1)*np.clip((r-140)/50,0,1);w*=((Y>395)&(Y<940)&(XX>420)&(XX<995)&(a[:,:,3]>0)&(bl<135))
  white=(a[:,:,:3].min(2)>175)&(a[:,:,3]>0);w[ndimage.binary_dilation(white,iterations=1)]=0
  z[:,:,:3]=np.clip(np.rint(a[:,:,:3].astype(float)+w[:,:,None]*off),0,255).astype('uint8');dst=P/f'X{f}_complete_native_palette_calibrated_FINAL.png';Image.fromarray(z).save(dst)
 else:dst=src
 change=np.any(a!=z,axis=2);rec={'frame':f,'source_final':str(src.resolve()),'source_final_sha256':sha(src),'final':str(dst.resolve()),'final_sha256':sha(dst),'maximum_rgb_offset':off.tolist(),'changed_pixels':int(change.sum()),'alpha_changed_pixels':int((a[:,:,3]!=z[:,:,3]).sum()),'regions':{}}
 for k,m in masks(a).items():
  before=a[m,:3].mean(0);after=z[m,:3].mean(0);rec['regions'][k]={'sample_pixels':int(m.sum()),'before_mean_rgb':before.tolist(),'before_mean_delta_from_mother':(before-ref[k]).tolist(),'after_mean_rgb':after.tolist(),'after_mean_delta_from_mother':(after-ref[k]).tolist(),'pass_each_channel_abs_at_most_4':bool(np.max(np.abs(after-ref[k]))<=4)}
 out['frames'].append(rec)
 if off.any():
  for j,arr in enumerate([a,z]):
   im=Image.fromarray(arr);bg=Image.new('RGBA',im.size,'#f7f5ed');bg.alpha_composite(im);crop=bg.crop((440,390,980,940)).resize((480,489)).convert('RGB');page.paste(crop,(j*600+60,(i-2)*490));d.text((j*600+18,(i-2)*490+5),f'X{f} '+('已归档前色' if j==0 else '同原生裙最小校色'),font=font(20),fill='#294953')
page.save(P/'X203_X206_SAME_NATIVE_CLOTH_PALETTE_BEFORE_AFTER.jpg',quality=91)
p=P/'X197_X206_MEAN_RGB_GATE_AND_TWO_FINAL_DELTAS.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps({'index':str(p.resolve()),'sha256':sha(p),'frames':[{'frame':v['frame'],'sha':v['final_sha256'],'cloth_delta':np.round(v['regions']['yellow_cloth']['after_mean_delta_from_mother'],3).tolist(),'skin_delta':np.round(v['regions']['arm_skin']['after_mean_delta_from_mother'],3).tolist(),'alpha_changed':v['alpha_changed_pixels']} for v in out['frames']]},ensure_ascii=False))
