#!/usr/bin/env python3
# coding=utf-8
# date 2021-08-29 04:30:13
# author calllivecn <c-all@qq.com>

import os
import sys
import time
import json
import socket
import logging
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
#import pyscreenshot
import mss

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    print(f"matpotlib 没有安装，不影响使用。")

"""
try:
    # 这玩意儿，会移动鼠标～why？？？
    import pyautogui
except ModuleNotFoundError:
    print(f"当前是win 系统 需要安装 pip install pyautogui 包")
    sys.exit(1)
"""

def getlogger(level=logging.INFO):
    logger = logging.getLogger("logger")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(filename)s:%(funcName)s:%(lineno)d %(message)s", datefmt="%Y-%m-%d-%H:%M:%S")
    consoleHandler = logging.StreamHandler(stream=sys.stdout)
    #logger.setLevel(logging.DEBUG)

    consoleHandler.setFormatter(formatter)

    # consoleHandler.setLevel(logging.DEBUG)
    logger.addHandler(consoleHandler)
    logger.setLevel(level)
    return logger

logger = getlogger()

DEBUG2 = 5

def runtime(func):
    def wrap(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        logger.log(DEBUG2, f"{func.__name__} 的运行耗时: {t2-t1} /秒")
        return result
    
    return wrap


MC_PROMPT="""\
1. 需要把游戏的字幕打开。
2. 把游戏窗口调整为和这个窗口一样大，并重叠，然后点开始。
3. 挂机时可以把帧数调低+可视范围调低+画质调低，
4. 在使用地毯mod加速时，最高只到/tick rate 50 就好，在多没有用。
"""


with open("usage.txt") as f:
    HELP_INFO=f.read()


# 每秒检测帧数
FPS = 30

# TEMPLATE_PATH = Path("images") / "mc-fishing_1920x1080.png"
# TEMPLATE_PATH = Path("images") / "mc-fishing_850x480.png"
TEMPLATE_PATH = Path("images") / "mc-fishing_850x480_1.18.png"
ICON = Path("images") / "icon.png"

class Conf:
    """
    ~~这玩意有bug,不能保存左上角坐标。改成左下角坐标，然后推算左上解坐标。~~
    """

    def __init__(self, savefile="data.json"):
        if savefile != Path:
            self.savefile = Path(savefile)
        else:
            self.savefile = savefile
        
        # 如果没有，则初始化。
        self.chekc_conf = self.savefile.exists()
    
    def load(self):

        with open(self.savefile, "r") as f:
            self._d = json.load(f)
        

        self.index = self._d["index"]
        self.template = self._d["template"]
        # 例：win_pos = 850x480+700+300
        self.win_pos = self._d["win_pos"]
        # 是相对于 win_pos 的位置，和 模板本身的长宽 例：(700, 300, 150, 160)
        self.screen_pos = self._d["screen_pos"]

        return True


    def save(self, index, template, win_pos, temp_pos):
        
        self._d = {
            "index": index,
            "template": str(template),
            "win_pos": win_pos,
            "screen_pos": temp_pos, # 截图相对游戏窗口的位置
        }
        
        with open(self.savefile, "w") as f:
            json.dump(self._d, f)
        
        return True

# check 桌面环境

class Mouse:

    def __init__(self):
        # default usage
        if sys.platform == "linux":

            if "wayland" in os.getenv("XDG_SESSION_TYPE").lower():
                try:
                    import mouse
                except ModuleNotFoundError:
                    logger.error(f"需要安装keyboardmouse模块,地址：https://github.com/calllivecn/keyboardmouse")
                    sys.exit(1)

                logger.info("你的桌面环境是 wayland 的~")
                logger.info("使用 mouse.py 鼠标方案")

                """
                try:
                    result = subprocess.run("type -p mouse.py".split(), shell=True)
                    result.check_returncode()
                    self.autotool = lambda : subprocess.run("mouse.py --mouseclick right".split(), stdout=subprocess.PIPE)
                except Exception as e:
                    print("需要安装keyboardmouse模块,地址：https://github.com/calllivecn/keyboardmouse", sys.stderr)
                    raise e
                    # print("使用pyautogui...")
                    # self.autotool = lambda : pyautogui.rightClick()
                """

                # 使用 mouse.py 
                self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                self.sock.settimeout(3)

                cmd = mouse.Cmd(mouse.SECRET)

                self.data = cmd.tobyte("right", mouse.KeySeq.MouseClick)

                def click(data):

                    self.sock.sendto(data, mouse.ADDR)
                    try:
                        data, addr = self.sock.recvfrom(64)
                    except socket.timeout:
                        logger.warning("收到 mouse.py server 确认超时")
                        sys.exit(2)

                    if data == b"ok":
                        return True, "ok"
                    else:
                        return "error: ", data

                self.autotool = lambda : click(self.data)

            else:
                logger.info("你的桌面环境是 X11 的~")
                logger.info("使用 xdotool 方案")

                try:
                    result = subprocess.run("type -p xdotool".split(), shell=True, stdout=subprocess.PIPE)
                    result.check_returncode()
                    self.autotool = lambda : subprocess.run("xdotool click 3".split(), stdout=subprocess.PIPE)
                except Exception as e:
                    logger.error("没有找到 xdotool, 尝试其他工具。")
                    raise e
                    # self.autotool = lambda : pyautogui.rightClick()

        else:
            logger.error("你的系统还没支持哦～")
            sys.exit(1)

    def click_right(self):
        self.autotool()
    
    def close(self):
        self.sock.close()


class BaitFish:

    def __init__(self, position, img_template, threshold=0.75):

        self.threshold = threshold

        p_img_template = Path(img_template)
        if not p_img_template.exists():
            logger.error("模板图片不存在。。。。")
            sys.exit(2)

        #图中的小图
        self.template = cv2.imread(img_template)

        # position: (200, 200, 400, 500) 
        self.position = position

        # 拿到模板图片大小
        template_size = self.template.shape
        h,w,c = template_size

        logger.debug(f"template_size 1 : {template_size}")

        # 比较 宽， 生产 缩放比例。(缩放之后就匹配不上了。。。。)
        # self.scale = (position[2] - position[0]) / w
        # logger.debug(f"scale: {self.scale}")

        # self.template = cv2.resize(template, (0, 0), fx=self.scale, fy=self.scale)

        #self.template_size = self.template.shape[:2]

        self.template_size = self.template.shape
        self.temp = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)

        # logger.debug(f"template_size resize 2: {self.template_size}")

        # cv2.imwrite(f"{time.time_ns()}-temp.PNG", self.temp) #, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

        self.mss_shot = mss.mss()


    def mss_close(self):
        self.mss_shot.close()


    def set_fps(self, fps):
        self.fps = fps


    # 获取屏幕指定位置的截图
    @runtime
    def screenshot(self):
        img = pyscreenshot.grab(bbox=self.position)

        # RGBA 2 RGB
        img = img.convert("RGB")
        if len(sys.argv) >= 2 and sys.argv[1] == "--debug":

            imgs = Path("img-debug")
            if not imgs.is_dir():
                os.mkdir(imgs)

            t=time.time_ns()
            img.save(f"{str(imgs)}/{t}-RGB.png")

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
    

    # 获取屏幕指定位置的截图(新版库，性能高)
    @runtime
    def screenshot_mss(self):
        img = self.mss_shot.grab(self.position)
        self.target_img = cv2.cvtColor(np.asanyarray(img), cv2.COLOR_RGB2BGR)
        return self.target_img


    @runtime
    def search_one_picture(self) -> bool:

        img_gray = cv2.cvtColor(self.target_img, cv2.COLOR_BGR2GRAY)

        self.result = cv2.matchTemplate(img_gray, self.temp, cv2.TM_CCOEFF_NORMED)
        """
        返回的是 ([x1, ...], [y1, ...])
        """

        loc = np.where(self.result >= self.threshold)
        """
        loc: 是这样的 loc=(array([], dtype=int64), array([], dtype=int64))
        """
        if len(loc[0]) >= 1:
            return True
        else:
            return False

    @runtime
    def search_more_picture(self) -> int:
        img_gray = cv2.cvtColor(self.target_img, cv2.COLOR_BGR2GRAY)

        self.result = cv2.matchTemplate(img_gray, self.temp, cv2.TM_CCOEFF_NORMED)
        """
        返回的是 ([x1, ...], [y1, ...])
        """

        loc = np.where(self.result >= self.threshold)
        """
        loc: 是这样的 loc=(array([], dtype=int64), array([], dtype=int64))
        """
        return len(loc[0])


    # 找图 返回最近似的点
    def search_picture(self):

        # self.target_img = cv2.imread('1630232776674203196.jpg')#要找的大图
        # img = cv2.resize(img, (0, 0), fx=self.scale, fy=self.scale)

        img_gray = cv2.cvtColor(self.target_img, cv2.COLOR_BGR2GRAY)

        self.result = cv2.matchTemplate(img_gray, self.temp, cv2.TM_CCOEFF_NORMED)
        logger.info(f"{self.result=}")

        # cv2.imwrite(f"{time.time_ns()}-img.PNG", img_gray)

        loc = np.where(self.result >= self.threshold)

        # 使用灰度图像中的坐标对原始RGB图像进行标记
        point = ()
        for pt in zip(*loc[::-1]):
            # 在图像上绘制一个矩形。
            # 参数img是要绘制矩形的图像，pt1和pt2是矩形的对角线顶点，color是矩形的颜色，thickness是矩形边框的粗细。
            cv2.rectangle(img_gray, pt, (pt[0] + self.template_size[1], pt[1] + self.template_size[0]), (7, 249, 151), 2)
            point = pt

        if point==():
            return None,None,None
        
        return img_gray, point[0]+ self.template_size[1]/2, point[1]


# 创建顶级组件容器
class AutoFishing:

    # 创建tkinter主窗口 # 初始化窗口，配置相关
    def __init__(self):

        # mouse click <right>
        # click_right is function()
        self.mouse = Mouse()

        self.root = tk.Tk()
        self.root.title("自动钓鱼AI")

        # 运行状态
        self._pregess = "-"

        # 设置应用图标
        # self.root.iconbitmap(str(tk.PhotoImage(ICON)))
        self.root.iconphoto(True, tk.PhotoImage(file=ICON))

        # 不允许改变窗口大小
        # root.resizable(False, False)

        # self.top.minsize(100, 50)

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        logger.debug(f"检测到屏幕大小: {self.screen_w} {self.screen_h}")

        # 指定主窗口位置与大小
        self.root.geometry(f"+{round(self.screen_w/5)}+{round(self.screen_h/5)}")



        # self.top.overrideredirect(True)
        # self.game_resolution.overrideredirect(True)

        # self.top.attributes('-alpha', 0.2)

        # self.top.attributes("-topmost", True) 
        # print("grame_resolution topmost: ", self.game_resolution.attributes("-topmost"))

        self.frame = ttk.Frame(self.root)
        self.frame.pack()

        l1 = ttk.Label(self.frame, text="选择模式：")
        l1.grid(row=0, column=0)

        # select 框
        self.selectors = ["850x480(推荐)", "1920x1080", "其他模式"]
        self.selected = ttk.Combobox(self.frame, values=self.selectors, state="readonly")
        self.selected.bind("<<ComboboxSelected>>", self.selectmode)
    
        
        # check Conf
        self.conf = Conf()
        if self.conf.chekc_conf:
            self.conf.load()
            self.index = self.conf.index
            self.win_pos = self.conf.win_pos
            self.template = self.conf.template
            self.screen_pos = self.conf.screen_pos

            self.selected.current(self.index)
        else:
            self.index = 0
            self.win_pos = "850x480"
            self.template = str(TEMPLATE_PATH)
            self.screen_pos = (700, 300, 150, 160)

            self.conf.save(0, self.template, self.win_pos, self.screen_pos)
            self.selected.current(0)

        self.selected.grid(row=0, column=1)

        # 设置游戏对齐窗口, 
        self.game_resolution = tk.Toplevel(self.root)
        self.game_resolution.title("MC 匹配窗口")

        # 查看之前的配置里有保存位置没有。
        self.game_resolution.geometry(self.win_pos)
        self.game_resolution.resizable(False, False)
        self.game_resolution.attributes('-alpha', 0.2)

        # self.game_resolution.destroy()
        # 禁止关闭提示窗口, 方式一
        self.game_resolution.protocol("WM_DELETE_WINDOW", lambda : None)

        # label = tk.Label(self.game_resolution, text="把游戏窗口调整为和这个窗口一样大，在点开始。", bg="#f21312")
        # label.pack(fill=tk.BOTH, expand="y")


        # 如果没有配置说明是初始化，需要把窗口移到中间。
        if not self.conf.chekc_conf:
            x, y = self.win_pos.split("x")
            logger.debug(f"x, y: {x}, {y}")
            self.winCenter(self.game_resolution, int(x), int(y))


        # game_resoultion
        # label = tk.Label(self.game_resolution, bg="#1122cc", borderwidth=5)
        label = ttk.Label(self.game_resolution, background="#1122cc", borderwidth=5)
        label.pack(fill=tk.BOTH, expand="yes")
        # label.bind("<B1-Motion>", lambda e: self.Resize(e, self.game_resolution))

        """
        改为新方式：使用提示窗口+从文本里读取说明内容。
        label2 = ttk.Label(label, text=MC_PROMPT, borderwidth=5)
        """

        label2 = ttk.Label(label, borderwidth=5)
        label2.pack(fill=tk.BOTH, expand="yes", padx=5, pady=5)
        label2.bind("<Button-1>", self.mouseDown)
        # label2.bind("<B1-Motion>", lambda e: self.moveWin(e, self.game_resolution))



        self.run_lock = Lock()
        
        # 重新开始计数
        self.reset_fishingcount = Lock()

        # self.addButton("开始", lambda e: self.start())
        # self.addButton("停止", lambda e: self.stop())

        # start stop
        self.start_stop_var = tk.StringVar()
        self.start_stop_var.set("开始")
        self.start_stop_btn = ttk.Button(self.frame, textvariable=self.start_stop_var)
        self.start_stop_btn.bind("<Button-1>", lambda e: self.start())
        self.start_stop_btn.grid(row=0, column=2)
        # self.frame_start_stop.pack()

        self.fishcount = 0
        self.fishingspeed = 0
        self.avg_speed = 0
        self.speed = []
        self.fishingspeed_timestamp = time.time()
        self.fishcount_var = tk.StringVar()
        self.fishcount_string = "钓鱼平均速度为：{} s/条，本次已经钓到 {} 条鱼"
        self.fishcount_var.set(self.fishcount_string.format(self.fishingspeed, self.fishcount))
        fishcount_label = ttk.Label(self.root, textvariable=self.fishcount_var)
        fishcount_label.pack()

        # 添加重新计数 btn
        self.clear_fishingcount = ttk.Button(self.root, text="重计钓鱼数")
        self.clear_fishingcount.bind("<Button-1>", lambda e: self.clear_fishingcount_func())
        self.clear_fishingcount.pack()

        # fps 
        fps_frame = ttk.Frame(self.root)
        fps_frame.pack()

        validate_cmd = self.root.register(self.__check_entry_input)

        label_fps = ttk.Label(fps_frame, text="FPS:")
        label_fps.grid(row=0, column=0)

        self.label_fps = ttk.Entry(fps_frame, width=4, validate="key", validatecommand=(validate_cmd, "%P"))
        self.label_fps.insert(0, FPS)
        self.label_fps.grid(row=0, column=1)

        # 使用说明
        # help_info_frame = ttk.Frame(self.root)
        # help_info_frame.pack()

        help_info_btn = ttk.Button(self.root, text="使用说明", command=self.__help_info)
        help_info_btn.pack(side="right")

        self._help_info = False


    def __check_entry_input(self, value):
        if value.isnumeric() or value == "":
            if len(value) <= 4:
                return True
            else:
                return False
        else:
            return False

    def addButton(self, text, func):
        # 上个按钮
        btn1 = ttk.Button(self.root, text=text)
        btn1.bind("<Button-1>", func)
        btn1.pack()
    
    def clear_fishingcount_func(self):
        logger.debug(f"重置计数")
        with self.reset_fishingcount:
            self.fishcount = 0
            self.fishingspeed = 0
            self.avg_speed = 0
            self.fishcount_var.set(self.fishcount_string.format(self.avg_speed, self.fishcount))

    def __help_info(self):
        # 这个点几次就会执行几次，需要打个标判断一下。
        if self._help_info:
            pass
        else:
            help_window = tk.Toplevel(self.root)
            help_window.title("使用说明")
            self._help_info = True

            def func_tmp():
                self._help_info = False
                logger.info(f"{self._help_info=}")
                help_window.destroy()


            help_window.protocol("WM_DELETE_WINDOW", func_tmp)

            label_text = ttk.Label(help_window, text=HELP_INFO)
            label_text.pack()

        # 这种方式，必须关闭了这个提示窗口才能点击开始。
        # messagebox.showinfo(title="使用说明", message=HELP_INFO)


    def mainloop(self):
        self.root.mainloop()
    

    def selectmode(self, event):
        value = self.selected.get()
        logger.info(f"切换模式: {value}")
        logger.debug(f"切换模式: {event} value: {value}")

        if value == "850x480(推荐)":
            self.index = 0
            self.template = Path("images") / "mc-fishing_850x480.png"
            self.win_pos = "850x480"
            self.screen_pos = (700, 300, 150, 160) # 左上角坐标，和截图的长宽。

            self.game_resolution.resizable(True, True)
            self.game_resolution.geometry(self.win_pos)
            self.game_resolution.resizable(False, False)
            self.game_resolution.attributes('-alpha', 0.2)
            tmp = self.win_pos.split("+")[0]
            x, y = tmp.split("x")
            self.winCenter(self.game_resolution, int(x), int(y))

            self.conf = Conf()
            self.conf.save(self.index, self.template, self.game_resolution.winfo_geometry(), self.screen_pos)

        elif value == "1920x1080":
            self.index = 1
            self.template = Path("images") / "mc-fishing_1920x1080_1.18.png"
            self.win_pos = "1920x1080"
            # self.screen_pos = (1600, 630, 1050, 980)
            # self.screen_pos = (1600, 630, 310, 430)
            self.screen_pos = (1600, 560, 300, 430)

            self.game_resolution.resizable(True, True)
            self.game_resolution.geometry(self.win_pos)
            self.game_resolution.resizable(False, False)
            self.game_resolution.attributes('-alpha', 0.2)
            tmp = self.win_pos.split("+")[0]
            x, y = tmp.split("x")
            self.winCenter(self.game_resolution, int(x), int(y))

            self.conf = Conf()
            self.conf.save(self.index, self.template, self.game_resolution.winfo_geometry(), self.screen_pos)

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
    

    def fishshow(self, interval):
        """
        interval: 上次出杆到这次收杆的时间间隔
        """
        self.fishcount += 1
        # self.fishingspeed = round(cur - self.fishingspeed_timestamp, 4)
        self.fishingspeed = round(interval, 4)
        logger.debug(f"上次钓鱼速度：{self.fishingspeed}s/条")

        # 如果是正常钓鱼，不是暂停，钓鱼时间应该会小于45s
        if self.fishingspeed <= 45:

            # 计数20次后，重新开始计算钓鱼速度。
            if len(self.speed) > 20:
                self.speed = [self.fishingspeed]
            else:
                self.speed.append(self.fishingspeed)

            self.avg_speed  = round(sum(self.speed) / len(self.speed), 1)

        self.fishcount_var.set(self.fishcount_string.format(self.avg_speed, self.fishcount))

        # self.fishingspeed_timestamp = cur
    
    
    def start(self):
        if self.run_lock.locked():
            self.start_stop_var.set("开始")
            self.run_lock.release()

            # 显示窗口
            # self.top.deiconify()
            self.game_resolution.deiconify()

            logger.info(f"stoping... {self.th.name}")

        else:
            # 隐藏窗口
            self.game_resolution.withdraw()

            logger.info("start ...")
            self.start_stop_var.set("暂停")
            self.run_lock.acquire()

            # 拿到游戏屏幕位置
            game_geometry = self.game_resolution.winfo_geometry()
            logger.info(f"拿到游戏屏幕位置: {game_geometry}")

            # 查看窗口位置变化。
            if self.win_pos != game_geometry:
                self.conf.save(self.index, self.template, game_geometry, self.screen_pos)

            w, tmp = game_geometry.split("x")
            h, x, y = tmp.split("+")

            self.game_position = (int(x), int(y))

            # 根据 game_position 位置，算出 目标图像在屏幕中的位置
            # temp_x1, temp_y1 = self.game_position[0] + 700, self.game_position[1] + 300
            # temp_x2, temp_y2 = temp_x1 + 150, temp_y1 + 160
            temp_x1, temp_y1 = self.game_position[0] + self.screen_pos[0], self.game_position[1] + self.screen_pos[1]
            temp_x2, temp_y2 = temp_x1 + self.screen_pos[2], temp_y1 + self.screen_pos[3]


            self.screenshot_pos = (temp_x1, temp_y1, temp_x2, temp_y2)
            logger.debug(f"截图位置: {self.screenshot_pos}")

            # 这个必须在子线程里面实例化
            # self.BF = BaitFish(self.screenshot_pos, str(self.template))
            self.th = Thread(target=self.run, daemon=True)
            self.th.start()
            logger.info(f"{self.th.name} 开始运行 ...")

    
    def pregess(self):
        print(self._pregess + "\r", end="", flush=True)
        if self._pregess == "-":
            self._pregess = "\\"
        elif self._pregess == "\\":
            self._pregess = "|"
        elif self._pregess == "|":
            self._pregess = "/"
        elif self._pregess == "/":
            self._pregess = "-"
        else:
            self._pregess = "-"
    
    def run(self):

        BF = BaitFish(self.screenshot_pos, str(self.template))

        fps = int(self.label_fps.get())
        logger.debug(f"FPS：{fps}")
        BF.set_fps(fps)

        # 如果超过60s 还没有收杆，可以是钩到水里的实体了。需要先下杆。
        fishing_timeout_flag = time.time()

        alarm_time = fishing_timeout_flag

        fishing_time = alarm_time

        while self.run_lock.locked():

            start = time.time()

            # 如果超过60s 还没有收杆，可能是钩到水里的实体了。需要先收一下杆。
            if (start - fishing_timeout_flag) > 60:
                fishing_timeout_flag = start
                logger.debug(f"超1分钟没有上钩了，收一下杆。")
                self.mouse.click_right()
                time.sleep(0.5)
                self.mouse.click_right()


            # BF.screenshot()
            BF.screenshot_mss()

            # img, x, y = BF.search_picture()
            # find_img = BF.search_one_picture()
            find_img_count = BF.search_more_picture()

            end = time.time()

            t = round(end - start, 3)
            # if img is None:
            if find_img_count == 0:
                self.pregess()

                if fps == 0:
                    interval = 0
                else:
                    interval = 1/fps -  t

                if interval >= 0:
                    time.sleep(interval)
                else:
                    # 每10s钟才输出一次警告信息
                    cur = time.time()
                    if (cur - alarm_time) > 10.0:
                        alarm_time = cur
                        logger.warning(f"{t}/s 当前机器性能不足，可能错过收竽时机。")
                
            else:

                fishing_timeout_flag = time.time()

                # 如果钓鱼速度快于3s/条，需要等待到3s, 在出下一次杆.
                # 上次收杆到下次出杆之间至少需要有3秒间隔

                # 上次出杆到这次收杆的日间间隔。
                t3 = fishing_timeout_flag - fishing_time

                if find_img_count == 1 and t3 > 3.0:
                    pass
                elif find_img_count > 1 and t3 < 3.0:
                    pass
                else:
                    continue

                self.fishshow(t3)

                # 收鱼竿
                logger.info("收鱼竿")
                self.mouse.click_right()

                # 这里是等待上次的，“浮漂：溅起水花” 从字幕里退出。
                # time.sleep(3)

                time.sleep(0.5) 

                logger.debug("出鱼竿")
                self.mouse.click_right()
                fishing_time = time.time()


        th = threading.current_thread()
        print(th.name, "退出...")
        if self.run_lock.locked():
            self.run_lock.release()
        # cv2.destroyAllWindows()

        BF.mss_close()



# main
def main():
    import argparse

    parse = argparse.ArgumentParser(usage="%(prog)s --fps <fps>")
    parse.add_argument("--fps", type=int, default=10, help="检测速度, 0: 以机器最高速度运行。(default: 10)")
    parse.add_argument("--debug", action="store_true", help="debug")

    args = parse.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("deubg 模式")

    global FPS
    if args.fps:
        FPS = args.fps

    fishing = AutoFishing()
    fishing.mainloop()


if __name__ == "__main__":
    main()
