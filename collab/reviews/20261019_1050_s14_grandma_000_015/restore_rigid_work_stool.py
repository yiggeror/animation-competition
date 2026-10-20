from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,binary_fill_holes,label
import numpy as np,json,hashlib
D=Path('/workspace/scratch/f060b5601755/s14_stage_setup_inputs_20261019_0756/grandma_throw_inputs');M=Image.open(D/'G000_whole_registered_candidate.png').convert('RGBA');a=np.array(M);Y,X=np.indices(a.shape[:2]);r,g,b,al=a.transpose(2,0,1);wood=(Y>=1012)&(Y<=1027)&(X>=345)&(X<=650)&(al>0)&(r>35)&(r>g*1.10)&(g>b*1.22);mask=(Y>=1027)|(wood);arr=a.copy();arr[:,:,3]=np.where(mask,al,0);arr[arr[:,:,3]==0,:3]=0;prop=Image.fromarray(arr)
# Only previously occluded seat-surface strips are completed from adjacent original G000 wood pixels, behind every shoe.
fill=Image.new('RGBA',M.size);rowtex=M.crop((483,1018,499,1027));
for x0 in range(376,626,16):fill.alpha_composite(rowtex,(x0,1018))
fill.alpha_composite(prop);prop=fill;prop.save(D/'G000_locked_complete_rigid_work_stool.png')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19);panel=Image.new('RGB',(3*627,2*665),'#f1f2ed');contacts=Image.new('RGB',(3*600,2*350),'#f1f2ed');manifest=[]
# Tiny uniform x anchor refinements align the midpoint of the two soles, not individual feet.
xref={0:0,3:3,6:-1,9:1,12:1,15:-7}
for i,f in enumerate([0,3,6,9,12,15]):
 im=Image.open(D/f'G{f:03d}_whole_registered_candidate.png').convert('RGBA');dx=xref[f]
 if dx:im=im.transform(im.size,Image.Transform.AFFINE,(1,0,-dx,0,1,0),resample=Image.Resampling.BICUBIC)
 q=np.array(im);rr,gg,bb,aa=q.transpose(2,0,1);brown=(Y>=1009)&(rr>35)&(rr>gg*1.10)&(gg>bb*1.22)&(aa>0);remove=(Y>=1027)|brown
 # Preserve the original white/black outsole antialias pixels at each actual shoe, but not brown generated wood.
 foot_region=(Y>=997)&(Y<1030)&(X>390)&(X<625);white=foot_region&(aa>64)&(rr>160)&(gg>160)&(bb>160);labs,n=label(white);sizes=np.bincount(labs.ravel());ids=np.argsort(sizes[1:])[-2:]+1;outsoles=np.isin(labs,ids);edge=binary_dilation(outsoles,iterations=2);bottom=np.where(edge,Y,-1).max(axis=0);shoemask=(Y<=bottom[None,:])&(Y>=997)&(bottom[None,:]>=0);remove=(Y>=1010)&(X>300)&(X<700)&(~shoemask)
 fg=q.copy();fg[:,:,3]=np.where(remove,0,aa);foreground=Image.fromarray(fg)
 out=prop.copy();out.alpha_composite(foreground);out.save(D/f'G{f:03d}_rigid_stool_restored.png')
 c=Image.new('RGBA',out.size,'#f1f2ed');c.alpha_composite(out);c=c.convert('RGB');dd=ImageDraw.Draw(c);dd.line((210,277,1140,277),fill='#809186',width=2);dd.line((220,1180,740,1180),fill='#a08776',width=2);panel.paste(c.resize((627,627)),((i%3)*627,(i//3)*665+38));ImageDraw.Draw(panel).text(((i%3)*627+15,(i//3)*665+8),f'G{f:03d}',font=font,fill='#344c57');contact=c.crop((340,965,660,1152)).resize((600,350));contacts.paste(contact,((i%3)*600,(i//3)*350));manifest.append({'frame':f,'file':str(D/f'G{f:03d}_rigid_stool_restored.png'),'sha256':hashlib.sha256((D/f'G{f:03d}_rigid_stool_restored.png').read_bytes()).hexdigest(),'whole_x_sole_midpoint_refinement':dx,'all_figure_and_cloth_pixels_retained_above_contact_region':bool(np.array_equal(q[Y<1009],np.array(foreground)[Y<1009])),'cloth_outside_prop_region_RGBA_unchanged':bool(np.array_equal(q[X>=700],np.array(foreground)[X>=700])),'stool_source':'G000 one fixed whole prop','stool_rescale_per_frame':False,'sole_contact_review_required':True})
panel.save(D/'G000_G015_rigid_stool_restored_group.jpg');contacts.save(D/'G000_G015_actual_shoe_seat_contacts.jpg');(D/'rigid_stool_restore_manifest.json').write_text(json.dumps(manifest,indent=2));print('saved group, contacts, manifest')
