#!/usr/bin/env python3
# coding=utf-8
# date 2023-07-14 20:27:51
# author calllivecn <c-all@qq.com>


import numpy as np
from scipy.signal import convolve2d
import matplotlib.pyplot as plt
from PIL import Image

# 读取图像并转换为灰度图
img = Image.open('../images/target_1920x1080.png')
img = np.array(img)

# 定义一个模糊核
kernel = np.array([[1, 2, 1],
                   [2, 4, 2],
                   [1, 2, 1]]) / 16

# 使用卷积对图像进行模糊处理
blurred_img = convolve2d(img, kernel, mode='same')

# 显示原始图像和模糊后的图像
plt.subplot(121)
plt.imshow(img, cmap='gray')
plt.title('Original Image')

plt.subplot(122)
plt.imshow(blurred_img, cmap='gray')
plt.title('Blurred Image')

plt.show()

