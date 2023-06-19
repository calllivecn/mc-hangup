
import time

import cv2
import numpy as np
#from matplotlib import 
import matplotlib.pyplot as plt

import math

def cv2plt_gray(img):
    """
    把单通道灰度图转换成3通道灰度图 plt 才能正常显示。
    """
    a = np.expand_dims(img, axis=2)
    b = np.expand_dims(img, axis=2)
    c = np.expand_dims(img, axis=2)
    return np.concatenate((a, b, c), axis=-1)

def imgshow(imgs, gray_imgs=[]):
    s = len(imgs) + len(gray_imgs)
    print(f"共{s}张图片")
    n = math.sqrt(s)
    if n > int(n):
        m = int(n) + 1
    else:
        m = int(n)
    n = int(n)

    t = True
    while (n * m) < s:
        if t:
            n += 1
            t = False
        else:
            m +=1
            t = True

    plt.Figure()
    for i, img in enumerate(imgs):
        print(i, "shape:", img.shape) 
        plt.subplot(n, m, i+1)
        plt.imshow(img)
        plt.axis("off")

    for j, gray in enumerate(gray_imgs):
        img = cv2plt_gray(gray)
        plt.subplot(n, m, j+i+2)
        plt.imshow(img)
        plt.axis("off")

    plt.show()

def search_picture(target, temp, threshold=0.7):

    # self.target_img = cv2.imread('1630232776674203196.jpg')#要找的大图
    # img = cv2.resize(img, (0, 0), fx=self.scale, fy=self.scale)

    #temp_size = temp.shape[::2]
    temp_size = temp.shape

    img_gray = target
    #img_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(img_gray, temp, cv2.TM_CCOEFF_NORMED)

    # cv2.imwrite(f"{time.time_ns()}-img.PNG", img_gray)

    loc = np.where(result >= threshold)

    # 使用灰度图像中的坐标对原始RGB图像进行标记
    point = ()
    # for pt in zip(*loc[::-1]):
    for w, h in zip(*loc[::-1]):
        cv2.rectangle(img_gray, (w, h), (w + temp_size[1], w + temp_size[0]), (7, 249, 151), 1)
        point = pt

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

temp = cv2.imread("temp-big.png")
target = cv2.imread("target-small.png")

temp_w = 320
target_w = 96

scale = target_w / temp_w 

temp = cv2.resize(temp, (0, 0), fx=scale, fy=scale)

temp_gray = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

#retval_temp, dst_temp = cv2.threshold(temp_gray, 125, 255, cv2.THRESH_BINARY)
#retval_target, dst_target = cv2.threshold(target_gray, 125, 255, cv2.THRESH_BINARY)

# 边缘
temp_canny = cv2.Canny(temp_gray, 50, 200)
target_canny = cv2.Canny(target_gray, 50, 200)

grays=[temp_gray, target_gray, temp_canny, target_canny]

img, x, y = search_picture(temp_canny, target_canny, 0.5)

if img is None:
    print("没有匹配到")
else:
    print("找到目标")
    grays.append(img)

imgshow([temp, target], gray_imgs=grays)
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
