#!/usr/bin/env python3
# coding=utf-8
# date 2023-07-11 12:13:08
# author calllivecn <calllivecn@outlook.com>


import numpy as np

def matchTemplate_CCORR_NORMED(template, image):
    # 获取模板和图像的尺寸
    template_height, template_width = template.shape[:2]
    image_height, image_width = image.shape[:2]

    # 计算相关性
    correlation = np.zeros((image_height - template_height + 1, image_width - template_width + 1), dtype=np.float32)
    for y in range(image_height - template_height + 1):
        for x in range(image_width - template_width + 1):
            # 提取源图像的一小部分
            patch = image[y : y + template_height, x : x + template_width]
            
            # 计算相关性系数
            correlation[y, x] = np.sum(template * patch)

    # 归一化相关性
    min_correlation = np.min(correlation)
    max_correlation = np.max(correlation)
    normalized_correlation = (correlation - min_correlation) / (max_correlation - min_correlation)

    return normalized_correlation

"""
在上述代码中，我们定义了一个名为 matchTemplate_CCORR_NORMED 的函数，它接受模板图像和源图像作为输入，并返回归一化相关性结果。

首先，我们获取模板和图像的尺寸，然后初始化一个空的相关性矩阵 correlation，用于存储计算得到的相关性系数。

接下来，我们使用嵌套的循环遍历源图像的每个可能的位置，提取与模板大小相同的图像块，并计算相关性系数。计算相关性系数的方法是通过对模板和图像块逐元素相乘，并求和得到。

然后，我们找到相关性矩阵中的最小值和最大值，用于归一化处理。通过减去最小值，并除以最大值与最小值的差，我们将相关性系数缩放到 0 到 1 之间，得到归一化的相关性矩阵 normalized_correlation。

最后，我们将归一化的相关性矩阵作为函数的输出返回。

请注意，以上代码是一个简化的示例，仅适用于灰度图像和单通道模板。如果你需要处理彩色图像或多通道模板，请进行相应的调整。此外，此示例中的实现可能不如 OpenCV 提供的实现高效和优化。
"""


# 只使用numpy 实现 彩色图转灰度图

def convert_image_to_grayscale(image):
  """Converts an image to grayscale.

  Args:
    image: A NumPy array representing an image.

  Returns:
    A NumPy array representing the grayscale image.
  """

  # Convert the image to a NumPy array of floats.
  image = np.asfarray(image)

  # Calculate the average of each RGB channel.
  grayscale_image = np.dot(image, [0.2989, 0.5870, 0.1140])

  # Return the grayscale image.
  return grayscale_image


# 
import numpy as np

def match_template(image, template):
  """Matches a template image against an image.

  Args:
    image: A NumPy array representing an image.
    template: A NumPy array representing a template image.

  Returns:
    A NumPy array of the same shape as `image`, where each element is the
    similarity between the corresponding pixel in `image` and the template image.
  """

  # Convert the images to grayscale.
  image_grayscale = np.asfarray(image).astype(np.float32)
  template_grayscale = np.asfarray(template).astype(np.float32)

  # Compute the correlation between the images.
  correlation = np.correlate(image_grayscale, template_grayscale, mode='same')

  # Return the correlation.
  return correlation


