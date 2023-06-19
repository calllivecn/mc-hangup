#!/usr/bin/env python3
# coding=utf-8
# date 2023-06-19 22:30:06
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
import mss
import numpy as np


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

def runtime(func):
    def wrap(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        logger.log(DEBUG2, f"{func.__name__} 的运行耗时: {t2-t1} /秒")
        return result
    
    return wrap


# 使用说明
try:
    with open("usage.txt") as f:
        HELP_INFO=f.read()
except FileNotFoundError:
    logger.error("是不是删除了数据文件: usage.txt")
    sys.exit(1)

DEBUG2 = 5

# 默认检测帧率
FPS = 10

# 窗口图标
ICON = Path("images") / "icon.png"

# 窗口初始化默认，模板。
TEMPLATE_PATH = Path("images") / "mc-fishing_850x480_1.18.png"


class Conf:
    """
    ~~这玩意有bug,不能保存左上角坐标。改成左下角坐标，然后推算左上解坐标。~~
    1. 在初始化时，就检测有没有保存的配置。
    2. update() 时，自己对比，看看是否需要更新文件。
    """

    def __init__(self, savefile="data.json"):
        if savefile != Path:
            self.savefile = Path(savefile)
        else:
            self.savefile = savefile
        
        # 如果没有，则初始化。
        if self.savefile.exists():
            self.load()
            self.isdefault = False
        else:
            # init
            self.isdefault = True

            self.index = 0
            self.win_pos = "850x480"
            self.template = str(TEMPLATE_PATH)
            self.screen_pos = (700, 300, 150, 160)

            self._d = {
                "index": self.index,
                "template": str(self.template),
                "win_pos": self.win_pos,
                "screen_pos": self.screen_pos, # 截图相对游戏窗口的位置
            }

            self.save()
    

    def load(self):

        try:
            with open(self.savefile, "r") as f:
                self._d = json.load(f)
        except Exception:
            return False

        self.index = self._d["index"]
        self.template = self._d["template"]
        # 例：win_pos = 850x480+700+300
        self.win_pos = self._d["win_pos"]
        # 是相对于 win_pos 的位置，和 模板本身的长宽 例：(700, 300, 150, 160)
        self.screen_pos = self._d["screen_pos"]

        return True

    def save(self):
        
        with open(self.savefile, "w") as f:
            json.dump(self._d, f)
        
        return True
    
    def update(self, index, template, win_pos, screen_pos):
        updated = False
        if self.index != index:
            self.index = index
            updated = True
        
        if self.template != template:
            self.template = template
            updated = True

        if self.win_pos != win_pos:
            self.win_pos = win_pos
            updated = True
        
        if self.screen_pos != screen_pos:
            self.screen_pos = screen_pos
            updated = True
        
        if updated:
            self.save()


class Mouse:

    def __init__(self):

        # 声明
        self.autotool = None

        # default usage
        if sys.platform == "linux":
            self.check_in_linux()    

        elif sys.platform == "win32":
            self.check_in_windows()

        else:
            logger.error("你的系统还没支持哦～")
            sys.exit(1)


    def click_right(self):
        self.autotool()
    
    def close(self):
        self.sock.close()
    
    
    # 平台检测+依赖检查
    def check_in_linux(self):
        logger.debug("当前操作系统 linux")
        if "wayland" in os.getenv("XDG_SESSION_TYPE").lower():
            logger.info("你的桌面环境是 wayland")
            if not self.__use_mouse():
                sys.exit(1)
            elif not self.__use_xdotool() or not self.__use_pyautogui():
                sys.exit(1)
            else:
                logger.error(f"没有支持鼠标方案")
                sys.exit(1)

        else:
            logger.info("你的桌面环境是 X11 的~")
            if self.__use_pyautogui() or self.__use_xdotool():
                pass
            else:
                logger.error(f"没有支持鼠标方案")
                sys.exit(1)


    def check_in_windows(self):
        logger.debug("当前操作系统 windows")
        if not self.__use_pyautogui():
            sys.exit(1)


    def __use_mouse(self) -> bool:
        """
        使用 mouse.py 鼠标方案。
        成功返回True, 失败返回False
        """
        try:
            import mouse
        except ModuleNotFoundError:
            logger.error(f"需要安装keyboardmouse模块,地址：https://github.com/calllivecn/keyboardmouse")
            return False
    
        logger.info("使用 mouse.py 方案")

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

        return True
    
    def __use_xdotool(self) -> bool:
        """
        使用 xdotool 鼠标方案。
        成功返回True, 失败返回False
        """
        try:
            result = subprocess.run("type -p xdotool".split(), shell=True, stdout=subprocess.PIPE)
            result.check_returncode()
            self.autotool = lambda : subprocess.run("xdotool click 3".split(), stdout=subprocess.PIPE)
            logger.info("使用 xdotool 方案")
            return True
        except Exception as e:
            logger.warning("没有找到 xdotool 需要安装。")
            # raise e
            return False


    def __use_pyautogui(self) -> bool:
        """
        使用 xdotool 鼠标方案。
        成功返回True, 失败返回False
        """
        try:
            import pyautogui
            self.autotool = lambda : pyautogui.rightClick()
            logger.info("使用 pyautogui 方案")
            return True
        except ModuleNotFoundError:
            logger.warning("没有找到 pyautogui 需要安装。")
            return False


class BaitFish:

    def __init__(self, position, img_template, fps, threshold=0.75):

        self.threshold = threshold

        p_img_template = Path(img_template)
        if not p_img_template.exists():
            logger.error("模板图片不存在。。。。")
            sys.exit(2)

        self.fps = fps

        # 找到的图像的像素值和, init
        self.img_light = 0

        #图中的小图
        self.template = cv2.imread(img_template)

        # position: (200, 200, 400, 500) 
        self.position = position

        # 拿到模板图片大小
        self.template_size = self.template.shape
        # h,w,c = template_size

        logger.debug(f"template_size 1 : {self.template_size}")

        self.temp = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)

        # 初始化截图库
        self.mss_shot = mss.mss()


    def mss_close(self):
        self.mss_shot.close()


    # 获取屏幕指定位置的截图(新版库，性能高)
    @runtime
    def screenshot_mss(self):
        img = self.mss_shot.grab(self.position)
        self.shot_img = np.asanyarray(img)
        self.target_img = cv2.cvtColor(self.shot_img, cv2.COLOR_RGB2BGR)
        return self.target_img


    @runtime
    def search_one_picture(self) -> bool:
        self.screenshot_mss()

        img_gray = cv2.cvtColor(self.target_img, cv2.COLOR_BGR2GRAY)

        self.result = cv2.matchTemplate(img_gray, self.temp, cv2.TM_CCOEFF_NORMED)
        # 返回的是 ([x1, ...], [y1, ...])

        loc = np.where(self.result >= self.threshold)
        """
        loc：
        在匹配结果数组self.result中查找大于或等于阈值self.threshold的元素。
        该函数返回一个元组，其中包含两个数组，分别表示满足条件的元素的行和列索引。
        """

        # 第一个
        h1, w2 = loc
        h, w, c = self.template_size
        logger.log(DEBUG2, f"这是: {h1=} {w2=} {w=} {h=} {loc=}")

        # loc: 是这样的 loc=(array([], dtype=int64), array([], dtype=int64))
        if len(loc[0]) >= 1:
            h1, w2 = h1[0], w2[0]
            n = self.target_img[h1:h1+h, w2:w2+w]
            self.img_light = np.sum(n)
            """
            filename = "/".join(["debug", str(time.time_ns()) + ".png"])
            logger.debug(f"{n.shape=} 保存下: {filename=}")
            cv2.imwrite(filename, n)
            """
            return True
        else:
            return False

    @runtime
    def search_more_picture(self) -> int:
        img_gray = cv2.cvtColor(self.target_img, cv2.COLOR_BGR2GRAY)

        self.result = cv2.matchTemplate(img_gray, self.temp, cv2.TM_CCOEFF_NORMED)
        # 返回的是 ([x1, ...], [y1, ...])

        loc = np.where(self.result >= self.threshold)
        # loc: 是这样的 loc=(array([], dtype=int64), array([], dtype=int64))
        return len(loc[0])



# 创建顶级组件容器
class AutoFishing:

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

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        logger.info(f"检测到屏幕大小: {self.screen_w} {self.screen_h}")

        # 指定主窗口位置与大小
        self.root.geometry(f"+{round(self.screen_w/5)}+{round(self.screen_h/5)}")

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
        """
        if self.conf.chekc_conf:
            self.conf.load()
            self.index = self.conf.index
            self.win_pos = self.conf.win_pos
            self.template = self.conf.template
            self.screen_pos = self.conf.screen_pos

        else:
            self.index = 0
            self.win_pos = "850x480"
            self.template = str(TEMPLATE_PATH)
            self.screen_pos = (700, 300, 150, 160)

            self.conf.save(0, self.template, self.win_pos, self.screen_pos)
        """

        self.selected.current(self.conf.index)
        self.selected.grid(row=0, column=1)

        # 设置游戏对齐窗口, 
        self.game_resolution = tk.Toplevel(self.root)
        self.game_resolution.title("MC 匹配窗口")
        self.game_resolution.update()

        # 查看之前的配置里有保存位置没有。
        self.game_resolution.geometry(self.conf.win_pos)
        self.game_resolution.resizable(False, False)
        self.game_resolution.attributes('-alpha', 0.5)

        # self.game_resolution.destroy()
        # 禁止关闭提示窗口, 方式一
        self.game_resolution.protocol("WM_DELETE_WINDOW", lambda : None)


        # 如果没有配置说明是初始化，需要把窗口移到中间。
        if self.conf.isdefault:
            x, y = self.conf.win_pos.split("x")
            logger.debug(f"x, y: {x}, {y}")
            self.winCenter(self.game_resolution, int(x), int(y))


        # game_resoultion
        # label = tk.Label(self.game_resolution, bg="#1122cc", borderwidth=5)
        label = ttk.Label(self.game_resolution, background="#1122cc", borderwidth=5)
        label.pack(fill=tk.BOTH, expand="yes")
        # label.bind("<B1-Motion>", lambda e: self.Resize(e, self.game_resolution))

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
            index = 0
            template = Path("images") / "mc-fishing_850x480.png"
            win_pos = "850x480"
            screen_pos = (700, 300, 150, 160) # 左上角坐标，和截图的长宽。

            self.game_resolution.resizable(True, True)
            self.game_resolution.geometry(win_pos)
            self.game_resolution.resizable(False, False)
            self.game_resolution.attributes('-alpha', 0.5)
            tmp = win_pos.split("+")[0]
            x, y = tmp.split("x")
            self.winCenter(self.game_resolution, int(x), int(y))

            self.conf.update(index, template, self.game_resolution.winfo_geometry(), screen_pos)

        elif value == "1920x1080":
            index = 1
            template = Path("images") / "mc-fishing_1920x1080_1.18.png"
            win_pos = "1920x1080"
            # screen_pos = (1600, 630, 1050, 980)
            # screen_pos = (1600, 630, 310, 430)
            screen_pos = (1600, 560, 300, 430)

            self.game_resolution.resizable(True, True)
            self.game_resolution.geometry(win_pos)
            self.game_resolution.resizable(False, False)
            self.game_resolution.attributes('-alpha', 0.5)
            tmp = win_pos.split("+")[0]
            x, y = tmp.split("x")
            self.winCenter(self.game_resolution, int(x), int(y))

            self.conf.update(index, template, self.game_resolution.winfo_geometry(), screen_pos)

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
            if self.conf.win_pos != game_geometry:
                self.conf.update(self.conf.index, self.conf.template, game_geometry, self.conf.screen_pos)

            w, tmp = game_geometry.split("x")
            h, x, y = tmp.split("+")

            self.game_position = (int(x), int(y))

            # 根据 game_position 位置，算出 目标图像在屏幕中的位置
            temp_x1, temp_y1 = self.game_position[0] + self.conf.screen_pos[0], self.game_position[1] + self.conf.screen_pos[1]
            temp_x2, temp_y2 = temp_x1 + self.conf.screen_pos[2], temp_y1 + self.conf.screen_pos[3]


            self.screenshot_pos = (temp_x1, temp_y1, temp_x2, temp_y2)
            logger.debug(f"截图位置: {self.screenshot_pos}")

            # 这个必须在子线程里面实例化
            # self.BF = BaitFish(self.screenshot_pos, str(self.template))
            self.th = Thread(target=self.run, daemon=True)
            self.th.start()
            logger.info(f"{self.th.name} 开始运行 ...")

    
    def pregess(self):
        print(self._pregess*20 + "\r", end="", flush=True)
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

        fps = int(self.label_fps.get())
        logger.debug(f"FPS：{fps}")
        BF = BaitFish(self.screenshot_pos, str(self.conf.template), fps)

        # 如果超过60s 还没有收杆，可以是钩到水里的实体了。需要先下杆。
        fishing_timeout_flag = time.time()

        alarm_time = fishing_timeout_flag

        fishing_time = alarm_time

        img_light = 0

        while self.run_lock.locked():
            self.pregess()

            start = time.time()
            # 如果超过60s 还没有收杆，可能是钩到水里的实体了。需要先收一下杆。
            if (start - fishing_timeout_flag) > 60:
                fishing_timeout_flag = start
                logger.debug(f"超1分钟没有上钩了，收一下杆。")
                self.mouse.click_right()
                time.sleep(0.5)
                self.mouse.click_right()

            find_img_count = BF.search_one_picture()

            end = time.time()

            # 截图+找图,消耗时间
            t = round(end - start, 3)

            def check_perf():
                interval = round(1/fps - t, 4)
                if interval > 0:
                    time.sleep(interval)
                else:
                    # 每10s钟才输出一次警告信息
                    cur = time.time()
                    if (cur - alarm_time) > 10.0:
                        alarm_time = cur
                        logger.warning(f"{t}/s 当前机器性能不足，可能错过收竽时机。")
            
            if find_img_count == 0:
                check_perf()
                
            else:

                fishing_timeout_flag = time.time()

                # 如果钓鱼速度快于3s/条，需要等待到3s, 在出下一次杆.
                # 上次收杆到下次出杆之间至少需要有3秒间隔

                """
                新的思路：如果这次找到的图片，亮度比上次高就说明，“浮漂：溅起水花” 从字幕里更新了(就是有鱼了)。
                """
                cmp = (BF.img_light / (img_light + 1))
                truefalse = cmp > 1.1
                logger.log(DEBUG2, f"打到的模板图像的亮度值：{img_light=} {BF.img_light=} {cmp=}")
                # 更新
                img_light = BF.img_light

                if truefalse:
                    # 上鱼了
                    pass
                else:
                    check_perf()
                    continue


                # 上次出杆到这次收杆的日间间隔。
                t3 = fishing_timeout_flag - fishing_time

                """
                if find_img_count == 1 and t3 > 3.0:
                    pass
                elif find_img_count > 1 and t3 < 3.0:
                    pass
                else:
                    check_perf()
                    continue
                """

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


def main():
    import argparse

    parse = argparse.ArgumentParser(usage="%(prog)s [--option]")
    parse.add_argument("-v", "--verbose", action="count", help="debug")

    args = parse.parse_args()

    if args.verbose == 1:
        logger.setLevel(logging.DEBUG)
        logger.debug("deubg 模式")

    elif args.verbose == 2:
        logger.setLevel(DEBUG2)
        logger.log(DEBUG2, "deubg2 模式")
    else:
        logger.setLevel(logging.INFO)

    fishing = AutoFishing()
    fishing.mainloop()


if __name__ == "__main__":
    main()
