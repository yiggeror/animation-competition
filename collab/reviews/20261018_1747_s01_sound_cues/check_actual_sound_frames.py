from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,numpy as np,json,hashlib
D=Path(__file__).resolve().parent;R=D.parent;V=R/'astra_s01_contact_actual_20261018_1727/S01_contact_full84.mp4';raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(V),'-f','rawvideo','-pix_fmt','rgb24','-']);arr=np.frombuffer(raw,np.uint8).reshape(-1,720,1280,3);assert len(arr)==84;F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);box=(640,438,711,512);selected=[11,12,28,33,34,35];eq={}
for f in selected:
 im=Image.fromarray(arr[f]);im.save(D/f'actual_F{f:03d}.png');prior=np.array(Image.open(R/f'astra_independent_contact_color_20261018_1733/S01/F{f:03d}.png').convert('RGB'));eq[f]=bool(np.array_equal(arr[f],prior));c=im.crop(box);enlarge=c.resize((c.width*8,c.height*8),Image.Resampling.NEAREST);panel=Image.new('RGB',(568,660),'white');panel.paste(enlarge,(0,36));dr=ImageDraw.Draw(panel);dr.text((8,8),f'Actual F{f:03d} / {f}/24 = {f/24:.6f}s',font=F,fill='black');dr.text((8,632),'8x nearest / original brightness and color',font=F,fill='black');panel.save(D/f'evidence_F{f:03d}_hand_basin_8x.png')
# Internal neighboring checks: full decode, not inferred from filenames.
sheet=Image.new('RGB',(6*284,350),'white');dr=ImageDraw.Draw(sheet)
for j,f in enumerate([28,29,30,33,34,35]):
 c=Image.fromarray(arr[f]).crop(box).resize((284,296),Image.Resampling.NEAREST);sheet.paste(c,(j*284,28));dr.text((j*284+5,5),f'F{f:03d} {f/24:.4f}s',font=F,fill='black')
sheet.save(D/'release_and_landing_actual_check.jpg',quality=100)
(D/'DECODE_CHECK.json').write_text(json.dumps({'video_path':str(V),'sha256':hashlib.sha256(V.read_bytes()).hexdigest(),'decoded_frames':len(arr),'fps':24,'zero_based':True,'actual_evidence_frames':selected,'matches_prior_independent_decode':eq,'crop_original_pixel_box':box,'enlargement':'nearest 8x, no brightness/color modification'},indent=2));print(json.dumps(eq))
