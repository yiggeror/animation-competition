"""Review annotation only; never modifies registered native pixels or geometry."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent
g=json.loads((R/'geometry/ONE_SIMILARITY_AND_SOURCE_CHECKS.json').read_text())
im=Image.open(R/'candidate/F036_SINGLE_SIMILARITY_NATIVE_ARM_AND_LIP_TRIAL.png').convert('RGBA')
bg=Image.new('RGBA',im.size,(237,240,242,255));bg.alpha_composite(im)
box=(470,420,840,735);zoom=2
pic=bg.convert('RGB').crop(box).resize((740,630),Image.Resampling.NEAREST)
d=ImageDraw.Draw(pic);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
def p(v):return ((v[0]-box[0])*zoom,(v[1]-box[1])*zoom)
targets=g['target_soft_anchors'];actual=g['mapped_anchors']
for i,(t,a,res) in enumerate(zip(targets,actual,g['residuals_native_px'])):
 tx,ty=p(t);ax,ay=p(a)
 d.line([(tx,ty),(ax,ay)],fill='#dd4b32',width=3)
 d.ellipse((tx-6,ty-6,tx+6,ty+6),outline='#27966b',width=2)
 d.ellipse((ax-5,ay-5,ax+5,ay+5),outline='#dd4b32',width=2)
 d.text((max(0,min(ax+8,530)),max(2,ay-25)),f'{i+1}: {res:.1f}px',font=font,fill='#b52e19')
ox,oy=p([731,673]);d.line([(ox,oy-30),(ox,oy+30)],fill='#244ca2',width=2)
card=Image.new('RGB',(780,735),'#edf0f2');c=ImageDraw.Draw(card)
c.text((20,10),'ONE SIMILARITY: ACTUAL CUFF + CURRENT PINCH',font=font,fill='#23364d')
c.text((20,36),'Green = soft anchor; red = mapped raw; blue =030 pinch x',font=font,fill='#23364d')
card.paste(pic,(20,75));card.save(R/'qa/DUAL_ANCHOR_RESIDUALS_REVIEW_ONLY.png')
print('residual review annotation saved; candidate unchanged')
