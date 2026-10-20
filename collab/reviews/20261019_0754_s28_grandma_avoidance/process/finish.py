from pathlib import Path
from PIL import Image
import numpy as np, subprocess as sp, json, hashlib, ctypes as CT
src=Path('/workspace/scratch/f060b5601755/s28_rod_clearance_review/recovery_clearance/check_recovery.py').read_text();a=src.index("r=CT.CDLL(");b=src.index("\ndef render(p):",a);exec(src[a:b],globals())
def render_svg(p,out):
 hd=r.rsvg_handle_new_from_file(str(p).encode(),None);assert hd;sf=ca.cairo_image_surface_create(0,1024,1536);ctx=ca.cairo_create(sf);assert r.rsvg_handle_render_cairo(hd,ctx);assert ca.cairo_surface_write_to_png(sf,str(out).encode())==0;ca.cairo_destroy(ctx);ca.cairo_surface_destroy(sf);go.g_object_unref(hd)
D=Path(__file__).parent
P=Path('/workspace/scratch/f060b5601755/s28_first_input_20261019_0540')
B=P/'grandma_first_input/call_GM_F000/S28_GM_F000_raw.png'
BC=D.parent/'clean_grandma_rods/S28_GM_F000_clear_external_rods.png'
def run(*args):
 sp.run(['magick',*map(str,args)],check=True)
def svgmask(name,body):
 p=D/(name+'.svg');p.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1536"><rect width="1024" height="1536" fill="black"/>'+body+'</svg>');render_svg(p,D/(name+'.png'));return D/(name+'.png')
def hem(im,frame):
 a=np.array(Image.open(im).convert('RGBA')).astype(float)
 lim={'000':(506,798),'006':(502,815),'012':(497,830)}[frame]
 xs=np.arange(lim[0],lim[1]+1);ys=[]
 for x in xs:
  z=a[790:880,max(0,x-3):x+4]
  blue=(z[:,:,2]>140)&(z[:,:,2]>z[:,:,1]+18)&(z[:,:,3]>128)
  yy=np.where(np.sum(blue,axis=1)>=2)[0]
  ys.append(float(790+yy.max()+4) if len(yy) else float('nan'))
 ys=np.array(ys);good=np.isfinite(ys);ys=np.interp(xs,xs[good],ys[good]);ys=np.array([np.median(ys[max(0,i-2):min(len(ys),i+3)]) for i in range(len(ys))])
 return [[0,820],[lim[0]-1,float(ys[0])]]+[[int(x),round(float(y),2)] for x,y in zip(xs,ys)]+[[lim[1]+1,float(ys[-1])],[1024,820]]

oldhem=hem(B,'000')
upperold=svgmask('baseline_upper_domain','<path fill="white" d="M0 0H1024V820 '+ ' '.join('L%g %g'%tuple(v) for v in oldhem[::-1])+' Z"/>')
# Protection follows entire palms, jade, and wrist collars; no rectangular cut through a wrist.
protected=svgmask('protected_palms_and_contacts','<path fill="white" d="M0 520H315V674H0Z M0 674H495V815H0Z"/>')
# Original pants and shoes remain at exactly their own pixel positions; only a hidden 30px under-hem strip is supplied above their upper edge.
run(BC,'-crop','1024x1476+0+60','+repage','-gravity','north','-background','none','-extent','1024x1536',D/'underhem_texture_source.png')
# A full semantic original hand patch excludes the separate blue blouse component.
from scipy.ndimage import label,binary_dilation
ba=np.array(Image.open(BC).convert('RGBA'));zone=(ba[674:815,:491,3]>1);labs,nlab=label(zone);chosen=labs[751-674,354];keep=binary_dilation(labs==chosen,iterations=1)
rects=[]
for yi,row in enumerate(keep):
 zz=np.where(row)[0]
 if len(zz):rects.append(f'<rect x="{zz.min()}" y="{yi+674}" width="{zz.max()-zz.min()+1}" height="1" fill="white"/>')
kh=svgmask('original_hand_semantic_keep','<path fill="white" d="M0 0H1024V674H0Z M0 815H1024V1536H0Z M515 674H1024V815H515Z"/>'+''.join(rects)+'<path fill="white" d="M490 697 L515 691 L515 756 L490 759Z"/>')
run(BC,kh,'-channel','A','-fx','u.a*((j>=674&&j<815&&i>470&&i<515&&u.b>=u.g&&u.g>=u.r)?0:1)','+channel','-depth','8',D/'original_full_hands_only.png')
meta={'operation':'zero-call semantic wrist and lower-garment continuity finish','editing_engine':'ImageMagick; Python only reads pixels and writes coordinates/metadata','baseline':str(B),'clear_baseline':str(BC),'no_new_generation':True,'frames':{}}
for f,shift,delta in [('006',(60,7),(12,8,-3)),('012',(67,8),(19,9,-14))]:
 print('START',f,flush=True)
 sub=D/('F'+f);sub.mkdir(exist_ok=True)
 raw=P/f'grandma_avoidance_group/call_GM_F{f}/S28_GM_F{f}_raw.png'
 # Single uniform source registration. Exact integer copy translation, no scale or rotation.
 run(raw,'-background','none','-gravity','northwest','-splice',f'{shift[0]}x{shift[1]}','-crop','1024x1536+0+0','+repage',sub/'uniform_registered.png')
 # Baseline cloth-only medians; white motifs, skin, hair, pants, and protected original palms are not globally filtered.
 exprs=[]
 for c,d in zip('rgb',delta):
  exprs.append(f'u.{c}+({d}/255)*((i>480&&j>330&&j<880)?min(1,max(0,(u.b-u.r-0.065)*25))*min(1,max(0,(u.g-u.r-0.025)*30))*min(1,max(0,(u.b-0.52)*20)):0)')
 # Three channel passes preserve alpha independently.
 cur=sub/'uniform_registered.png'
 for c,expr in zip('RGB',exprs):
  nxt=sub/f'cloth_{c}.png';run(cur,'-channel',c,'-fx',expr,'+channel','-depth','8',nxt);cur=nxt
 run(cur,sub/'cloth_aligned.png')
 # Smooth local vertical remap of the entire wrist/forearm ribbon. Taper to zero by elbowward edge.
 # This is a <=8px contour reconciliation, not an independent body registration or limb-length scale.
 pars={'006':[(315,430,590,2,6/46,540,680),(480,620,699,-7,6/55,630,800)],'012':[(315,430,590,-1,5/46,540,680),(480,620,699,0,7/55,630,800)]}[f]
 terms=[]
 for x0,x1,y0,b,k,lo,hi in pars:
  w=f'(0.5+0.5*cos(pi*(i-{x0})/{x1-x0}))'
  g=f'min(1,max(0,(j-{lo})/12))*min(1,max(0,({hi}-j)/12))'
  terms.append(f'(i>={x0}&&i<{x1}&&j>{lo}&&j<{hi}?{w}*({b}+({k})*(j-{y0}))*{g}:0)')
 expr='u.p{i,j+'+'+'.join(terms)+'}'
 run(sub/'cloth_aligned.png','-channel','RGBA','-virtual-pixel','transparent','-fx',expr,'+channel','-depth','8',sub/'wrist_ribbons_joined.png')
 nh=hem(sub/'uniform_registered.png',f)
 nhmask=svgmask('F'+f+'_new_upper_domain','<path fill="white" d="M0 0H1024V820 '+' '.join('L%g %g'%tuple(v) for v in nh[::-1])+' Z"/>')
 # Whole lower body first, untouched. Original upper clothing is cleared rather than retained as thin side slivers.
 # New torso covers this base; the upper-edge texture is only visible in the narrow opening above original trouser edge.
 run(BC,D/'underhem_texture_source.png',upperold,'-channel','RGBA','-fx','u*(1-u[2])+u[1]*u[2]','+channel','-depth','8',sub/'lower_body_with_hidden_hem_extension.png')
 hipx=502 if f=='006' else 497
 hp=svgmask('F'+f+'_upper_hip_contour','<rect width="1024" height="1536" fill="white"/><path fill="black" d="M0 790 H'+str(hipx)+' C'+str(hipx)+' 810 502 835 501 878 H0Z"/>')
 run(sub/'lower_body_with_hidden_hem_extension.png',hp,'-channel','A','-fx','u.a*u[1].r','+channel','-depth','8',sub/'lower_body_hip_joined.png')
 run(sub/'lower_body_hip_joined.png',sub/'wrist_ribbons_joined.png',nhmask,'-channel','RGBA','-fx','u*(1-u[2])+u[1]*u[2]','+channel','-depth','8',sub/'body_joined.png')
 # Complete original palms/bracelet plus broad feathered forearm corridor, never a cut through hand/fingers.
 # Define replacement mask: 1 original, 0 new. 20px crossfade sits beyond protected wrists.
 protectbody='<path fill="white" d="M0 520H315V674H0Z M0 674H495V815H0Z"/>'
 # SVG linear ramps only across the forearm itself. At far edge new & old contours coincide to subpixel.
 ramps='<defs><linearGradient id="g"><stop stop-color="white"/><stop offset="1" stop-color="black"/></linearGradient></defs><path fill="url(#g)" d="M315 570 H335 V650 H315Z"/><path fill="url(#g)" d="M495 696 L515 691 L515 756 L495 759Z"/>'
 pm=svgmask('F'+f+'_hand_restore_mask',protectbody+ramps)
 run(sub/'body_joined.png',D/'original_full_hands_only.png',pm,'-channel','RGBA','-fx','u*(1-u[2])+u[1]*u[2]','+channel','-depth','8',D/f'S28_GM_F{f}_finished.png')
 out=D/f'S28_GM_F{f}_finished.png'
 run(out,'-channel','A','-fx','u.a*((i>=487&&i<=494&&j>=680&&j<=696)?0:1)','+channel','-depth','8',sub/'final_no_stray.png')
 run(sub/'final_no_stray.png',out)
 run(out,'-background','#969696','-alpha','remove','-alpha','off',sub/'gray.png')
 run(out,'-background','#2c3443','-alpha','remove','-alpha','off',sub/'deep.png')
 run(sub/'gray.png','-crop','700x430+150+500','+repage','-resize','1400x860',sub/'seams_2x.png')
 meta['frames'][f]={'raw':str(raw),'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'uniform_source_transform':[1,0,0,1,*shift],'cloth_only_median_delta_rgb':delta,'wrist_local_vertical_contour_reconciliation':pars,'source_to_final_no_limb_length_normalization':True,'original_pants_and_shoes_unchanged_below_y':880,'original_four_palm_entries':[[232,630],[229,619],[354,751],[359,739]],'original_hem':oldhem,'new_hem':nh,'output':str(out)}
 (D/'PROCESS_WORKING.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
 print('DONE',f,flush=True)
