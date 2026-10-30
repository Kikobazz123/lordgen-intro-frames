import numpy as np, json
from PIL import Image, ImageFilter
U='../source/'
# ---- city plate: extend sky upward by 360px, upscale 2x
c=Image.open(U+'city.jpg').convert('RGB'); W,H=c.size; EXT=360
top=np.array(c.crop((0,0,W,90)).filter(ImageFilter.GaussianBlur(70))).astype(float)
ext=np.zeros((EXT,W,3))
for y in range(EXT):
    k=(EXT-y)/EXT
    row=top[int(min(89,max(0,(1-k)*40)))]
    ext[y]=row*(1-0.28*k)+np.array([70,62,80])*0.28*k  # darker violet zenith
rng=np.random.default_rng(3)
n=np.array(Image.fromarray((rng.random((EXT//30,W//60))*255).astype(np.uint8)).resize((W,EXT),Image.BICUBIC).filter(ImageFilter.GaussianBlur(25))).astype(float)/255
ext+= (n[...,None]-0.5)*40*np.array([1.0,0.8,0.9])
full=np.vstack([np.clip(ext,0,255),np.array(c).astype(float)])
# blend seam
for i in range(40):
    a=i/40; full[EXT+i]=full[EXT+i]*a+full[EXT-1]*(1-a)
full=np.clip(full,0,255)
# brand grade: shadows->green, highlights->gold/cream
G=np.array([14,59,46.]); Au=np.array([169,132,58.]); Cr=np.array([250,240,215.])
L=(full@[0.299,0.587,0.114])/255.0
sh=np.clip(1-L*1.8,0,1)[...,None]; hi=np.clip((L-0.55)/0.45,0,1)[...,None]
gr=full*(1-0.55*sh)+G*1.6*0.55*sh
gr=gr*(1-0.35*hi)+ (Au*0.5+Cr*0.5)*0.35*hi
gr=gr*1.03
for name,arr in [('plate',full),('plate_g',gr)]:
    im=Image.fromarray(np.clip(arr,0,255).astype(np.uint8)).resize((W*2,(H+EXT)*2),Image.LANCZOS)
    im=im.filter(ImageFilter.UnsharpMask(2,60,2))
    im.save(f'assets/{name}.jpg',quality=94)
    im.filter(ImageFilter.GaussianBlur(6)).save(f'assets/{name}_b1.jpg',quality=92)
    im.filter(ImageFilter.GaussianBlur(18)).save(f'assets/{name}_b2.jpg',quality=92)
# ---- owl: warm grade + gold rim from left
o=np.array(Image.open('assets/owl_cut.png').convert('RGBA')).astype(float)
a=o[...,3]/255
rgb=o[...,:3]*np.array([1.0,0.95,0.88])
xs=np.linspace(0,1,o.shape[1])[None,:,None]; rgb=rgb*(1-0.22*xs)  # falloff to right
sh=np.roll(a,10,axis=1); sh[:, :10]=0
edge=np.clip(a-sh,0,1); edge=np.array(Image.fromarray((edge*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))).astype(float)/255
rgb=rgb+edge[...,None]*np.array([255,190,90])*0.9
out=np.dstack([np.clip(rgb,0,255),o[...,3]]).astype(np.uint8)
Image.fromarray(out).save('assets/owl_lit.png')
# ---- logo pieces
lg=Image.open(U+'logo.png').convert('RGB'); la=np.array(lg).astype(int)
ink=(np.abs(la-[250,247,239]).sum(2)>60)
rgba=np.dstack([la,(ink*255)]).astype(np.uint8)
# alpha with antialias
d=np.abs(la-[250,247,239]).sum(2); alpha=np.clip(d/140*255,0,255).astype(np.uint8)
rgba[...,3]=alpha
Image.fromarray(rgba).save('assets/logo_rgba.png')
gold=(np.abs(la-[169,132,58]).sum(2)<90)&ink
gm=np.zeros_like(rgba); gm[...,3]=(gold*alpha).astype(np.uint8); gm[...,:3]=255
Image.fromarray(gm).save('assets/logo_goldmask.png')
# ---- particles
rng=np.random.default_rng(7); N=7000
oa=o[...,3]>200; oy,ox=np.where(oa); idx=rng.choice(len(oy),N,replace=False)
src=np.stack([ox[idx],oy[idx]],1).astype(float); scol=o[oy[idx],ox[idx],:3]
my,mx=np.where(ink[396:1370,700:1460]); my=my+396; mx=mx+700
idx2=rng.choice(len(my),N,replace=False)
dst=np.stack([mx[idx2],my[idx2]],1).astype(float); dcol=la[my[idx2],mx[idx2]]
# coherent matching: sort by angle around eye-mid then radius bands
def key(p,c,s):
    v=(p-c)/s; ang=np.arctan2(v[:,1],v[:,0]); r=np.hypot(*v.T)
    return np.lexsort((ang,np.floor(r*14)))
ks=key(src,np.array([362,163]),300); kd=key(dst,np.array([1079,760]),600)
P=[]
for i in range(N):
    a_=ks[i]; b_=kd[i]
    P+= [round(src[a_,0],1),round(src[a_,1],1),round(dst[b_,0],1),round(dst[b_,1],1),
         *map(int,scol[a_]),*map(int,dcol[b_]), round(float(rng.random()),3)]
json.dump(P,open('assets/particles.json','w'))
print('ok')
