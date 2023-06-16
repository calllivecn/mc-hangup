#!/usr/bin/env python3
# coding=utf-8
# date 2023-06-14 20:12:12
# author calllivecn <c-all@qq.com>

import time

from cnocr import CnOcr

img_fp = 'images/mc-fishing_1920x1080_1.18_src.png'
img_fp = '/tmp/截图 2023-06-14 20-15-44.png'
ocr = CnOcr()  # 所有参数都使用默认值

t1=time.time()
for i in range(10):
    out = ocr.ocr(img_fp)
t2=time.time()

print(out)

print(f"耗时：{t2-t1}/s")
