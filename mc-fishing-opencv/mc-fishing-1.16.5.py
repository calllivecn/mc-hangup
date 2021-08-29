#!/usr/bin/env python3
# coding=utf-8
# date 2021-08-29 04:30:13
# author calllivecn <c-all@qq.com>


import sys
import time
import tkinter as tk
from pathlib import Path
from threading import Thread

import cv2
from mss.models import Monitors
import numpy as np
import pyscreenshot
import matplotlib.pyplot as plt


try:
    pass
    # import libkbm
    # import libhotkey
except ModuleNotFoundError:
    print("需要安装keyboardmouse模块,地址：https://github.com/calllivecn/keyboardmouse", file=sys.stderr)
    sys.exit(1)


class BaitFish:

    def __init__(self, position, img_template='mc-fishing.png', threshold=0.7):

        self.threshold = threshold

        p_img_template = Path(img_template)
        if not p_img_template.exists():
            print("模板图片不存在。。。。", file=sys.stderr)
            sys.exit(2)

        #图中的小图
        template = cv2.imread(img_template)

        # position: (200, 200, 400, 500) 
        self.position = position

        # 拿到模板图片大小
        template_size = template.shape[:2]
        # print("template_size 1 :", template_size)

        # 比较 宽， 生产 缩放比例。
        self.scale = template_size[1] / position[0]

        template = cv2.resize(template, (0, 0), fx=self.scale, fy=self.scale)

        self.template_size = template.shape[:2]

        # print("template_size resize 2:", self.template_size)

        self.temp = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)


    # 获取屏幕指定位置的截图
    def screenshot(self):
        # self.target_img = pyscreenshot.grab(bbox=(200, 200, 400, 700))
        img = pyscreenshot.grab(bbox=self.position)
        self.target_img = np.asanyarray(img)
        # print("target_img shape:", self.target_img.shape)

        return img

        # plt.figure()
        # plt.imshow(img, animated=True)
        # plt.show()


    # 找图 返回最近似的点
    def search_picture(self):

        # img = cv2.imread('2021-08-29_04.32.47.png')#要找的大图
        # img = cv2.resize(img, (0, 0), fx=self.scale, fy=self.scale)

        img_gray = cv2.cvtColor(self.target_img, cv2.COLOR_BGR2GRAY)
        self.result = cv2.matchTemplate(img_gray, self.temp, cv2.TM_CCOEFF_NORMED)

        loc = np.where(self.result >= self.threshold)

        # 使用灰度图像中的坐标对原始RGB图像进行标记
        point = ()
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_gray, pt, (pt[0] + self.template_size[1], pt[1] + + self.template_size[0]), (7, 249, 151), 2)
            point = pt

        if point==():
            return None,None,None

        return img_gray, point[0]+ self.template_size[1]/2, point[1]


# 创建顶级组件容器
class Monitor:

    # 创建tkinter主窗口
    def __init__(self):

        self.root = tk.Tk()
        self.root.title("主窗口")

        # 指定主窗口位置与大小
        self.root.geometry("200x80+200+200")

        # 不允许改变窗口大小
        # root.resizable(False, False)

        self.top = tk.Toplevel(self.root)

        self.top.minsize(100, 50)

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        # print("screen:", self.screen_w, self.screen_h)

        self.top.geometry("200x200+400+300")

        self.top.overrideredirect(True)

        self.top.attributes('-alpha', 0.2)
        self.top.attributes("-topmost", True) 

        # label = tkinter.Label(top, bg="#f21312")
        # label.pack(fill=tkinter.BOTH, expand="y")

        label = tk.Label(self.top, bg="#1122cc", borderwidth=5)
        label.pack(fill=tk.BOTH, expand="yes")
        label.bind("<B1-Motion>", self.Resize)

        label2 = tk.Label(label, bg="#ff2233", borderwidth=5)
        label2.pack(fill=tk.BOTH, expand="yes", padx=5, pady=5)
        label2.bind("<Button-1>", self.mouseDown)
        label2.bind("<B1-Motion>", self.moveWin)

        self.show = True


    def addButton(self, text, func):
        # 上个按钮
        btn1 = tk.Button(self.root, text=text)
        btn1.bind("<Button-1>", func)
        btn1.pack()

    def mainloop(self):
        self.root.mainloop()

    def mouseDown(self, event):
        self.w_x = event.x
        self.w_y = event.y
        # print("mouseDown:", event, "w_x, w_y:", self.top.win, self.w_y)
    
    def moveWin(self, event):
        # print("move:", event)
        x = self.top.winfo_x() + (event.x - self.w_x)
        y = self.top.winfo_y() + (event.y - self.w_y)

        # print("x y:", f"+{x}+{y}")
        self.top.geometry(f"+{x}+{y}")
        # self.top.update()
    
    def Resize(self, event):
        self.top.geometry(f"{event.x}x{event.y}")
    
    def hideen(self):
        if self.show:
            self.show = False
            self.top.withdraw()
        else:
            self.show = True
            self.top.deiconify()
    
    def start(self, run):
        geometry = self.top.winfo_geometry()
        print("geometry:", geometry)
        w, tmp = geometry.split("x")
        h, x, y = tmp.split("+")

        self.position = (int(x), int(y), int(x) + int(w), int(y) + int(h))
        print(self.position)

        bf = BaitFish(self.position)

        self.hideen()

        self.th = Thread(target=run, args=(bf,), daemon=True)
        self.th.start()
        print("autofish running.")
    
    def end(self, event):
        self.hideen()


# init start
class AutoFish:

    def __init__(self, mon):
        self.mon = mon
        # self.kbm = libkbm.VirtualKeyboardMouse()

    def run(self, bf):
        plt.figure()
        while True:
            start = time.time()
            img = bf.screenshot()
            end = time.time()
            # print("screentshot time:", end - start)
            start = end

            img, x, y = bf.search_picture()
            end = time.time()
            # print("search picture time:", end - start)
            start = end
            if img:
                # 收鱼竿
                # self.kbm.mouseclick("right")
                print(f"{time.localtime()}: 收鱼竿")

                plt.imshow(img, animated=True)
                plt.show()
            else:
                plt.savefig(f"{time.time_ns()}.png") 


            end = time.time()
            print("time:", end - start)

            time.sleep(0.1)


# main
def main():
    mon = Monitor()

    fish = AutoFish(mon)

    mon.addButton("开始", lambda e: mon.start(fish.run))

    mon.addButton("停止", mon.end)

    mon.mainloop()


if __name__ == "__main__":
    main()