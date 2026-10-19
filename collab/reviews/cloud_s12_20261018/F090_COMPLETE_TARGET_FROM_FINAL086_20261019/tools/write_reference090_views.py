from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json

def write_views(O,R,M,g,B,n,bg,fg,active,fixed,feet,s,t):
    font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
    first=Image.new('RGBA',(1024,1536),'#e1e4e6');first.alpha_composite(Image.fromarray(n));dr=ImageDraw.Draw(first)
    for y,txt,sz in [(18,'F090 / HIPS RISE / BOTH ELBOWS RETRACT / COMPLETE ROUND KNEES',20),(55,'SOLE QUALIFIED ACTUAL086 PIXELS / POSE REFERENCE ONLY',20),(91,'Two complete shoulder-elbow-wrist-palm chains; true closed grips remain.',18),(1410,'Full knee faces + natural folds must be NEW drawing; no growing box cut.',18),(1450,'Current real shins/ankles/shoes/blank and ground support remain native.',18)]:dr.text((18,y),txt,font=font(sz),fill='#25313b')
    first.convert('RGB').save(O/'inputs/01_F090_FULL_VISIBLE_RISE_AND_BOTH_ELBOW_RETRACTION.png')

    props=Image.open(O/'code_props/F090_TRUE_CRANE_AND_TWO_PHYSICALLY_RIGID_RODS_REFERENCE.png').convert('RGBA')
    base=Image.open(R/'right_hand_lower_rod_inputs_20261019/first034_040/code_props/background_box_cloth_UNCHANGED.png').convert('RGBA');base=base.copy()
    # Release only the old pressure fold; current code-crane alpha supplies cloth
    # shadow. Static box/room and old actual support shadow are not reconstructed.
    k=4;c=Image.new('RGBA',(1920*k,1080*k));cd=ImageDraw.Draw(c);cd.polygon([(int(x*k),int(y*k)) for x,y in [(1010,800),(1850,800),(1838,764),(1022,764)]],fill='#2f4a78')
    for j in range(16):
     cx=1050+j*52;cy=784+(j%2)*6
     for xx,yy,rr in [(cx,cy,4),(cx+26,cy-9,2.5)]:cd.ellipse(((xx-rr)*k,(yy-rr)*k,(xx+rr)*k,(yy+rr)*k),fill=(235,235,225,179))
    c=c.resize((1920,1080),Image.Resampling.LANCZOS);base.paste(c.crop((1430,780,1560,800)),(1430,780))
    shadow=props.getchannel('A').transform((1920,1080),Image.Transform.AFFINE,(1,-.04/.06,795*.04/.06,0,1/.06,800-795/.06),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(3));clip=Image.new('L',(1920,1080));ImageDraw.Draw(clip).polygon([(1010,800),(1850,800),(1838,764),(1022,764)],fill=255);sa=np.uint8(np.asarray(shadow)*.07)*(np.asarray(clip)>0);shade=Image.new('RGBA',(1920,1080),(14,20,30,0));shade.putalpha(Image.fromarray(sa));base.alpha_composite(shade)
    base.save(O/'code_props/F090_BOX_CLOTH_UNLOAD_CONTEXT_REFERENCE.png')
    def scene(im):return im.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BICUBIC)
    ctx=base.copy();ctx.alpha_composite(Image.open(M/'actual_scene/F086_native_ground_shadows_actual_layer.png'));ctx.alpha_composite(scene(Image.fromarray(bg)));ctx.alpha_composite(props);ctx.alpha_composite(scene(Image.fromarray(fg)));ctx.alpha_composite(Image.open(M/'actual_scene/F086_box_front_actual_layer.png'));ctx.save(O/'anatomy/F090_SAME_PERSON_TRUE_PROP_BOX_GROUND_CONTEXT_REFERENCE_ONLY.png');dr=ImageDraw.Draw(ctx);dr.text((18,18),'F090 SAME POSE + TRUE60deg CODE CRANE / PHYSICALLY RIGID RODS / UNLIT REFERENCE ONLY',font=font(22),fill='white');ctx.convert('RGB').save(O/'inputs/02_SAME_F090_TRUE_PAPER_TURN_RODS_BOX_GROUND_CONTEXT.png')

    overlay=Image.new('RGBA',(1024,1536),'#e1e4e6');overlay.alpha_composite(Image.fromarray(n));dr=ImageDraw.Draw(overlay)
    for role,color in [('L','#1b8c85'),('R','#bd6c22')]:
     a=g['arms_actual_source_projected_proxies_not_hidden_bones'][role];pts=[a['target'][k] for k in ['shoulder','elbow','wrist','true_grip']];dr.line([tuple(v) for v in pts],fill=color,width=3)
     for label,p in zip(['S','E','W','G'],pts):dr.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),fill=color);dr.text((p[0]+8,p[1]-10),role+label,font=font(16),fill=color)
    dr.text((18,18),'ACTUAL-SOURCE VISIBLE ARM PROXIES / REVIEW ONLY / NOT A THIRD MODEL POSE',font=font(20),fill='#25313b');overlay.convert('RGB').save(O/'reference/SAME_F090_VISIBLE_COMPLETE_ARM_CHAINS_AND_TRUE_GRIPS.png')
    g['reference_geometry_checks']={'fixed_support_RGBA_changes':0,'fixed_visible_pixels':int((fixed&(B[:,:,3]>0)).sum()),'source_reference_pixels_adopted_as_new_art':0,'source_controls':s.tolist(),'target_controls':t.tolist(),'imagegen_calls':0,'actual090_full_Canvas':0,'code_prop_only_reference_batches':1};(O/'geometry/F090_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json').write_text(json.dumps(g,indent=2)+'\n')
    print(json.dumps({k:v for k,v in g['reference_geometry_checks'].items() if k not in ['source_controls','target_controls']},indent=2))
