#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-08 14:29:15
# author calllivecn <c-all@qq.com>

import os
import re
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path
from threading import Lock

from pprint import pprint

from mcdreforged import config
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer
from mcdreforged.permission.permission_level import PermissionLevel

PLUGIN_METADATA = {
    # ID（即插件ID）是您插件的身份字符串。它应该由小写字母，数字和下划线组成，长度为1到64
    'id': 'backup', 
    'version': '0.1.0',
    'name': '服务端自动备份工具(rsync)',
    'author': [
        'calllivecn'
   ],
    'link': 'https://github.com/calllivecn/mc-hangup',
    'dependencies': {
        'mcdreforged': '>=1.3.0',
    }
}

cmdprefix = "." + "bak"

cur_dir = Path(os.path.dirname(os.path.dirname(__file__)))

config_file = cur_dir / "config" / "backup.json"

# 默认目录 和 备份路径(相对mcdr的路径)
BACKUP_DIR = Path("backup")
AUTOBACKUP_DIR = BACKUP_DIR / "autobackup"
WORLD_DIR = Path("server") / "world"
BACKUP_INFO = BACKUP_DIR / "backupinfo.json"

# 配置文件

CFG = {
    "world_dir": str(WORLD_DIR),
    "backup_dir": str(BACKUP_DIR),
    "backup_interval": 30 * 60,
    "backup_seq": [1, 2, 2, 4, 3],
}

def read_cfg(server):
    global BACKUP_DIR
    global WORLD_DIR
    global AUTOBACKUP_DIR
    global CFG

    if config_file.exists():
        with open(config_file) as f:
            CFG = json.load(f)

            BACKUP_DIR = Path(CFG["backup_dir"])
            WORLD_DIR = Path(CFG["world_dir"])

    else:
        with open(config_file, "w") as f:
            json.dump(CFG, f, ensure_ascii=False, indent=4)

    # init
    if not BACKUP_DIR.exists():
        os.makedirs(BACKUP_DIR)
    
    # init autobackup 目录
    # if not AUTOBACKUP_DIR.exists():
        # os.makedirs(AUTOBACKUP_DIR)
    
    return True


# 给一个锁
class BackupInternal:
    def __init__(self):
        self._lock = Lock()
        self._internal = 0

    @property    
    def value(self):
        with self._lock:
            return self._internal
    
    @value.setter
    def value(self, value):
        with self._lock:
            self._internal = value
    
    def locked(self):
        return self._lock.locked()
    
    def __enter__(self):
        self._lock.acquire()
    

    def __exit__(self, typ, value, traceback):
        self._lock.release()


SAVED_THE_GAME = Lock()
PLUGIN_RELOAD = False
B = BackupInternal()
backing = Lock()

def permission(func):

    def warp(*args, **kwargs):
        # print(f"*args {args}  **kwargs {kwargs}", file=sys.stdout)
        server, info = __get(args[0])
        perm = server.get_permission_level(info)

        # print(f"warp(): {args} {kwargs}", file=sys.stdout)
        if perm >= PermissionLevel.USER:
            func(*args, **kwargs)
 
    return warp


def __get(src):
    return src.get_server(), src.get_info()


### 定义 


def backup2current(source, target):
    if not source.endswith("/"):
        source = source + "/"
    
    print(f"rsync: {source} ==> {target}")
    try:
        # subprocess.check_call(["rsync", "-av", "--delete", source, target])
        subprocess.check_call(["rsync", "-a", "--delete", source, target])
    except FileNotFoundError as e:
        raise e
    except Exception as e:
        raise e



class BackInfo:

    def __init__(self, server):

        self.server = server

        self.cur_timestamp = time.strftime("%Y-%m-%d_%H:%M:%S")

        self.backup_seq = CFG["backup_seq"]
        self.backup_info = BACKUP_DIR / "backupinfo.json"

        self.backup_list = []
        self.rollback_last = {"timestamp": "", "msg": ""}

        # 读写备份信息的锁
        self.__rw = Lock()


        # 初始化bak目录
        for i in range(len(self.backup_seq)):
            bak = BACKUP_DIR / f"bak-{i}"
            if not bak.exists():
                bak.mkdir()

            self.backup_list.append({"value": self.backup_seq[i] - 1, "timestamp": "", "msg":""})
            

        if BACKUP_INFO.exists():
            self.__read()
        else:
            self.__write()

    
    def list(self):
        ls = []

        for d in self.backup_list:
            ls.append((d["timestamp"], d["msg"]))
        
        if self.rollback_last["timestamp"] == "":
            return ls, None
        else:
            return ls, (self.rollback_last["timestamp"], self.rollback_last["msg"])
        
    
    def __update(self, msg):
        """
        更新 value archivename
        return 要被删除的 archivename, 没有 return ""
        """

        cur = self.cur_timestamp
        cur_msg = msg

        baks = []

        seq_len = len(self.backup_list)
        print("self.backup_list ==> ")
        pprint(self.backup_list)

        # 从第2个开始，算起
        for i in range(seq_len):

            self.backup_list[i]["value"] += 1

            if self.backup_seq[i] <= self.backup_list[i]["value"]:
                self.backup_list[i]["value"] = 0

                self.backup_list[i]["timestamp"], cur = cur, self.backup_list[i]["timestamp"]
                
                #update 备份注释
                self.backup_list[i]["msg"], cur_msg = cur_msg, self.backup_list[i]["msg"]

                # 准备执行备份递进
                baks.append(BACKUP_DIR / f"bak-{i}")
            else:
                # if self.backup_list[i]["timestamp"] != "" and cur != self.backup_list[i]:
                    # baks.append(BACKUP_DIR / f"bak-{i}")
                break

        print("self.backup_list ==> 执行后 ")
        pprint(self.backup_list)

        baks_stack = []
        if len(baks) >= 2:
            a = baks[1:]
            b = baks[:-1]
            a.reverse()
            b.reverse()

            baks_stack = list(zip(b, a))

        print("baks_stack ==> ")
        pprint(baks_stack)

        for src, target in baks_stack:
            self.__baks(src, target)


        self.__write()


    def rollback(self, number):
        tm = self.backup_list[number]["timestamp"]
        msg = self.backup_list[number]["msg"]

        if msg == "":
            self.server.say(RText(f"服务器30s 后回滚到：{tm}", RColor.green))
        else:
            self.server.say(RText(f"服务器30s 后回滚到：{tm} 注释： {msg}", RColor.green))
        
        time.sleep(25)
        
        for i in range(5, 1, -1):
            if msg == "":
                self.server.say(RText(f"服务器{i}s 后回滚到：{tm}", RColor.green))
            else:
                self.server.say(RText(f"服务器{i}s 后回滚到：{tm} 注释： {msg}", RColor.green))
        
        
        if self.server.is_server_running():
            self.server.logger.info("关闭服务器中...")
            self.server.stop()
            self.server.wait_for_start()
            self.server.logger.info("等待服务器，关闭后，执行回滚.")
        else:
            self.server.logger.info("服务器没有运行")
            return

        
        rollback_dir = BACKUP_DIR/"rollback"
        if rollback_dir.exists():
            shutil.rmtree(str(rollback_dir))

        try:
            shutil.move(str(WORLD_DIR), str(rollback_dir))
            backup2current(str(BACKUP_DIR/f"bak-{number}"), str(WORLD_DIR))
        except Exception as e:
            raise e
        
        # 更新 BackInfo
        self.rollback_last["timestamp"] = time.strftime("%Y-%m-%d_%H:%M:%S")
        self.rollback_last["msg"] =  msg
        self.__write()
        
        self.server.start()



    def __read(self):

        with self.__rw:

            with open(BACKUP_INFO, "r") as f:
                j = json.load(f)

            self.backup_list = j["backup_list"]
            self.rollback_last = j["rollback_last"]
        
    def __write(self):
        with self.__rw:
            with open(BACKUP_INFO, "w") as f:
                j = {"backup_list": self.backup_list, "rollback_last": self.rollback_last}
                json.dump(j, f, ensure_ascii=False, indent=4)
    
    def __baks(self, src, target):
            backup2current(str(src), str(target))

    def autobackup(self, msg=""):


        self.server.say(RTextList(RText("开始备份存档： "), RText(f"{self.cur_timestamp} ", RColor.yellow), RText("...")))

        t1 = time.time()
        # save-off
        self.server.rcon_query("save-off")
        # server.rcon_query("save-all flush")

        result = self.server.rcon_query("save-all")

        if re.findall("Saved the game", result):
            # self.server.say("拿到 `Saved the game` 结果")
            pass
        else:
            # self.server.say(RText("服务器可能 过于卡顿 备份失败。。。", RColor.red))
            # self.server.say(RText(f"没拿到 ｀Saved the game｀ 拿到的是{result}", RColor.red))
            return


        try:
            backup2current(str(WORLD_DIR), str(BACKUP_DIR/"bak-0"))
        except Exception as e:
            self.server.say(RText("插件内部错误。。。", RColor.red))
            raise e
        
        self.server.rcon_query("save-on")

        t2 = time.time()

        self.server.say(RTextList(RText("备份存档： "), RText(f"{self.cur_timestamp}", RColor.yellow), RText(" 完成 "), RText(f"耗时：{round(t2-t1, 2)}s", RColor.yellow)))

        # 更新存档信息
        self.__update(msg)


@new_thread("auto backup")
def autobackup_lock(server):

    if backing.locked():
        server.say(RText("备份的太频繁... 等会吧", RColor.red))
    else:
        server.say(RText("手动触发备份存档 ..."))
        with backing:
            bi = BackInfo(server)
            bi.autobackup()
        
        # 每次备份后，需要reset 自动备份计时器（B.value）
        B.value = 0

@new_thread("manual backup")
def manual_backup_lock(server, msg):

    if backing.locked():
        server.say(RText("备份的太频繁... 等会吧", RColor.red))
    else:
        server.say(RText("手动触发备份存档 ..."))
        with backing:
            bi = BackInfo(server)
            bi.autobackup(msg)
        
        # 每次备份后，需要reset 自动备份计时器（B.value）
        B.value = 0


@new_thread("rollback")
def rollback_lock(server, number):

    if backing.locked():
        server.say(RText("有备份在进行中... 等会吧", RColor.red))
    else:
        server.say(RText(f"回滚备份存档 ... {number}", RColor.yellow))
        with backing:
            bi = BackInfo(server)
            bi.rollback(number)
        
        # 每次备份后，需要reset 自动备份计时器（B.value）
        B.value = 0


def waitrcon(server):
    # server刚启动时，等待rcon
    while True:

        if server.is_rcon_running():
            # server.logger.info("rcon is running")
            break
        # else:
            # server.logger.info("wait rcon is running")
        
        time.sleep(5)


def player_online(server):

    if server.is_server_startup():

        waitrcon(server)

        result = server.rcon_query("list")
        # server.logger.info(f"players() server.rcon_query() --> {result}")

        match = re.match("There are ([0-9]+) of a max of ([0-9]+) players online:(.*)", result)
        players = int(match.group(1))

        if players == 0:
            return False
        else:
            return True

    else:
        return False


@new_thread("backup Timer")
def wait30minute(server):

    minute30 = 30
    while True:

        # 每分钟检测有没有有玩家 在线，并累计。
        B.value = 0
        while B.value < minute30:

            time.sleep(60)
            if player_online(server):
                B.value += 1
            
            if PLUGIN_RELOAD:
                server.logger.info("backup Timer 线程退出")
                return
            
        if not backing.locked():
            with backing:
                bi = BackInfo(server)
                bi.autobackup()



## 定义指令函数
@permission
def help(src):
    server, info = __get(src)

    msg=[f"{'='*10} 使用说明 {'='*10}",
    f"",
    f"{'='*10} 使用方法 {'='*10}",
    f"{cmdprefix}                    查看使用方法",
    f"{cmdprefix} list               列出所有备份",
    f"{cmdprefix} backup             手动触发创建备份",
    f"{cmdprefix} backupmsg <备注>    手动触发创建备份, 添加注释",
    f"{cmdprefix} rollback <序号>     恢复到指定备份",
    ]
    server.reply(info, "\n".join(msg))

@permission
def ls(src, ctx):
    server = src.get_server()
    info = src.get_info()
    
    msg=[f"{'='*10} 当前存档 {'='*10}"]

    bi = BackInfo(server)
    archives, rollback = bi.list()
    for i, archive in enumerate(archives):
        if archive[1] == "":
            msg.append(f"[{i}] 存档： {archive[0]}")
        else:
            msg.append(f"[{i}] 存档： {archive[0]} 注释： {archive[1]}")

    msg.append(f"{'-'*30}")

    if rollback:
        msg.append(f"上次回滚前的存档： {rollback[0]} 注释： {rollback[1]}")

    msg.append(f"使用： {cmdprefix} rollback <序号> 回滚")

    server.reply(info, "\n".join(msg))


@permission
def backup(src, ctx):

    server = src.get_server()
    autobackup_lock(server)

@permission
def backup_msg(src, ctx):

    server = src.get_server()
    msg = ctx.get("msg")
    manual_backup_lock(server, msg)


@permission
def rollback(src, ctx):

    server = src.get_server()
    info = src.get_info()

    number = int(ctx.get("number"))
    server.reply(info, f"{number}")

    bi = BackInfo(server)
    ls = bi.list()
    ls_len = len(ls)
    if 0 > number or number > ls_len - 1:
        server.reply(info, RText(f"回滚号，只能在 0-{ls_len - 1} 范围", RColor.red))
        return
    
    rollback_lock(server, number)



def build_command():
    c = Literal(cmdprefix).runs(lambda src: help(src))
    c.then(Literal("list").runs(lambda src, ctx: ls(src, ctx)))
    c.then(Literal("backup").runs(lambda src, ctx: backup(src, ctx)))
    c.then(Literal("backupmsg").then(QuotableText("msg").runs(lambda src, ctx: backup_msg(src, ctx))))
    c.then(Literal("rollback").then(Integer("number").runs(lambda src, ctx: rollback(src, ctx))))
    return c


# rcon_query("save-all") 的输出不会到这来。
def on_info(server, info):
    pass

def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, PLUGIN_METADATA["name"], PermissionLevel.ADMIN)
    server.register_command(build_command())

    # init
    read_cfg(server)

    wait30minute(server)

    if old_plugin is None:
        pass
    else:
        old_plugin.PLUGIN_RELOAD = True
        B.value = old_plugin.B.value

def on_unload(server):
    global PLUGIN_RELOAD
    PLUGIN_RELOAD = True

def on_player_joined(server, player, info):
    pass

def on_player_left(server, player):
    pass

