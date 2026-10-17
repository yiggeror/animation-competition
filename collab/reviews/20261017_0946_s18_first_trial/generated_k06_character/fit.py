from PIL import Image,ImageFilter,ImageDraw,ImageFont
from pathlib import Path
import numpy as np,json,math
from scipy.ndimage import sobel
out=Path('/tmp/laidian-s18-pilot-audit/generated_k06_character');root=Path('/workspace/animation-competition')
a=Image.open(root/'assets/chars/x18_laugh.png').convert('RGB'); b=Image.open(out/'evidence/candidate_nominal_gray.png').convert('RGB')
def grad(im):
    z=np.asarray(im.convert('L'),float);return np.minimum(np.hypot(sobel(z,axis=0),sobel(z,axis=1)),300)
g1,g2=grad(a),grad(b)
anchors={'A_seat':[22,899],'B_rightfoot':[312,1142],'C_leftfoot':[22,1142],'D_topseat':[22,858],'E_barcorner':[77,1015]}
items=[]
for name,(x,y) in anchors.items():
    r=12 if x<30 else 16;tmp=g1[y-r:y+r+1,x-r:x+r+1];tmp=tmp-tmp.mean();n=np.linalg.norm(tmp);best=(-1,0,0)
    for dy in range(-35,21):
      for dx in range(-15,16):
        xx,yy=x+dx,y+dy
        if xx-r<0 or yy-r<0 or xx+r>=635 or yy+r>=1175:continue
        sub=g2[yy-r:yy+r+1,xx-r:xx+r+1];sub=sub-sub.mean();score=float((tmp*sub).sum()/(n*np.linalg.norm(sub)+1e-9))
        if score>best[0]:best=(score,dx,dy)
    items.append({'name':name,'source':[x,y],'candidate_nominal':[x+best[1],y+best[2]],'score':best[0]})
# Fit only A and B, leave C and other edges independent validation.
src=np.array([v['source'] for v in items[:2]],float);cand=np.array([v['candidate_nominal'] for v in items[:2]],float)
u=src[1]-src[0];v=cand[1]-cand[0];ar=np.dot(u,v)/np.dot(v,v);br=(u[1]*v[0]-u[0]*v[1])/np.dot(v,v);M=np.array([[ar,-br],[br,ar]]);t=src[0]-M@cand[0]
for q in items:q['registered']=(M@np.array(q['candidate_nominal'])+t).tolist();q['residual_px']=float(np.linalg.norm(np.array(q['registered'])-q['source']))
scale=(922/635+1706/1175)/2; Mn=M/scale;inv=np.linalg.inv(Mn);offset=-inv@t;coeffs=(*inv[0],offset[0],*inv[1],offset[1]);raw=Image.open('/tmp/laidian-s18-pilot-candidate/generated_k06_v1/x18_k06_candidate.png').convert('RGBA');fit=raw.transform(a.size,Image.Transform.AFFINE,coeffs,Image.Resampling.BICUBIC)
bg=Image.new('RGBA',a.size,(220,220,220,255));bg.alpha_composite(fit);fitrgb=bg.convert('RGB');fitrgb.save(out/'evidence/candidate_stool_registered_gray.png')
font=ImageFont.truetype(str(root/'assets/fonts/NotoSansSC-VF.ttf'),18)
for name,box in [('full',(0,0,635,1175)),('head',(35,70,465,490)),('dress',(90,440,550,950)),('stool_shoes',(0,820,635,1175))]:
    x1=a.crop(box);x2=fitrgb.crop(box);w,h=x1.size;im=Image.new('RGB',(w*2,h+35),'white');d=ImageDraw.Draw(im);im.paste(x1,(0,35));im.paste(x2,(w,35));d.text((5,6),'母版',font=font,fill='black');d.text((w+5,6),'新 k06（仅按木凳相似配准）',font=font,fill='black');im.save(out/'evidence'/f'{name}_registered_pair.png')
# edge overlay: source magenta, generated cyan, coincident dark.
ea=grad(a);eb=grad(fitrgb);z=np.full((1175,635,3),255,np.uint8);ma=ea>95;mb=eb>95;z[ma]=[200,35,155];z[mb]=[0,170,190];z[ma&mb]=[30,30,30];Image.fromarray(z).save(out/'evidence/registered_edges.png')
# local best translations after globally fixed stool alignment, for static-region shape checking.
ga=grad(a);ngb=grad(fitrgb);regions={'hair_bangs':[115,95,360,205],'ear':[158,278,243,365],'white_collar':[218,414,327,473],'bodice_dots':[180,467,285,570],'lower_skirt':[115,756,345,861],'near_shoe':[397,1065,576,1155],'far_hand':[438,701,527,765]}
regionres=[]
for name,(x0,y0,x1,y1) in regions.items():
    tmp=ga[y0:y1,x0:x1];tmp=tmp-tmp.mean();nn=np.linalg.norm(tmp);best=(-1,0,0)
    for dy in range(-28,29):
      for dx in range(-15,16):
        if x0+dx<0 or y0+dy<0 or x1+dx>635 or y1+dy>1175:continue
        sub=ngb[y0+dy:y1+dy,x0+dx:x1+dx];sub=sub-sub.mean();score=float((tmp*sub).sum()/(nn*np.linalg.norm(sub)+1e-9))
        if score>best[0]:best=(score,dx,dy)
    regionres.append({'name':name,'box':regions[name],'best_candidate_offset_from_master':[best[1],best[2]],'edge_corr':best[0],'note':'Diagnostic local correlation; not another applied transform or proof of identity.'})
res={'method':'Local gradient-NCC landmarks (integer nominal source scale), global 2-point similarity fitted only A/B; C/D/E held out. Original images unchanged.','nominal_native_scale':scale,'anchor_matches':items,'candidate_native_to_master_matrix':Mn.tolist(),'translation':t.tolist(),'local_scale_from_nominal':float(math.hypot(ar,br)),'rotation_deg':math.degrees(math.atan2(br,ar)),'static_region_residual_search':regionres}
(out/'registration_measurements.json').write_text(json.dumps(res,ensure_ascii=False,indent=2));print(json.dumps(res,ensure_ascii=False,indent=2))
