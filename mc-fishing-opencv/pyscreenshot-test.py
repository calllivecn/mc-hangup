#!/usr/bin/env python3
# coding=utf-8
# date 2023-06-17 02:46:37
# author calllivecn <c-all@qq.com>


import time

import pyscreenshot



t1 = time.time()
for i in range(10):
    img = pyscreenshot.grab(bbox=(0, 0, 400, 800), backend="mss")
t2 = time.time()
print(img)
print("平均一次耗时：", round((t2-t1)/10, 3), "/s")

