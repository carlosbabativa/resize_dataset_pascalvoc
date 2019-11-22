import cv2
import os

'Darkflow\'s yolo.resize_input(self,im)'
def resize_input(im,rsz):
	w, h = rsz
	imsz = cv2.resize(im, (w, h))
	# imsz = imsz / 255.
	# imsz = imsz[:,:,:]
	return imsz

# imgdir=input('path: ')
imgdir = 'snail-grain/out'

sub_ls = list(filter(lambda x: '.jpg' in x,os.listdir(imgdir)[:-1]))

imgs = [cv2.imread(os.path.join(imgdir,sub)) for sub in sub_ls]
# w_, h_ ,c= imgs[0].shape
w,h = (416,416)
yolo_sqz = (w,h)

# what = resize_inpcut(imgs[0],yolo_sqz)
ww,hh = (832,832)
new_sz = (ww,hh)

ww,hh = (1248,1248)
lg_sz = (ww,hh)

# imgs_416 = [resize_input(img,yolo_sqz) for img in imgs]
# imgs_832 = [resize_input(img,new_sz) for img in imgs]
imgs_1248 = [resize_input(img,lg_sz) for img in imgs]
# outdir_sm = imgdir+'/yolov2_416'
# outdir_md = imgdir+'/yolov2_832'
outdir_lg = imgdir+'/yolov2_1248'
for out in [outdir_lg]:
	if not os.path.exists(out):
		os.mkdir(out)

# [cv2.imwrite(outdir_sm+'/'+name,img) for name, img in zip(sub_ls, imgs_416)]
# [cv2.imwrite(outdir_md+'/'+name,img) for name, img in zip(sub_ls, imgs_832)]
[cv2.imwrite(outdir_lg+'/'+name,img) for name, img in zip(sub_ls, imgs_1248)]
