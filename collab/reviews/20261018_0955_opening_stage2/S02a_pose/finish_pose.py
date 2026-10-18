from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import json,hashlib,numpy as np
R=Path(__file__).parent
S=Path('astra_xiaoman_opening_refs_20261018_0906/originals')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def finish(call,frame,source,raw,next_anchor):
 s=Image.open(source).convert('RGBA');d=Image.open(raw).convert('RGBA');raw_size=list(d.size);n=Image.open(next_anchor).convert('RGBA')
 if d.size==(1671,941):
  padded=Image.new('RGBA',(1672,941),(0,0,0,0));padded.paste(d,(0,0));d=padded
 assert s.size==d.size==(1672,941)
 mask=Image.new('L',s.size,0);dr=ImageDraw.Draw(mask)
 # Upper head, pigtails, and generated neck/collar. Lower chest and lower sleeves remain original.
 box=(480,40,1205,775);poly=[(650,728),(1028,728),(1030,856),(1010,883),(666,883),(646,856)]
 dr.rectangle(box,fill=255);dr.polygon(poly,fill=255);mask=mask.filter(ImageFilter.GaussianBlur(3))
 out=R/'final'/f'S02a_F{frame:03d}.png';f=Image.composite(d,s,mask);f.save(out);mp=R/'qa'/f'F{frame:03d}_edit_mask.png';mask.save(mp)
 bg=Image.new('RGBA',s.size,(90,94,99,255))
 def flat(im):return Image.alpha_composite(bg,im).convert('RGB')
 for label,im in [('previous',s),('next',n)]:Image.blend(flat(im),flat(f),.5).save(R/'qa'/f'F{frame:03d}_{label}_50pct.png')
 ims=[flat(s),flat(f),flat(n)];sheet=Image.new('RGB',(1672,622),(28,33,40));ds=ImageDraw.Draw(sheet)
 for i,(im,label) in enumerate(zip(ims,['previous original','new in-between','next original'])):
  im=im.crop((450,70,1220,890));im.thumbnail((553,590));sheet.paste(im,(i*557,30));ds.text((i*557+5,8),label,fill='white')
 sheet.save(R/'qa'/f'F{frame:03d}_pose_review.png')
 a=np.asarray(s);b=np.asarray(f);mm=np.asarray(mask);outside=int(np.any(a!=b,axis=2)[mm==0].sum());chest=int(np.any(a[895:]!=b[895:],axis=2).sum())
 p=R/'manifest.json';m=json.loads(p.read_text());entry=next(x for x in m['calls'] if x['call']==call);entry.update({'status':'locally_accepted_pending_independent_review','raw':str(raw),'raw_sha256':sha(raw),'raw_size':raw_size,'final':str(out),'final_sha256':sha(out),'final_size':list(f.size),'composite_static_master':str(source),'composite_static_master_sha256':sha(source),'mask':str(mp),'mask_sha256':sha(mp),'mask_shape':{'upper_box':box,'collar_polygon':poly,'gaussian_radius_px':3},'transform':('Pad one fully transparent column at right, no rescale or shift' if raw_size==[1671,941] else 'none; native 1672x941 donor and static master'),'mask_outside_changed_pixels':outside,'lower_chest_y895_plus_changed_pixels':chest,'next_anchor':str(next_anchor),'next_anchor_sha256':sha(next_anchor),'notes':'Generated head and real neck/collar connection rejoined by explicit mask. No translation or scale of donor. Lower chest and lower sleeves retain master pixels. Acting gate remains independent.'});p.write_text(json.dumps(m,indent=2));print(entry)
if __name__=='__main__':finish(6,23,S/'S02a_k01_focus.png',R/'raw/call06_F023_local_connection.png',S/'S02a_k02_tense.png')
