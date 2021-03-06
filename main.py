# This Python file uses the following encoding: utf-8
import os
import os.path as ops
import numpy as np
import random
import cv2
import argparse
from PIL import Image, ImageFilter, ImageEnhance, ImageStat

from multiprocessing import Pool
import shutil
class Config:
    list = [(200,90),(110,20),(160,60),(260,160)]

    @classmethod
    def getOne(cls):
        return cls.list[random.randrange(0,len(cls.list))]

    @classmethod
    def getTest(cls):
        return (260,160)

def init_file(img_path):
    files = os.listdir(img_path)
    files_arr=[]
    for file_name in files:
        full_name = ops.join(img_path,file_name)
        if ops.isfile(full_name):
            if full_name.split('.')[-1].lower() == 'jpg' or full_name.split('.')[-1].lower() == 'png':
                files_arr.append(full_name)
    files_arr.sort()
    return files_arr

# 把所有的素材读进来,返回所选的路径
def read_material(pic_path):
    dir_list = []
    for file in os.listdir(pic_path):
        dir_list.append(file)
    # print(dir_list)
    pics = {}
    for the_dir in dir_list:
        pics[the_dir]=init_file(ops.join(pic_path,str(the_dir)))
    return pics

def get_one_number(the_dict, character):
    length = len(the_dict[character])
    return the_dict[character][random.randrange(0,length)]

def text_generate(text, dict, width, height, bright_setting = 200):
    length=len(text)
    image = Image.new('RGBA',(width*length,height),(0,0,0,0))
    image_mask = Image.new('1',(width*length,height),(0))
    addition = 0
    # np.set_printoptions(threshold=1000000)
    for character in text:
        pic = Image.open(get_one_number(dict,character))
        pic.rotate(random.randint(-5,5),expand=1)
        image_width, _ = pic.size

        # 如果太小,拉伸图像
        # if pic.size[0] < width:
        #     pic = pic.resize([width, int(pic.size[1]*(width/pic.size[0]))],Image.ANTIALIAS)
        # elif pic.size[1] < height:
        #     pic.thumbnail([int(pic.size[0]*(height/pic.size[1])),height], Image.ANTIALIAS)
        _,_,_,alpha = pic.split()
        pic_b = ImageEnhance.Brightness(pic)
        stat = ImageStat.Stat(pic,mask = alpha)
        brightness = bright_setting/(stat.mean[0]+20)
        # print(brightness)
        pic = pic_b.enhance(brightness)
        # additions = (addition,0)
        additions = (addition+random.randrange(-2,2),random.randrange(-2,2))
        image.paste(pic,additions,mask=alpha)
        image_mask.paste(pic,additions,mask=alpha)
        addition = addition + image_width + 10
    image = image.crop([0,0,addition+12,image.height])
    image_mask = image_mask.crop([0,0,addition+12,image.height])
    return image,image_mask

def get_one_file(file_arr):
    return file_arr[random.randint(0,len(file_arr)-1)]

def background_generate(width, height, bright_setting):
    pictures = init_file('./background')
    if len(pictures)>0:
        picture = Image.open(get_one_file(pictures))
        x = random.randint(0, picture.size[0] - width)
        y = random.randint(0, picture.size[1] - height)            
        croped = picture.crop(
            (
                x,
                y,
                x + width,
                y + height,
            )
        )
        stat = ImageStat.Stat(croped)
        pic_b = ImageEnhance.Brightness(croped)
        brightness = bright_setting / (stat.mean[0]+20)
        # print(brightness)
        croped = pic_b.enhance(brightness)
        return croped

def disorted_generate(src):
    return src

def generate(out_dir,index,text,skewing_angle=1,width=49,height=59,blur=0):
    # print(out_dir)
    the_dict = read_material('./pics')
    bright_settings = Config.getOne()
    image,image_mask = text_generate(str(text),the_dict,width,height,bright_settings[0])
    # 创建图片
    random_angle = random.randint(-skewing_angle,skewing_angle)
    # 旋转
    rotated_img = image.rotate(random_angle)
    # 扭曲
    disorted_img = disorted_generate(rotated_img)
    new_text_width, new_text_height = disorted_img.size
    # 背景图片
    background = background_generate(new_text_width+10,new_text_height+10,bright_settings[1])
    margin = (10,20,8,10)  # 左右上下      
    # print(disorted_img.mode)
    # mask = disorted_img.point(lambda x: 0 if x == 255 or x == 0 else 255, 'RGBA')
    # background.paste(disorted_img,(margin[0],margin[2]),mask=mask)
    background.paste(disorted_img,(margin[0],margin[2]),mask=image_mask)
    # 重新调整图像大小 
    new_width = float(new_text_width + margin[1] + margin[0]) * (float(height) / float(new_text_height + margin[2]+ margin[3]))
    image_on_background = background.resize((int(new_width),height), Image.ANTIALIAS)
    final_image = image_on_background.filter(ImageFilter.GaussianBlur(blur))
    # final_image = final_image.filter(ImageFilter.EMBOSS)
    # 生成名称     
    image_name  = '{}_{}.{}'.format(text, str(index), 'jpg')
    final_image = final_image.convert('RGB')
    # print(final_image.mode)
    final_image.save(ops.join(out_dir,image_name))
    return final_image

def simple_generate(out_dir):
    return generate(out_dir,str(random.randint(0,100000000)),str(random.randint(0,100000000)))

def run(thread_count,number,out_dir,repeat_number):
    p=Pool(thread_count)
    for _ in range(number):
        p.apply_async(simple_generate,[out_dir])
    p.close()
    p.join()
    add_real_pic(out_dir,repeat_number)

def add_real_pic(out_dir,repeat_number):
    # 把原图放进去.首先要重命名
    if not os.path.isdir('./real_out'):
        os.makedirs('./real_out')
    real_files = init_file('./real')
    for _ in range(repeat_number):
        for file in real_files:
            img = Image.open(file)
            file_name = file.split('/')[-1]
            text = file_name.split('.')[0]
            img.save(ops.join(out_dir,text+'_'+str(random.randint(0,100000000))+'.jpg'))


def write_file(out_dir):
    # 写文件
    f = open(os.path.join('./', 'sample.txt'),'w')
    files = init_file(out_dir)
    # print(files)
    for file in files:
        file_name = file.split('/')[-1]
        text = file_name.split('.')[0].split('_')[0]
        f.write("{} {}\n".format('./'+file_name,text))
    f.close()

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate synthetic text data for text recognition.')
    parser.add_argument(
        "output_dir",
        type=str,
        nargs="?",
        help="The output directory",
        default="./out",
    )
    parser.add_argument(
        "-t",
        "--thread_count",
        type=int,
        nargs="?",
        help="Define the number of thread to use for image generation",
        default=8,
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        nargs="?",
        help="The number of images to be created.",
        default=100
    )
    parser.add_argument(
        "-r",
        "--repeat_number",
        type=int,
        nargs="?",
        help="The number of real images repeat.",
        default=2
    )
    return parser.parse_args()

def main(): 
    # generate('./out',1,1245231415)
    print("first, start to generate pictures.")
    args = parse_arguments()
    if os.path.isdir(args.output_dir):
        shutil.rmtree(args.output_dir,True)
    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)
    run(args.thread_count,args.count,args.output_dir,args.repeat_number)    
    # 写文件
    write_file(args.output_dir)
    
if __name__ == '__main__':
    main()