# Source-pixel anatomy reference math only. Never production person art.
def uv(v):return v/(np.linalg.norm(v) or 1)
def normal(v):
 v=uv(v);return np.array([-v[1],v[0]])
def rigid(im,mat):
 A=np.array(mat)[:,:2];t=np.array(mat)[:,2];iv=np.linalg.inv(A);q=-iv@t;return im.transform(OUT,Image.Transform.AFFINE,tuple(iv[0])+(q[0],)+tuple(iv[1])+(q[1],),Image.Resampling.BICUBIC)
def warp_arm(a,S0,E0,W0,St,Et,Wt,mat,far=False):
 S0,E0,W0,St,Et,Wt=map(lambda x:np.array(x,float),[S0,E0,W0,St,Et,Wt]);A=np.array(mat)[:,:2];t=np.array(mat)[:,2];handv=uv(np.array([975.7142857,957.3802078])-W0)if far else uv(np.array([820.,986.])-W0);hu=uv(E0-S0);ht=uv(Et-St)
 sc=[S0-hu*90,S0,S0+.65*(E0-S0),E0,E0+.55*(W0-E0),W0-uv(W0-E0)*45,W0+handv*5]
 tc=[St-ht*90,St,St+.65*(Et-St),Et,Et+.55*(Wt-Et),Wt-uv(Wt-Et)*45*np.linalg.norm(Wt-Et)/np.linalg.norm(W0-E0),A@sc[6]+t]
 sn=[normal(E0-S0)]*3+[normal(uv(E0-S0)+uv(W0-E0)),normal(W0-E0),normal(W0-E0),normal(handv)]
 tn=[normal(Et-St)]*3+[normal(uv(Et-St)+uv(Wt-Et)),normal(Wt-Et),normal(Wt-Et),A@sn[6]]
 widths=([85,90,70,48,34,29,29]if far else[110,110,80,66,43,33,33]);src=[];dst=[]
 for c,z,n,q,w in zip(sc,tc,sn,tn,widths):
  for sign in [-1,0,1]:src.append(c+sign*n*w);dst.append(z+sign*q*w)
 src=np.array(src);dst=np.array(dst);tri=Delaunay(dst);y,x=np.mgrid[:H,:W];along=(x-W0[0])*handv[0]+(y-W0[1])*handv[1];threshold=-8 if far else -12;arm=a.copy();hand=a.copy();arm[along>=threshold+10]=0;hand[along<threshold]=0
 if far:
  jade=(a[:,:,1].astype(int)>a[:,:,0].astype(int)+15)&(a[:,:,1].astype(int)>a[:,:,2].astype(int)+5)&(a[:,:,3]>0)&(x>=842)&(x<900)&(y>=884)&(y<960);jade=binary_dilation(jade,iterations=3)
  hand[jade]=0;arm[jade]=a[jade]
 xmin=max(0,int(dst[:,0].min()-3));xmax=min(OUT[0],int(dst[:,0].max()+4));ymin=max(0,int(dst[:,1].min()-3));ymax=min(OUT[1],int(dst[:,1].max()+4));oy,ox=np.mgrid[ymin:ymax,xmin:xmax];pts=np.column_stack([ox.ravel(),oy.ravel()]);si=tri.find_simplex(pts);ok=si>=0;valid=pts[ok];ii=si[ok];bb=np.einsum('nij,nj->ni',tri.transform[ii,:2],valid-tri.transform[ii,2]);bb=np.column_stack([bb,1-bb.sum(axis=1)]);coords=np.einsum('ni,nij->nj',bb,src[tri.simplices[ii]])
 aa=arm.astype(float)/255;aa[:,:,:3]*=aa[:,:,3:4];vals=np.column_stack([map_coordinates(aa[:,:,k],[coords[:,1],coords[:,0]],order=1,mode='constant')for k in range(4)]);good=vals[:,3]>0;vals[good,:3]/=vals[good,3:4];res=np.zeros((OUT[1],OUT[0],4),np.uint8);res[valid[:,1],valid[:,0]]=np.uint8(np.clip(vals*255+.5,0,255));im=Image.fromarray(res,'RGBA');handim=rigid(Image.fromarray(hand,'RGBA'),mat);im=Image.alpha_composite(im,handim);return im,{'source_control_vertices':src.tolist(),'target_control_vertices':dst.tolist(),'distal_hand_rigid_matrix':mat,'hand_scale':1.0,'mirrored':False,'reference_only_not_drawing':True}
def plate(im):return im.transform((1024,1024),Image.Transform.AFFINE,(1/1.12,0,294.4/1.12,0,1/1.12,473.6/1.12),Image.Resampling.NEAREST)
def scene(im):return im.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BICUBIC)
