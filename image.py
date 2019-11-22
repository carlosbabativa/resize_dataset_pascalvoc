import os
import cv2
import numpy as np
from utils import get_file_name
import xml.etree.ElementTree as ET
import traceback
import copy


def process_image(file_path, output_path, w, h, save_box_images,do_crop,do_sub_crop):
    out_size = (w,h)
    (base_dir, file_name, ext) = get_file_name(file_path)
    image_path = '{}/{}.{}'.format(base_dir, file_name, ext)
    xml = '{}/{}.xml'.format(base_dir, file_name)
    if do_crop:
        try:
            crop(
                image_path,
                xml,
                output_path,
                out_w,
                out_h,
                do_sub_crop,
                save_box_images=save_box_images,
            )
        except Exception as e:
            traceback.print_exc()
            print('{}_____{}'.format(image_path,e))
    elif do_sub_crop:
        try:
            subcrop(
                image_path,
                xml,
                output_path,
                w,
                h,
                do_sub_crop,
                save_box_images=save_box_images,
            )
        except Exception as e:
            traceback.print_exc()
            print('{}_____{}'.format(image_path,e))
    else:
        try:
            resize(
                image_path,
                xml,
                tuple(int(dim) for dim in (x, y)),
                output_path,
                save_box_images=save_box_images
            )
        except Exception as e:
            print('[ERROR] error with {}\n file: {}'.format(image_path, e))
            print('--------------------------------------------------')
    
    
        



def draw_box(boxes, image, path):
    for i in range(0, len(boxes)):
        cv2.rectangle(image, (boxes[i][2], boxes[i][3]), (boxes[i][4], boxes[i][5]), (255, 0, 0), 1)
    cv2.imwrite(path, image)


def resize(image_path,
           xml_path,
           newSize,
           output_path,
           save_box_images=False,
           verbose=False):

    image = cv2.imread(image_path)

    scale_x = newSize[0] / image.shape[1]
    scale_y = newSize[1] / image.shape[0]

    image = cv2.resize(image, (newSize[0], newSize[1]))

    newBoxes = []
    xmlRoot = ET.parse(xml_path).getroot()
    xmlRoot.find('filename').text = image_path.split('/')[-1]
    size_node = xmlRoot.find('size')
    size_node.find('width').text = str(newSize[0])
    size_node.find('height').text = str(newSize[1])

    for member in xmlRoot.findall('object'):
        bndbox = member.find('bndbox')

        xmin = bndbox.find('xmin')
        ymin = bndbox.find('ymin')
        xmax = bndbox.find('xmax')
        ymax = bndbox.find('ymax')

        xmin.text = str(np.round(int(xmin.text) * scale_x))
        ymin.text = str(np.round(int(ymin.text) * scale_y))
        xmax.text = str(np.round(int(xmax.text) * scale_x))
        ymax.text = str(np.round(int(ymax.text) * scale_y))

        newBoxes.append([
            1,
            0,
            int(float(xmin.text)),
            int(float(ymin.text)),
            int(float(xmax.text)),
            int(float(ymax.text))
            ])

    (_, file_name, ext) = get_file_name(image_path)
    cv2.imwrite(os.path.join(output_path, '.'.join([file_name, ext])), image)

    tree = ET.ElementTree(xmlRoot)
    tree.write('{}/{}.xml'.format(output_path, file_name, ext))
    if int(save_box_images):
        save_path = '{}/boxes_images/boxed_{}'.format(output_path, ''.join([file_name, '.', ext]))
        draw_box(newBoxes, image, save_path)

def subcrop(image_path,
           xml_path,
           output_path,
           out_w,
           out_h,
           do_sub_crop,
           save_box_images=False,
           verbose=False):
    
    image = cv2.imread(image_path)
    image_name, image_ext = image_path.split('/')[-1].split('.')
    h, w, c = image.shape
    h_times, h_marg = (h//out_h, h%out_h//2)
    w_times, w_marg = (w//out_w, w%out_w//2)
    subs_cnt = h_times * w_times
    sub_imgs = {}

    for r in range(h_times-1):
        for c in range(w_times-1):
            sub_hi, sub_hf = ( h_marg + r*out_h, h_marg + (r+1)*out_h )
            sub_wi, sub_wf = ( w_marg + c*out_w, w_marg + (c+1)*out_w )
            sub_id = w_times*r + c+1
            sub_imgs[r,c] = (image[sub_hi:sub_hf,sub_wi:sub_wf],sub_id,(sub_hi,sub_hf,sub_wi,sub_wf),(r,c))
    
    # new_H, new_W, c = image.shape
    new_H, new_W = (out_h, out_w)

    dx = new_W / w
    dy = new_H / h

    xmlRoot = ET.parse(xml_path).getroot()
    size_node = xmlRoot.find('size')
    orig_w = size_node.find('width')
    orig_h = size_node.find('height')
    size_node.find('width').text = str(new_W)
    size_node.find('height').text = str(new_H)
        
    for image,id,sub_loc,sub_idx in sub_imgs.values():
        shi,shf,swi,swf = sub_loc

        newBoxes = []
        xmlRoot_sub = copy.deepcopy(xmlRoot)
        sub_name = image_name + '_' + str(id) 
        xmlRoot_sub.find('filename').text = sub_name + '.' + image_ext
            
        # old_boxes_cnt = sum([1 for x in enumerate(xmlRoot.findall('object'))])
        for object_node in xmlRoot_sub.findall('object'):
            bndbox = object_node.find('bndbox')
            
            xmin = bndbox.find('xmin')
            ymin = bndbox.find('ymin')
            xmax = bndbox.find('xmax')
            ymax = bndbox.find('ymax')

            xmin_ = int(float(xmin.text))
            ymin_ = int(float(ymin.text))
            xmax_ = int(float(xmax.text))
            ymax_ = int(float(ymax.text))

            lx = xmax_ - xmin_
            ly = ymax_ - ymin_
            # xmax_new = xmin_ + lx
            # ymax_new = ymin_ + ly


            if not any ((xmin_ <= swi, xmax_ >= swf, ymin_ <= shi, ymax_ >= shf)):
                xmin_new = np.round(xmin_ - swi)
                ymin_new = np.round(ymin_ - shi)
                xmin.text = str(xmin_new)
                ymin.text = str(ymin_new)
                xmax_new = xmin_new + lx
                ymax_new = ymin_new + ly
                xmax.text = str(np.round(xmax_new)) 
                ymax.text = str(np.round(ymax_new)) 

                newBoxes.append([
                    1,
                    0,
                    int(float(xmin.text)),
                    int(float(ymin.text)),
                    int(float(xmax.text)),
                    int(float(ymax.text))
                    ])
            else:
                xmlRoot_sub.remove(object_node) # Object would sit outside of cropped section. Delete Box

        cnt_boxes = len(newBoxes)
        # if cnt_boxes != old_boxes_cnt:
        #     print('keeping only {} out of {} for {}'.format(cnt_boxes,old_boxes_cnt,image_name))
        if cnt_boxes > 0:
            # (_, file_name, ext) = get_file_name(image_path)
            cv2.imwrite(os.path.join(output_path, '.'.join([sub_name, image_ext])), image)
            tree = ET.ElementTree(xmlRoot_sub)
            tree.write('{}/{}.xml'.format(output_path, sub_name))
        if int(save_box_images and cnt_boxes > 0):
            save_path = '{}/boxes_images/boxed_{}'.format(output_path, ''.join([sub_name, '.', image_ext]))
            draw_box(newBoxes, image, save_path)


# _________________________________CUSTOM___________________________________________________________________
def crop(image_path,
           xml_path,
           output_path,
           out_w,
           out_h,
           do_sub_crop,
           save_box_images=False,
           verbose=False):
    # if margins is None:
    #     margins = (0.2847,0.0,0.1424,0.1424)
    
                


    if out_size is not None:
        ow, oh = out_size
        dlw, dlh = ((w-ow),(h-oh))
        dw, dh = (dlw/w,dlh/h)
        margins = (dh*.8,dh*.2,dw*.5,dw*.5)
    
    ht, hb, wl, wr = margins    
    mt, mb, ml, mr = [int(round(dim,0)) for dim in (ht*h, hb*h, wl*w, wr*w)]
    
    orig_img = image.copy()
    image = orig_img[mt:h-mb,ml:w-mr,:].copy()
    # print('new image shape: '+str(image.shape))
    new_H, new_W, c = image.shape
    
    dx = new_W / w
    dy = new_H / h

    newBoxes = []
    xmlRoot = ET.parse(xml_path).getroot()
    xmlRoot.find('filename').text = image_name
    size_node = xmlRoot.find('size')
    orig_w = size_node.find('width')
    orig_h = size_node.find('height')
    size_node.find('width').text = str(new_W)
    size_node.find('height').text = str(new_H)
    old_boxes_cnt = sum([1 for x in enumerate(xmlRoot.findall('object'))])
    for object_node in xmlRoot.findall('object'):
        bndbox = object_node.find('bndbox')

        xmin = bndbox.find('xmin')
        ymin = bndbox.find('ymin')
        xmax = bndbox.find('xmax')
        ymax = bndbox.find('ymax')

        xmin_ = int(float(xmin.text))
        ymin_ = int(float(ymin.text))
        xmax_ = int(float(xmax.text))
        ymax_ = int(float(ymax.text))

        lx = xmax_ - xmin_
        ly = ymax_ - ymin_
        xmax_new = xmin_ + lx
        ymax_new = ymin_ + ly


        if not any ((xmin_ <= ml, xmax_ >= w-mr, ymin_ <= mt, ymax_ >= h-mb)):
            xmin_new = np.round(xmin_ - ml)
            ymin_new = np.round(ymin_ - mt)
            xmin.text = str(xmin_new)
            ymin.text = str(ymin_new)
            xmax_new = xmin_new + lx
            ymax_new = ymin_new + ly
            xmax.text = str(np.round(xmax_new)) if xmax_new <= w-mr else str(w-mr)
            ymax.text = str(np.round(ymax_new)) if ymax_new <= h-mb else str(h-mb)

            newBoxes.append([
                1,
                0,
                int(float(xmin.text)),
                int(float(ymin.text)),
                int(float(xmax.text)),
                int(float(ymax.text))
                ])
        else:
            xmlRoot.remove(object_node) # Object would sit outside of cropped section. Delete Box

    cnt_boxes = len(newBoxes)
    if cnt_boxes != old_boxes_cnt:
        print('keeping only {} out of {} for {}'.format(cnt_boxes,old_boxes_cnt,image_name))
    if cnt_boxes > 0:
        (_, file_name, ext) = get_file_name(image_path)
        cv2.imwrite(os.path.join(output_path, '.'.join([file_name, ext])), image)
        tree = ET.ElementTree(xmlRoot)
        tree.write('{}/{}.xml'.format(output_path, file_name, ext))
    if int(save_box_images and cnt_boxes > 0):
        save_path = '{}/boxes_images/boxed_{}'.format(output_path, ''.join([file_name, '.', ext]))
        draw_box(newBoxes, image, save_path)

# -----------------------------------------------------------------------------------------------------------------------------------
