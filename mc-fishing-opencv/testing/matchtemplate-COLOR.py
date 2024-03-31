#!/usr/bin/env python3
# coding=utf-8
# date 2023-07-11 12:29:28
# author calllivecn <calllivecn@outlook.com>

"""
在 OpenCV 的 matchTemplate 函数中，各种匹配方法（如 cv2.TM_SQDIFF、cv2.TM_CCORR、cv2.TM_CCOEFF 等）可以用于匹配彩色图像，而不仅限于灰度图像。

当使用彩色图像进行模板匹配时，需要对每个通道（如红色、绿色、蓝色）分别进行匹配操作，然后将匹配结果合并。

以下是一种用于匹配彩色图像的伪代码示例：
"""

import cv2
import numpy as np

def matchTemplate_color(template, image, method):
    # 拆分模板和图像的通道
    template_channels = cv2.split(template)
    image_channels = cv2.split(image)

    # 初始化匹配结果矩阵
    result = np.zeros_like(image)

    # 针对每个通道进行匹配
    for template_channel, image_channel in zip(template_channels, image_channels):
        # 使用匹配方法进行模板匹配
        match_result = cv2.matchTemplate(image_channel, template_channel, method)

        # 将匹配结果累加到最终结果矩阵
        result += match_result

    return result

# 示例用法
template = cv2.imread("template.png")
image = cv2.imread("image.png")

# 使用彩色图像匹配方法（如cv2.TM_CCOEFF_NORMED）
matched_image = matchTemplate_color(template, image, cv2.TM_CCOEFF_NORMED)


"""
在上述示例代码中，我们定义了一个名为 matchTemplate_color 的函数，该函数可以用于匹配彩色图像。在函数内部，我们首先将模板图像和源图像的通道分离成单独的通道。

然后，我们针对每个通道分别应用匹配方法，使用 OpenCV 的 matchTemplate 函数进行模板匹配。对于每个通道，我们得到了单通道的匹配结果。

最后，我们将每个通道的匹配结果累加到最终的匹配结果矩阵中，得到最终的彩色匹配结果。

请注意，这只是一个示例，如果有其他特定需求，可以根据具体情况进行调整和优化。同时，这种方法对于特定的匹配场景可能有一定的局限性，需要根据具体问题进行评估和调整。
"""

