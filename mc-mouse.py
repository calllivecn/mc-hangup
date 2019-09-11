#!/usr/bin/env python3
# coding=utf-8
# date 2019-09-11 21:24:52
# author calllivecn <c-all@qq.com>

import time

import libkbm


kbm = libkbm.VirtualKeyboardMouse()


try:
    while True:
        kbm.mouseclick("right")
        time.sleep(1)
except KeyboardInterrupt:
    print()

try:
    kbm.mousebtndown("left")
    input("按CTRL+C结束。")
except KeyboardInterrupt:
    kbm.mousebtnup("left")
    print()
