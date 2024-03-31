#!/usr/bin/env python3
# coding=utf-8
# date 2023-07-14 22:42:19
# author calllivecn <calllivecn@outlook.com>

import sys

import cv2
import numpy as np
#from matplotlib import 
import matplotlib.pyplot as plt

from funcs import imgshow


def draw_loction(target, temp_w, temp_h, loc):
    # 使用灰度图像中的坐标对原始RGB图像进行标记(把找到的位置用矩形框出来)
    # for x, y in zip(*loc[::-1]):
    for x, y in zip(*loc[::-1]):
        cv2.rectangle(target, (x, y), (x + temp_w, y + temp_h), color=(7, 249, 151), thickness=1)


def deduplication(loc, temp_size):
    """
    找出位置后，还需要去除重复的位置，因为步长是1个像素，所以可能会重复。
    拿到第一个位置，只要接下来的位置在（w+temp_w, h+temp_h）这个范围内就说明是重复的。
    """

    loc_dedup_x = [loc[1][0]]
    loc_dedup_y = [loc[0][0]]

    print(f"{loc_dedup_x=} {loc_dedup_y=}")
    for x, y in zip(*loc[::-1]):
        if (x - loc_dedup_x[-1]) <= temp_size[0] and (y - loc_dedup_y[-1]) <= temp_size[1]:
            pass
        else:

            loc_dedup_x.append(x)
            loc_dedup_y.append(y)

    return (loc_dedup_y, loc_dedup_x)



def search_picture(target, temp, threshold=0.7):

    temp_w, temp_h = temp.shape[1], temp.shape[0]

    print(f"{temp_w=}  {temp_h=}")

    result = cv2.matchTemplate(target, temp, cv2.TM_CCOEFF_NORMED)

    loc = np.where(result >= threshold)
    # loc: (y: array([...]), x: array[...])

    dedup_loc = deduplication(loc, temp_size=(temp_w, temp_h))

    draw_loction(target, temp_w, temp_h, dedup_loc)
    
    return dedup_loc


def search_one_picture(target, temp, threshold=0.7):

    temp_w, temp_h = temp.shape[1], temp.shape[0]

    print(f"{temp_w=}  {temp_h=}")

    result = cv2.matchTemplate(target, temp, cv2.TM_CCOEFF_NORMED)

    loc = np.where(result >= threshold)
    # loc: (y: array([...]), x: array[...])

    return (loc[0][0], loc[1][0])


temp_path = sys.argv[1]
target_path = sys.argv[2]

# cv2.imread() 读出来的，是BGR 颜色通道。
temp = cv2.imread(temp_path)
target = cv2.imread(target_path)

position_count = search_picture(target, temp, 0.8)

print(f"{position_count}")
count = len(position_count[0]) 
if count == 0:
    print("没有匹配到")
else:
    print(f"找到 {count} 目标")

imgshow([cv2.cvtColor(temp, cv2.COLOR_BGR2RGB), cv2.cvtColor(target, cv2.COLOR_BGR2RGB)])

# 单独，标记后的图片
imgshow([cv2.cvtColor(target, cv2.COLOR_BGR2RGB)])

