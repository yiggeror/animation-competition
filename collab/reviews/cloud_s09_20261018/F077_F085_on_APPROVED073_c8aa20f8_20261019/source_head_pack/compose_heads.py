from pathlib import Path
from PIL import Image
import argparse
p=argparse.ArgumentParser();p.add_argument('approved073_body');p.add_argument('output_directory');a=p.parse_args()
r=Path(__file__).resolve().parent;o=Path(a.output_directory);o.mkdir(parents=True,exist_ok=True)
b=Image.open(a.approved073_body).convert('RGBA');assert b.size==(1672,941)
for n in ('077','085'):
 s=Image.open(r/f'F{n}_registered_source.png').convert('RGBA');m=Image.open(r/f'F{n}_whole_head_neck_mask.png').convert('L')
 Image.composite(s,b,m).save(o/f'F{n}_final073_body.png')
