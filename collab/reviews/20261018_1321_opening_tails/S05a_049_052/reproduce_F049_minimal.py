"""Reproduce accepted F049 from its saved scaffold, call09 raw and explicit mask."""
from pathlib import Path
from PIL import Image
import hashlib
R=Path(__file__).resolve().parent;O=R/'verification_replay';O.mkdir(exist_ok=True)
base=Image.open(R/'inputs/F049_from_locked_pose_scaffold.png').convert('RGBA');raw=Image.open(R/'raw/call09_F049_mass_release.png').convert('RGBA');layer=base.copy();layer.paste(raw.resize((430,415),Image.Resampling.LANCZOS),(620,420));mask=Image.open(R/'masks/F049_release_exhale_mask.png').convert('L');out=Image.composite(layer,base,mask);out.putalpha(base.getchannel('A'));p=O/'S05a_F049.png';out.save(p);h=hashlib.sha256(p.read_bytes()).hexdigest();assert h=='9aecf498cb5ddb24198d4a7029446b48797487a81a3b86da1c42967e222e0410';print(h)
