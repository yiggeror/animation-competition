"""One F036 review input. Zero image calls; never production character art."""
from pathlib import Path
import copy, hashlib, json, subprocess, xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation

P=Path(__file__).resolve().parent; PACK=P.parent; ROOT=PACK.parents[2]
S=PACK/'handoff_008_020_032_generation_002/F032/S20_F032_accepted.png'
A=np.array(Image.open(S).convert('RGBA')); H,W=A.shape[:2]; yy,xx=np.indices((H,W))
assert hashlib.sha256(S.read_bytes()).hexdigest()=='b586eee0eebbd09167d27171eefccf5297b58472a736010ce871497452195b95'
NS='http://www.w3.org/2000/svg'; ET.register_namespace('',NS)
old=ET.parse(PACK/'next_036_057_inputs_002/F036/inputs/01_unique_opaque_complete_target.svg').getroot()
original_x=next(c for c in old if c.attrib.get('transform')=='translate(608 190) scale(1.55)')
root=ET.Element('{%s}svg'%NS,{'width':str(W),'height':str(H),'viewBox':f'0 0 {W} {H}'})
def path(d,fill='#ffcfac',stroke='#644b3c',width='2.8'):
 return ET.Element('{%s}path'%NS,{'d':d,'fill':fill,'stroke':stroke,'stroke-width':width,'stroke-linejoin':'round','stroke-linecap':'round'})
# Whole continuous leg contours. No knee/elbow/shoulder construction rings.
root.append(path('M568 687 C563 717 568 750 568 780 L568 876 Q571 891 582 889 L593 880 C596 830 604 775 607 736 L608 694 Z','#efc09f'))
root.append(path('M626 699 C625 734 630 766 633 796 L638 875 Q645 886 657 879 L665 867 C666 824 663 775 665 738 L664 706 Z'))
for i in [6,13]:
 g=ET.Element('{%s}g'%NS,{'transform':'translate(608 190) scale(1.55)'});g.append(copy.deepcopy(original_x[i]));root.append(g)
# Far arm is one silhouette, behind the torso; the wrist ends at the real L palm.
root.append(path('M621 372 C640 383 676 422 714 444 Q724 451 738 444 L819 411 Q826 409 831 414 L839 434 L736 476 Q714 485 699 474 C665 451 631 418 610 400 Q603 383 621 372 Z','#efc09f'))
# Reuse only the already-new F036 torso/head construction, never the old whole child.
g=ET.Element('{%s}g'%NS,{'transform':'translate(608 190) scale(1.55)'})
for i in range(20,31):g.append(copy.deepcopy(original_x[i]))
root.append(g)
# Near arm: continuous shoulder->upper arm->bent elbow->forearm->real R wrist.
root.append(path('M628 363 C647 348 673 322 699 301 Q713 286 727 296 C747 314 774 344 800 357 L807 377 Q801 388 791 386 C767 371 740 350 719 330 Q715 326 711 331 C688 350 665 378 644 391 Q627 390 628 363 Z'))
root.append(path('M714 314 Q713 323 724 330','none','#c99071','1.4'))
root.append(path('M590 352 C603 342 625 345 642 357 C651 368 648 383 637 393 L620 404 C605 407 592 397 587 383 Q581 368 590 352 Z','#f2c64b'))
root.append(path('M597 355 Q607 367 610 379 M632 362 Q640 371 637 382','none','#d5a63b','1.4'))
svg=P/'child_continuous_construction.svg';ET.ElementTree(root).write(svg,encoding='unicode')
subprocess.run(['node',str(PACK/'handoff_008_020_032_generation_002/render_static.cjs'),str(svg)],cwd=ROOT,check=True)
C=np.array(Image.open(svg.with_suffix('.png')).convert('RGBA'))
svg.with_suffix('.png').unlink();svg.unlink()

def poly(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
R=poly([(789,363),(798,348),(813,340),(825,335),(841,341),(849,353),(850,379),(837,390),(812,391),(793,386)])
L=poly([(823,416),(831,402),(847,394),(861,394),(878,402),(882,432),(870,446),(847,448),(832,440),(824,431)])
# Actual source wood only, including its existing ink/AA border; no new faux rods.
r,g,b=A[:,:,:3].astype(float).transpose(2,0,1)
wood=(A[:,:,3]>80)&(r>g+10)&(g>b+10)&(b<g*.76)
reg=json.loads((PACK/'cam20_crane_lamp_left_001/registration_input.json').read_text())
shaft={}
for role in ['T_H','T_S']:
 q=reg['rods'][role];dist=np.abs(yy-q['slope']*xx-q['intercept'])/np.hypot(1,q['slope'])
 band=(dist<13)&(xx>=773)&(xx<951)&(yy>320)&(yy<461)
 shaft[role]=binary_dilation(wood&band&~R&~L,iterations=1)&band&~R&~L
hands={'R':R,'L':L};translations={'R':(0,0),'L':(0,-1)};own={'R':'T_H','L':'T_S'}
def shift_array(a,dx,dy):
 out=np.zeros_like(a);sy=slice(max(0,-dy),min(H,H-dy));sx=slice(max(0,-dx),min(W,W-dx));out[max(0,dy):min(H,H+dy),max(0,dx):min(W,W+dx)]=a[sy,sx];return out

# Grandma remains source032. Only the already-approved C-rod/gap delta is reused.
G=((xx>=995)|((xx>=889)&(yy>=285)&(yy<=440))|((xx>=922)&(yy>=440)&(yy<=527)))&~shaft['T_H']&~shaft['T_S']
G&=~shift_array(shaft['T_S'],0,-1)
G&=A[:,:,3]>0
old000=np.array(Image.open(PACK/'F000/f000_scene_gate_001/cleanup/S20_F000_master_clean.png').convert('RGBA'))
rotated=np.array(Image.open(PACK/'cam20_crane_lamp_left_001/people_F000_rods_rotated.png').convert('RGBA'))
D=np.array(Image.open(PACK/'cam20_crane_lamp_left_001/mask_all_changed_pixels.png').convert('L'))>0
gdelta=D&G;assert np.array_equal(A[gdelta],old000[gdelta])
# The reviewed real front texture intentionally ends 45px before each clamp;
# its existing full scene shaft must continue behind the original finger gaps.
high=Image.new('RGBA',(W*4,H*4));draw=ImageDraw.Draw(high)
for role in ['C_N','C_B']:
 q=reg['rods'][role];p0=q['shaft_tip_master_px'];p1=[952,q['slope']*952+q['intercept']]
 pts=[tuple(v*4 for v in p0),tuple(v*4 for v in p1)]
 draw.line(pts,fill=(103,80,52,255),width=16);draw.line(pts,fill=(178,139,82,255),width=10)
crane=np.array(high.resize((W,H),Image.Resampling.LANCZOS))
base=crane.copy();base[G]=A[G]
base[gdelta]=rotated[gdelta]
gaps=gdelta&(rotated[:,:,3]==0);base[gaps]=crane[gaps]
# Visible C shafts use the approved rigid rotations and stay behind the new child.
cm=D&~G&(rotated[:,:,3]>0);base[cm]=rotated[cm]
B=np.array(Image.alpha_composite(Image.fromarray(base),Image.fromarray(C)))
protected=np.zeros((H,W),bool);grip_rows=[]
for side in ['R','L']:
 area=hands[side]|shaft[own[side]];core=area&(A[:,:,3]>180)
 mask=area&(A[:,:,3]>5)&binary_dilation(core,iterations=1)
 dx,dy=translations[side];M=shift_array(mask,dx,dy);V=shift_array(A,dx,dy)
 layer=np.zeros_like(A);layer[M]=V[M]
 B=np.array(Image.alpha_composite(Image.fromarray(B),Image.fromarray(layer)));protected|=M
 opaque=M&(V[:,:,3]==255);assert np.array_equal(B[opaque],V[opaque])
 grip_rows.append({'hand':'X.'+side,'rod':own[side],'translation_px':[dx,dy],'rotation_degrees':0,'scale':1,'source_pixels':int(mask.sum()),'rigid_layer_RGBA_changes':0,'final_opaque_pair_RGBA_changes':0,'AA_wrist_join':'original alpha composited over new continuous forearm; no geometric warp'})
# Preserve all original G figure pixels outside the previously approved C delta.
assert np.array_equal(B[G&~D],A[G&~D])
out=Image.fromarray(B);out.save(P/'01_F036_corrected_target.png')
box=(690,270,1010,475);out.crop(box).resize((960,615),Image.Resampling.NEAREST).save(P/'02_F036_same_view_palms_rods_3x.png')
visible_crane=((crane[:,:,3]>0)|cm)&(C[:,:,3]==0)&~G
old_child=(A[:,:,3]>80)&(((xx<740)&(yy>145))|((xx<889)&(yy>325)&(yy<490)))
edit=binary_dilation((C[:,:,3]>0)|old_child,iterations=10)&~G&~visible_crane&~protected
Image.fromarray((edit*255).astype('uint8')).convert('RGB').save(P/'03_child_edit_only_black_protect.png')
metadata={'status':'ONE_CORRECTED_F036_INPUT_PENDING_ASTRA','new_image_calls':0,'source032':str(S.relative_to(ROOT)),'source032_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'failed_raw_used':False,'new_child_domain':'whole head/neck/chest/pelvis/two legs and two continuous arms; no shoulder/elbow rings; real palms and each own turtle shaft protected','grandma_nonrod_figure_RGBA_changes':0,'grandma_existing_approved_C_delta_pixels':int(gdelta.sum()),'C_axis_source':'445d2921 / cam20_crane_lamp_left_001; reused without angle/camera change','rigid_grip_pairs':grip_rows,'ownership':{'T_H':'X.R','T_S':'X.L','C_B':'G.L','C_N':'G.L'},'contact_crop_box':list(box),'crop_scale':3,'single_mask':'white child edit only; grandma, both real palm/shaft pairs, approved C rods black protected','identity_reference_only':'existing next_036_057_inputs_002/F036/inputs/03_heads_internal_materials_only.png; whole old person is not a competing model reference','target_is_input_only_not_new_animation_frame':True}
for name in ['01_F036_corrected_target.png','02_F036_same_view_palms_rods_3x.png','03_child_edit_only_black_protect.png']:
 metadata.setdefault('files',[]).append({'path':name,'sha256':hashlib.sha256((P/name).read_bytes()).hexdigest()})
(P/'source_and_protection.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:metadata[k] for k in ['new_image_calls','grandma_nonrod_figure_RGBA_changes','grandma_existing_approved_C_delta_pixels','rigid_grip_pairs']},ensure_ascii=False))
