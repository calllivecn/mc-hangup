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

# 窗口图标
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
            elif not self.__use_xdotool():
                sys.exit(1)
            elif not self.__use_pyautogui():
                sys.exit(1)
            else:
                logger.error(f"没有支持鼠标方案")
                sys.exit(1)

        else:
            logger.info("你的桌面环境是 X11 的~")
            if not self.__use_pyautogui():
                sys.exit(1)
            elif not self.__use_xdotool():
                sys.exit(1)
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
