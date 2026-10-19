from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json
O=Path(__file__).resolve().parents[1];R=O.parent;M=R/'F090_SAME_RAW_SEMANTIC_OWNERSHIP_FIXED_20261019'
g=json.loads((O/'geometry/F094_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json').read_text())
bg=np.asarray(Image.open(O/'anatomy/F094_REFERENCE_BG.png').convert('RGBA'));fg=np.asarray(Image.open(O/'anatomy/F094_REFERENCE_FG_TRUE_FRONT_DIGITS.png').convert('RGBA'))
font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
props=Image.open(O/'code_props/F094_TRUE_CRANE_AND_TWO_PHYSICALLY_RIGID_RODS_REFERENCE.png').convert('RGBA')
base=Image.open(R/'right_hand_lower_rod_inputs_20261019/first034_040/code_props/background_box_cloth_UNCHANGED.png').convert('RGBA');base=base.copy()
# Release only the old pressure fold; current code-crane alpha supplies cloth
# shadow. Static box/room and old actual support shadow are not reconstructed.
k=4;c=Image.new('RGBA',(1920*k,1080*k));cd=ImageDraw.Draw(c);cd.polygon([(int(x*k),int(y*k)) for x,y in [(1010,800),(1850,800),(1838,764),(1022,764)]],fill='#2f4a78')
for j in range(16):
 cx=1050+j*52;cy=784+(j%2)*6
 for xx,yy,rr in [(cx,cy,4),(cx+26,cy-9,2.5)]:cd.ellipse(((xx-rr)*k,(yy-rr)*k,(xx+rr)*k,(yy+rr)*k),fill=(235,235,225,179))
c=c.resize((1920,1080),Image.Resampling.LANCZOS);base.paste(c.crop((1430,780,1560,800)),(1430,780))
shadow=props.getchannel('A').transform((1920,1080),Image.Transform.AFFINE,(1,-.04/.06,795*.04/.06,0,1/.06,800-795/.06),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(3));clip=Image.new('L',(1920,1080));ImageDraw.Draw(clip).polygon([(1010,800),(1850,800),(1838,764),(1022,764)],fill=255);sa=np.uint8(np.asarray(shadow)*.07)*(np.asarray(clip)>0);shade=Image.new('RGBA',(1920,1080),(14,20,30,0));shade.putalpha(Image.fromarray(sa));base.alpha_composite(shade)
base.save(O/'code_props/F094_BOX_CLOTH_UNLOAD_CONTEXT_REFERENCE.png')
def scene(im):return im.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BICUBIC)
ctx=base.copy();ctx.alpha_composite(Image.open(M/'actual_scene/F090_native_ground_shadows_actual_layer.png'));ctx.alpha_composite(scene(Image.fromarray(bg)));ctx.alpha_composite(props);ctx.alpha_composite(scene(Image.fromarray(fg)));ctx.alpha_composite(Image.open(M/'actual_scene/F090_box_front_actual_layer.png'));ctx.save(O/'anatomy/F094_SAME_PERSON_TRUE_PROP_BOX_GROUND_CONTEXT_REFERENCE_ONLY.png');dr=ImageDraw.Draw(ctx);dr.text((18,18),'F094 SAME POSE + TRUE65deg CODE CRANE / PHYSICALLY RIGID RODS / UNLIT REFERENCE ONLY',font=font(22),fill='white');ctx.convert('RGB').save(O/'inputs/02_SAME_F094_TRUE65_PAPER_RODS_BOX_GROUND_CONTEXT.png')
