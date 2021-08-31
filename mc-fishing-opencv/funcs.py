#!/usr/bin/env python3
# coding=utf-8
# date 2021-08-31 00:15:13
# author calllivecn <c-all@qq.com>

import math

import cv2
import numpy as np
import matplotlib.pyplot as plt


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
        #plt.axis("off")

    for j, gray in enumerate(gray_imgs):
        img = cv2plt_gray(gray)
        plt.subplot(n, m, j+i+1)
        plt.imshow(img)
        #plt.axis("off")

    plt.show()

def search_picture(target, temp, threshold=0.7):

    # self.target_img = cv2.imread('1630232776674203196.jpg')#要找的大图
    # img = cv2.resize(img, (0, 0), fx=self.scale, fy=self.scale)

    temp_size = temp.shape[::2]

    img_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(img_gray, temp, cv2.TM_CCOEFF_NORMED)

    # cv2.imwrite(f"{time.time_ns()}-img.PNG", img_gray)

    loc = np.where(result >= threshold)

    # 使用灰度图像中的坐标对原始RGB图像进行标记
    point = ()
    for pt in zip(*loc[::-1]):
        cv2.rectangle(img_gray, pt, (pt[0] + temp_size[1], pt[1] + temp_size[0]), (7, 249, 151), 1)
        point = pt

    if point==():
        return None,None,None
    
    return img_gray, point[0]+ temp_size[1]/2, point[1]
