#!/usr/bin/env python3
# coding=utf-8
# date 2021-08-29 04:30:13
# author calllivecn <c-all@qq.com>

import os
import sys
import time
import json
import subprocess
import threading
import tkinter as tk
from tkinter import (
    ttk,
    messagebox,
)
from pathlib import Path
from threading import Thread, Lock

import cv2
import numpy as np
import pyscreenshot
import matplotlib.pyplot as plt

"""
try:
    # 这玩意儿，会移动鼠标～why？？？
    import pyautogui
except ModuleNotFoundError:
    print(f"当前是win 系统 需要安装 pip install pyautogui 包")
    sys.exit(1)
"""


# TEMPLATE_PATH = Path("images") / "mc-fishing_1920x1080.png"
TEMPLATE_PATH = Path("images") / "mc-fishing_850x480.png"

ICON = Path("images") / "icon.png"

class Conf:

    def __init__(self, savefile="data.json"):
        self.savefile = Path(savefile)
        
        # 如果没有，则初始化。
        if not self.savefile.exists():

            self.__d["850x480(推荐)"] = {
                "template": "mc-fishing_850x480.png",
                "win_pos": self.game_resolution.winfo_geometry(),
                "temp_post": (700, 300, 150, 160)
            }
    
    def query(self, selectmode):

        with open(self.savefile, "r") as f:
            self.__d = json.load(f)
        
        conf = self.__d.get(selectmode)

        if conf is None:
            return conf
        else: 
            self.template = Path(conf["template"])

            # 例：win_pos = 850x480+700+300
            self.win_pos = conf["win_pos"]

            # 是相对于 win_pos 的位置，和  模板本身的长宽 例：(700, 300, 150, 160)
            self.temp_pos = conf["temp_pos"]

            return True


    def save(self, selectname, template, win_pos, temp_pos):
        
        with open(self.savefile, "r") as f:
            self.__d = json.load(f)
        
        self.__d[selectname] = {
            "template": str(template),
            "win_post": win_pos,
            "temp_post": temp_pos,
        }
        
        with open(self.savefile, "w") as f:
            json.dump(self.__d, f)
        
        return True


class Mouse:

    def __init__(self):
        # default usage
        self.autotool = lambda : subprocess.run(["mouse.py"], stdout=subprocess.PIPE)

        try:
            result = subprocess.run("type -p xdotool".split(), shell=True, stdout=subprocess.PIPE)
            result.check_returncode()
            self.autotool = lambda : subprocess.run("xdotool click 3".split(), stdout=subprocess.PIPE)
        except Exception as e:
            print("没有找到 xdotool, 尝试其他工具。")
            # self.autotool = lambda : pyautogui.rightClick()


        if sys.platform == "linux":
            if "wayland" in os.getenv("XDG_SESSION_TYPE").lower():
                print("你的桌面环境是 wayland 的~")
                print("还没有实现~~哈哈, 请换成，X11 桌面环境~, 可以测试使用了")

                try:
                    result = subprocess.run("type -p mouse.py".split(), shell=True)
                    result.check_returncode()
                    self.autotool = lambda : subprocess.run(["mouse.py"], stdout=subprocess.PIPE)
                except Exception as e:
                    raise e
                    # print("使用pyautogui...")
                    # self.autotool = lambda : pyautogui.rightClick()

                """
                try:
                    import libkbm
                except ModuleNotFoundError:
                    print("需要安装keyboardmouse模块,地址：https://github.com/calllivecn/keyboardmouse")
                    sys.exit(1)
                """
            else:
                print("你的桌面环境是 X11 的~")

    def click_right(self):
        self.autotool()


class BaitFish:

    def __init__(self, position, img_template, threshold=0.75):

        self.threshold = threshold

        p_img_template = Path(img_template)
        if not p_img_template.exists():
            print("模板图片不存在。。。。", file=sys.stderr)
            sys.exit(2)

        #图中的小图
        self.template = cv2.imread(img_template)

        # position: (200, 200, 400, 500) 
        self.position = position
        # print("self.target size: ", position[2] - position[0])

        # 拿到模板图片大小
        template_size = self.template.shape
        h,w,c = template_size

        print("template_size 1 :", template_size)

        # 比较 宽， 生产 缩放比例。
        self.scale = (position[2] - position[0]) / w
        print("scale: ", self.scale)

        # self.template = cv2.resize(template, (0, 0), fx=self.scale, fy=self.scale)

        #self.template_size = self.template.shape[:2]

        self.template_size = self.template.shape

        self.temp = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)

        print("template_size resize 2:", self.template_size)

        # cv2.imwrite(f"{time.time_ns()}-temp.PNG", self.temp) #, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    

    # 获取屏幕指定位置的截图
    def screenshot(self):
        img = pyscreenshot.grab(bbox=self.position)

        # RGBA 2 RGB
        img = img.convert("RGB")

        # img.save("screenshot-RGB.png")
        # self.target_img = np.asanyarray(img)

        # RGB 2 BGR
        # self.target_img = self.target_img[..., ::-1]
        self.target_img = cv2.cvtColor(np.asanyarray(img), cv2.COLOR_RGB2BGR)

        # RGBA 2 BGR
        # self.target_img = cv2.cvtColor(np.asanyarray(img), cv2.COLOR_RGBA2BGR)

        # plt.figure()
        # plt.imshow(self.target_img, animated=True)
        # plt.show()

        return self.target_img


    # 找图 返回最近似的点
    def search_picture(self):

        # self.target_img = cv2.imread('1630232776674203196.jpg')#要找的大图
        # img = cv2.resize(img, (0, 0), fx=self.scale, fy=self.scale)


        img_gray = cv2.cvtColor(self.target_img, cv2.COLOR_BGR2GRAY)

        self.result = cv2.matchTemplate(img_gray, self.temp, cv2.TM_CCOEFF_NORMED)

        # cv2.imwrite(f"{time.time_ns()}-img.PNG", img_gray)

        loc = np.where(self.result >= self.threshold)

        # 使用灰度图像中的坐标对原始RGB图像进行标记
        point = ()
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_gray, pt, (pt[0] + self.template_size[1], pt[1] + self.template_size[0]), (7, 249, 151), 2)
            point = pt

        if point==():
            return None,None,None
        
        return img_gray, point[0]+ self.template_size[1]/2, point[1]

# 创建顶级组件容器
class AutoFishing:

    # 创建tkinter主窗口
    def __init__(self):

        # 初始化窗口，配置相关
        # self.kbm = libkbm.VirtualKeyboardMouse()

        # mouse click <right>
        # click_right is function()
        self.mouse = Mouse()

        self.root = tk.Tk()
        self.root.title("自动钓鱼AI")

        # 设置应用图标
        # self.root.iconbitmap(tk.PhotoImage(ICON))
        self.root.iconphoto(False, tk.PhotoImage(file=ICON))

        # 不允许改变窗口大小
        # root.resizable(False, False)

        # self.top = tk.Toplevel(self.root)
        self.game_resolution = tk.Toplevel(self.root)

        # self.top.minsize(100, 50)

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        # print("screen:", self.screen_w, self.screen_h)

        # 指定主窗口位置与大小
        self.root.geometry(f"+{round(self.screen_w/5)}+{round(self.screen_h/5)}")

        self.game_resolution.geometry("850x480")
        self.game_resolution.resizable(False, False)
        self.winCenter(self.game_resolution, 850, 480)

        # self.top.overrideredirect(True)
        # self.game_resolution.overrideredirect(True)

        # self.top.attributes('-alpha', 0.2)
        self.game_resolution.attributes('-alpha', 0.2)

        # self.top.attributes("-topmost", True) 
        # print("grame_resolution topmost: ", self.game_resolution.attributes("-topmost"))

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        l1 = tk.Label(self.frame, text="选择模式：")
        l1.grid(row=0, column=0)

        # select 框
        self.selected = ttk.Combobox(self.frame, values=["850x480(推荐)", "其他模式"], state="readonly")
        self.selected.bind("<<ComboboxSelected>>", self.selectmode)
        self.selected.current(0)
        self.selected.grid(row=0, column=1)

        # label = tkinter.Label(top, bg="#f21312")
        # label.pack(fill=tkinter.BOTH, expand="y")

        # top
        # label = tk.Label(self.top, bg="#1122cc", borderwidth=5)
        # label.pack(fill=tk.BOTH, expand="yes")
        # label.bind("<B1-Motion>", lambda e : self.Resize(e, self.top))

        # label2 = tk.Label(label, borderwidth=5)
        # label2.pack(fill=tk.BOTH, expand="yes", padx=5, pady=5)
        # label2.bind("<Button-1>", self.mouseDown)
        # label2.bind("<B1-Motion>", lambda e : self.moveWin(e, self.top))

        # game_resoultion
        label = tk.Label(self.game_resolution, bg="#1122cc", borderwidth=5)
        label.pack(fill=tk.BOTH, expand="yes")
        # label.bind("<B1-Motion>", lambda e: self.Resize(e, self.game_resolution))

        label2 = tk.Label(label, borderwidth=5)
        label2.pack(fill=tk.BOTH, expand="yes", padx=5, pady=5)
        label2.bind("<Button-1>", self.mouseDown)
        label2.bind("<B1-Motion>", lambda e: self.moveWin(e, self.game_resolution))

        self.run_lock = Lock()

        # self.addButton("开始", lambda e: self.start())
        # self.addButton("停止", lambda e: self.stop())

        # start stop
        self.start_stop_var = tk.StringVar()
        self.start_stop_var.set("开始")
        self.start_stop_btn = tk.Button(self.frame, textvariable=self.start_stop_var)
        self.start_stop_btn.bind("<Button-1>", lambda e: self.start())
        self.start_stop_btn.grid(row=0, column=2)
        # self.frame_start_stop.pack()

        self.fishcount = 0
        self.fishingspeed = 0
        self.speed = []
        self.fishingspeed_timestamp = time.time()
        self.fishcount_var = tk.StringVar()
        self.fishcount_string = "当前钓鱼速度为：{} s/条，已经钓到 {} 条鱼"
        self.fishcount_var.set(self.fishcount_string.format(self.fishingspeed, self.fishcount))
        fishcount_label = tk.Label(self.root, textvariable=self.fishcount_var)
        fishcount_label.pack()

    def addButton(self, text, func):
        # 上个按钮
        btn1 = tk.Button(self.root, text=text)
        btn1.bind("<Button-1>", func)
        btn1.pack()

    def mainloop(self):
        self.root.mainloop()
    
    def selectmode(self, event):
        value = self.selected.get()
        print("select mode event:", event, "value:", value)

        if value == "850x480(推荐)":
            self.conf = Conf(Path("images") / "mc-fishing_850x480.png",
                                win_pos=self.game_resolution.winfo_geometry(),
                                temp_post=(700, 300, 150, 160)
                            )
        elif value == "1920x1080":
            self.conf = Conf(Path("images") / "mc-fishing_1920x1080.png",
                                win_pos=self.game_resolution.winfo_geometry(),
                                temp_post=(700, 300, 150, 160)
                            )
        elif value == "其他模式":
            messagebox.showinfo(title="提示", message="还没实现，请期待～")
            self.selected.current(0)
        else:
            messagebox.showinfo(title="提示", message="还没实现，请期待～")
            self.selected.current(0)
    
    def winCenter(self, win, w, h):
        # w = win.winfo_width()
        # h = win.winfo_height()

        x = round((self.screen_w - w) / 2)
        y = round((self.screen_h - h) / 2)
        # print("win Center", w, h, x, y, self.screen_w, self.screen_h)
        win.geometry(f"+{x}+{y}")


    def mouseDown(self, event):
        self.w_x = event.x
        self.w_y = event.y
        # print("mouseDown:", event, "w_x, w_y:", self.top.win, self.w_y)
    
    def moveWin(self, event, who):
        # print("move:", event)
        x = who.winfo_x() + (event.x - self.w_x)
        y = who.winfo_y() + (event.y - self.w_y)

        # print("x y:", f"+{x}+{y}")
        who.geometry(f"+{x}+{y}")
        # self.top.update()
    
    def Resize(self, event, who):
        who.geometry(f"{event.x}x{event.y}")
    

    def fishshow(self, cur):
        self.fishcount += 1
        self.fishingspeed = round(cur - self.fishingspeed_timestamp)

        # 如果是正常钓鱼，不是暂停，钓鱼时间应该会小于45s
        if self.fishingspeed <= 45:

            # 计数100次后，重新开始计算钓鱼速度。
            if len(self.speed) > 100:
                self.speed = [self.fishingspeed]
            else:
                self.speed.append(self.fishingspeed)

            speed  = round(sum(self.speed) / len(self.speed))

            self.fishcount_var.set(self.fishcount_string.format(speed, self.fishcount))

        self.fishingspeed_timestamp = cur
    
    
    def start(self):
        if self.run_lock.locked():
            self.start_stop_var.set("开始")
            self.run_lock.release()

            # 显示窗口
            # self.top.deiconify()
            self.game_resolution.deiconify()

            print("stoping...", self.th.name)
        else:
            # 隐藏窗口
            # self.top.withdraw()
            self.game_resolution.withdraw()

            print("start ...")        
            self.start_stop_var.set("暂停")
            self.run_lock.acquire()

            # 拿到 游戏屏幕位置
            game_geometry = self.game_resolution.winfo_geometry()
            print("game_resolution geometry:", game_geometry)

            w, tmp = game_geometry.split("x")
            h, x, y = tmp.split("+")

            self.game_position = (int(x), int(y))

            # 根据 game_position 位置，算出 目标图像在屏幕中的位置
            temp_x1, temp_y1 = self.game_position[0] + 700, self.game_position[1] + 300
            temp_x2, temp_y2 = temp_x1 + 150, temp_y1 + 160

            screentshot_pos = (temp_x1, temp_y1, temp_x2, temp_y2)
            print("tempalte posistion: ", screentshot_pos)

            self.BF = BaitFish(screentshot_pos, str(TEMPLATE_PATH))
            self.th = Thread(target=self.run, daemon=True)
            self.th.start()
            print(self.th.name, "autofish running.")
    
    def run(self):
        while self.run_lock.locked():

            start = time.time()

            p = self.BF.screenshot()
            img, x, y = self.BF.search_picture()

            end = time.time()

            t = round(end - start, 3)
            if img is None:
                # cv2.imwrite(f"{time.time_ns()}.PNG", p)
                interval = 0.1 -  t
                if interval >= 0:
                    time.sleep(interval)
                else:
                    print(f"""{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}: {t}/s 当前机器性能不足，可能错过收竽时机。""")
            else:
                t = round(end - start, 3)
                # 收鱼竿
                #subprocess.run("xdotool click 3".split())
                self.fishshow(end)
                self.mouse.click_right()
                print(f"""{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}: 收鱼竿""")
                # cv2.imwrite(f"{time.time_ns()}-ok.PNG", img)# [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                time.sleep(1)
                self.mouse.click_right()
                time.sleep(2)

            # start = end
            # print(f"""{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}: {t}/s 当前性能。""")

        th = threading.current_thread()
        
        print(th.name, "退出...")
        if self.run_lock.locked():
            self.run_lock.release()
        # cv2.destroyAllWindows()


# main
def main():
    fishing = AutoFishing()
    fishing.mainloop()


if __name__ == "__main__":
    main()
