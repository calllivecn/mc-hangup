
import copy
import time

import cv2
import numpy as np
#from matplotlib import 
import matplotlib.pyplot as plt

import math

from funcs import imgshow


def search_picture(target, temp, target_src, threshold=0.7):

    # self.target_img = cv2.imread('1630232776674203196.jpg')#要找的大图
    # img = cv2.resize(img, (0, 0), fx=self.scale, fy=self.scale)

    #temp_size = temp.shape[::2]
    temp_size = temp.shape

    img_gray = target
    print(f"{temp.shape=}  {target.shape=}")
    #img_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(img_gray, temp, cv2.TM_CCOEFF_NORMED)

    # cv2.imwrite(f"{time.time_ns()}-img.PNG", img_gray)

    loc = np.where(result >= threshold)

    # 使用灰度图像中的坐标对原始RGB图像进行标记(把找到的位置用矩形框出来)
    point = ()
    # for pt in zip(*loc[::-1]):
    for w, h in zip(*loc[::-1]):
        cv2.rectangle(target_src, (w, h), (w + temp_size[1], h + temp_size[0]), color=(7, 249, 151), thickness=2)
        point = (w, h)

    if point==():
        return None,None,None
    
    return img_gray, point[0]+ temp_size[1]/2, point[1]


#temp = cv2.imread("template.png", cv2.IMREAD_UNCHANGED)
#target = cv2.imread("target.png", cv2.IMREAD_UNCHANGED)

"""
使用二值化后 在缩放（还没完整测试）


使用 缩放 后的 灰度图 进行 边缘检测 在 匹配，(testing）
1. to 灰度图
2. 缩放
3. 边缘检测
4. match

5. 把 2步 3步交换下顺序
"""

temp = cv2.imread("images/mc-fishing_1920x1080.png")
target = cv2.imread("images/target_1920x1080.png")

temp_gray = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

#retval_temp, dst_temp = cv2.threshold(temp_gray, 125, 255, cv2.THRESH_BINARY)
#retval_target, dst_target = cv2.threshold(target_gray, 125, 255, cv2.THRESH_BINARY)

# 边缘
temp_canny = cv2.Canny(temp_gray, 50, 200)
target_canny = cv2.Canny(target_gray, 50, 200)

grays=[temp_gray, target_gray, temp_canny, target_canny]

img, x, y = search_picture(target_gray, temp_gray, target, 0.7)

if img is None:
    print("没有匹配到")
else:
    print("找到目标")

imgshow([temp, cv2.cvtColor(target, cv2.COLOR_BGR2RGB)])
imgshow(grays, True)

exit(0)

#temp = cv2.cvtColor(temp, cv2.COLOR_BGR2RGB)

"""
resize:

INTER_NEAREST：最近邻插值

INTER_LINEAR：线性插值（默认）

INTER_AREA：区域插值

INTER_CUBIC：三次样条插值

INTER_LANCZOS4：Lanczos 插值

缩小时推荐使用 cv2.INTER_AREA

扩展放大时推荐使用 cv2.INTERCUBIC 和 cv2.INTERLINEAR，前者比后者运行速度慢。
"""

scale = 0.9

#temp = cv2.resize(temp, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

target = cv2.resize(target, (0, 0), fx=1.1, fy=1.1, interpolation=cv2.INTER_CUBIC)

temp_h, temp_w = temp.shape[:2]

result = cv2.matchTemplate(target, temp, cv2.TM_CCOEFF_NORMED) 

loc = np.where(result >= 0.8)
for pt in zip(*loc[::-1]):
    cv2.rectangle(target, pt, (pt[0] + temp_w, pt[1] + temp_h), (255, 0, 0), 2)

imgshow((temp, target))
