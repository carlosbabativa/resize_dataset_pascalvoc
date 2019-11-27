import os
import argparse
from image import process_image
from utils import create_path, add_end_slash
from optparse import OptionParser
###
#Work within the data directory
###
os.chdir('data')


#pass arguments
parser = argparse.ArgumentParser()

parser.add_argument(
    '-p',
    '--path',
    dest='dataset_path',
    help='Path to dataset data ?(image and annotations).',
    required=True
)
parser.add_argument(
    '-o',
    '--output',
    dest='output_path',
    help='Path that will be saved the resized dataset',
    default='./',
    required=True
)
parser.add_argument(
    '-w',
    '--new_w',
    dest='w',
    help='The new x images size',
    required=True
)
parser.add_argument(
    '-hh',
    '--new_h',
    dest='h',
    help='The new y images size',
    required=True
)
parser.add_argument(
    '-s',
    '--save_box_images',
    dest='save_box_images',
    help='If True, it will save the resized image and a drawed image with the boxes in the images',
    default=0
)
parser.add_argument(
    '-c',
    '--do_crop',
    dest='do_crop',
    help='If True, it will crop',
    default=0
)
parser.add_argument(
    '-sc',
    '--do_sub_crop',
    dest='do_sub_crop',
    help='If True, it will sub-crop',
    default=0
)
# parser.add_argument(
#     '-z',
#     '--out_size',
#     dest='out_size',
#     help='Final cropped Output Size',
#     default=(1664,1664)
# )
# parser.add_argument(
#     '-m',
#     '--margins',
#     dest='margins',
#     help='...',
#     default=None
# )
IMAGE_FORMATS = ('.jpeg', '.JPEG', '.png', '.PNG', '.jpg', '.JPG')

args = parser.parse_args()

args.dataset_path += '/data_train'
args.output_path += '/data_train'
create_path(args.output_path)
create_path(''.join([args.output_path, '/boxes_images']))

args.dataset_path = add_end_slash(args.dataset_path)
args.output_path = add_end_slash(args.output_path)
assert os.path.exists(args.dataset_path), 'All data (images and annotations) should be within a folder named \'data_train\''

for root, _, files in os.walk(args.dataset_path):
        output_path = os.path.join(args.output_path, root[len(args.dataset_path):])
        create_path(output_path)

        for file in files:
            if file.endswith(IMAGE_FORMATS):
                file_path = os.path.join(root, file)
                process_image(file_path, output_path, int(args.w),int(args.h), args.save_box_images,args.do_crop,args.do_sub_crop)
