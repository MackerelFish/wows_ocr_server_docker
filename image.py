import cv2
import numpy as np
import requests
import threading
import json
import time
import get_Hash
import random
import os
from multiprocessing.dummy import Pool as ThreadPool

config = json.load(open('./config.json', 'r', encoding='utf8'))
img_size_max = config['img_size_max'].split(',')
img_size_min = config['img_size_min'].split(',')
img_aim_long = int(config['img_aim_long'])
img_path = '/save/'
if not os.path.exists(img_path):
    os.mkdir(img_path)
if not os.path.exists(img_path+"recent/"):
    os.mkdir(img_path+"recent/")
if not os.path.exists(img_path+"ship/"):
    os.mkdir(img_path+"ship/")
if not os.path.exists(img_path+"sx/"):
    os.mkdir(img_path+"sx/")
if not os.path.exists(img_path+"sd/"):
    os.mkdir(img_path+"sd/")
if not os.path.exists(img_path+"other/"):
    os.mkdir(img_path+"other/")

path_list = 0
for i in os.listdir(img_path):#获取图片数量
    path_list=path_list+len(os.listdir(img_path+i))
path = []
imgdata = []
state = True
cancel_tmr = False

for i in range(2):
    img_size_max[i] = int(img_size_max[i])
    img_size_min[i] = int(img_size_min[i])

def dowm(string):
    try:
        data = requests.get(
            string,
            timeout=5,
            headers={'User-Agent': 'Mozilla/5.0'},
            proxies={"http": None, "https": None},
            verify=False
        )
        if 400 <= data.status_code < 500:
            print(f"HTTP {data.status_code}错误 - 客户端请求异常: {string}")
            return None
        data.raise_for_status()
        #data = requests.get(string,proxies = { "http": None, "https": None})
        return data.content
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        return None
    except Exception as e:
        print(f"未知错误: {str(e)}")
        return None

def timer1():
    global path
    global imgdata
    global state
    paths = path
    path = []
	# 打印当前时间
    if not cancel_tmr:
        if len(paths)!=0:
            state = False
            start = time.time()
            imgdata = pool.map(dowm, paths)
            # for i in imgdata:
            #     print(len(i))
            # print(time.time()-start,len(imgdata))
            state = True
        threading.Timer(0.1, timer1).start()
        
def timer2():
    global path_list
    temp_sum = 0
    for i in os.listdir(img_path):  # 获取图片数量
        temp_sum = temp_sum + len(os.listdir(img_path+i))
    if path_list != temp_sum:
        get_Hash.get_MD5Hash(img_path)
    path_list = temp_sum
    threading.Timer(4, timer2).start()
    
def img_dow(image_url,file_name,file_name_S):
    global path
    global imgdata
    global state
    while not state:
        time.sleep(0.01)
    path.append(image_url)
    datatag = len(path)-1
    # print(datatag)
    time.sleep(0.1)
    while True:
        time.sleep(0.01)
        # print('sleep')
        if state:
            data = imgdata[datatag]
            break
    # data = requests.get(image_url).content
    if data is None:
        return "图像不符合"
    datalong = len(data)/1024/1024
    if datalong > 1:
        datalongstr = str(round(datalong,4))+'MB'
    else:
        datalongstr = str(round(datalong*1024,4))+'KB'
    if tuple(data[0:4]) == (0x47,0x49,0x46,0x38):
        # print("图片类型为GIF跳过")
        return "图像不符合"
    else:
        img_np_arr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(img_np_arr, cv2.IMREAD_COLOR)
        shape = img.shape
        cv2.imwrite(file_name_S,img)
        if shape[1] < img_size_max[0] and shape[0] < img_size_max[1] and shape[0] > img_size_min[1] and shape[1] > img_size_min[0]:
            if shape[0] > img_aim_long+200 or shape[1] > img_aim_long+200:
                if shape[0] > shape[1]:
                    beishu =  round(img_aim_long/shape[0],2)
                else:
                    beishu =  round(img_aim_long/shape[1],2)
                dst = cv2.resize(img,None, fy = beishu,fx=beishu, interpolation=cv2.INTER_AREA)  # 缩小
                dst = cv2.normalize(dst, dst=None, alpha=250, beta=5, norm_type=cv2.NORM_MINMAX)
                # dst = cv2.blur(dst,(3,3))#低值滤波
                dst = cv2.GaussianBlur(dst, (5, 5), 0, 0)  # 高斯滤波
                cv2.imwrite(file_name, dst)
            elif shape[0] < img_aim_long-300 and shape[1] < img_aim_long-300:
                if shape[0] > shape[1]:
                    beishu =  round(800/shape[0],2)
                else:
                    beishu =  round(800/shape[1],2)
                dst = cv2.resize(img, (int(beishu * shape[1]), int(beishu * shape[0])), interpolation=cv2.INTER_CUBIC)  # 放大2倍
                dst = cv2.normalize(dst, dst=None, alpha=250, beta=5, norm_type=cv2.NORM_MINMAX)
                # dst = cv2.blur(dst,(3,3))#低值滤波
                dst = cv2.GaussianBlur(dst, (5, 5), 0, 0)  # 高斯滤波
                cv2.imwrite(file_name, dst)
            else:
                dst = img
                cv2.imwrite(file_name, dst)
                # print()
            return datalongstr
        else:
            return "图像不符合"
pool = ThreadPool(6)
timer1()
timer2()
