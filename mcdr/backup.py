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
    "backup_seq": [2, 2, 4, 3],
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
            AUTOBACKUP_DIR = BACKUP_DIR / "autobackup"

    else:
        with open(config_file, "w") as f:
            json.dump(CFG, f, ensure_ascii=False, indent=4)

    # init
    if not BACKUP_DIR.exists():
        os.makedirs(BACKUP_DIR)
    
    # init autobackup 目录
    if not AUTOBACKUP_DIR.exists():
        os.makedirs(AUTOBACKUP_DIR)
    
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

        self.backup_seq = CFG["backup_seq"]
        self.backup_info = BACKUP_DIR / "backupinfo.json"

        self.backup_list = []
        self.rollback_last = ""

        # 读写备份信息的锁
        self.__rw = Lock()


        # 初始化bak目录
        for i in range(len(self.backup_seq) + 1):
            bak = BACKUP_DIR / f"bak-{i}"
            if not bak.exists():
                bak.mkdir()

            self.backup_list.append({"value": 0, "timestamp": "", "msg":""})
            

        if BACKUP_INFO.exists():
            self.__read()
        else:
            self.__write()

    
    def list(self):
        ls = []

        for d in self.backup_list:
            if d["timestamp"] == "":
                return ls
            else:
                ls.append(d["timestamp"])
        
        if self.rollback_last != "":
            ls.append(self.rollback_last)
        
        return ls
    
    def __update(self):
        """
        更新 value archivename
        return 要被删除的 archivename, 没有 return ""
        """

        cur = self.cur_timestamp

        baks = []

        seq_len = len(self.backup_list)
        print("self.backup_list ==> ", self.backup_list)
        # 从第2个开始，算起
        for i in range(1, seq_len):

            self.backup_list[i]["value"] += 1

            if self.backup_seq[i] <= self.backup_list[i]["value"]:
                self.backup_list[i]["value"] = 0
                self.backup_list[i]["timestamp"], cur = cur, self.backup_list[i]["timestamp"]
                # 执行备份递进
                baks.append(BACKUP_DIR / f"bak-{i}")
                
            else:

                if self.backup_list[i]["timestamp"] != "" and cur != self.backup_list[i]:
                    baks.append(self.backup_list[i]["timestamp"])

                self.backup_list[i]["timestamp"] = cur
                break

        print("self.backup_list ==> 执行后 ", self.backup_list)
        
        baks = baks[1:]
        baks.reverse()

        for i in range(len(baks) - 1):
            self.__baks(baks[:1], baks[i])
        
        if len(baks) >= 1:
            self.__baks(BACKUP_DIR/"bak-1", baks[0])


        # 写前更新最新时间
        self.backup_list[0]["timestamp"] = self.cur_timestamp
        self.__write()


    def select_list(self, number):
        return self.backup_list[number]["timestamp"]

    
    def last_rollback(self):
        return self.rollback_last

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
            backup2current(src, target)

    def autobackup(self):

        self.cur_timestamp = time.strftime("%Y-%m-%d_%H:%M:%S")

        self.server.say(RTextList(RText("开始备份存档： "), RText(f"{self.cur_timestamp} ", RColor.yellow), RText("...")))

        t1 = time.time()
        # save-off
        # server.rcon_query("save-off")
        self.server.execute("save-off")
        # server.rcon_query("save-all flush")

        # 这个可能是阻塞的？ 不是
        result = self.server.rcon_query("save-all")

        # 使用锁等待 saved the game
        # global SAVED_THE_GAME
        if SAVED_THE_GAME.acquire(180):
            self.server.say("拿到 `Saved th game` 结果")
        else:
            self.server.say(RText("服务器可能 过于卡顿 备份失败。。。", RColor.red))
            return


        # wait saved the game
        #global SAVED_THE_GAME
        #c = 0
        #while not SAVED_THE_GAME:
        #    self.server.logger.info(f"server.rcon_query() ==> {result}")
        #    time.sleep(1)

        #    if c >= 180:
        #        self.server.say(RText("服务器可能 过于卡顿 备份失败。。。", RColor.red))
        #        return
        #    c += 1

        try:
            backup2current(str(WORLD_DIR), str(BACKUP_DIR/"bak-0"))
        except Exception as e:
            self.server.say(RText("插件内部错误。。。", RColor.red))
            raise e
        
        self.server.execute("save-on")

        #SAVED_THE_GAME = False

        t2 = time.time()

        self.server.say(RTextList(RText("备份存档： "), RText(f"{self.cur_timestamp}", RColor.yellow), RText(" 完成 "), RText(f"耗时：{round(t2-t1, 2)}s", RColor.yellow)))

        # 更新存档信息
        self.__update()


@new_thread("auto backup")
def autobackup_lock(server):

    SAVED_THE_GAME.acquire()

    if backing.locked():
        server.say(RText("备份的太频繁... 等会吧", RColor.red))
    else:
        server.say(RText("手动触发备份存档 ..."))
        with backing:
            bi = BackInfo(server)
            bi.autobackup()
        
        # 每次手动备份后，需要reset B.value
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
    f"{cmdprefix} backup [备注]       手动触发创建备份",
    f"{cmdprefix} rollback <序号>     恢复到指定备份",
    ]
    server.reply(info, "\n".join(msg))

@permission
def ls(src, ctx):
    server = src.get_server()
    info = src.get_info()
    
    msg=[f"{'='*10} 当前存档 {'='*10}"]

    bi = BackInfo(server)
    archives = bi.list()
    for i, archive in enumerate(archives):
        msg.append(f"[{i}] 存档： {archive}")

    msg.append(f"{'-'*30}")
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


@permission
def rollback(src, ctx):

    server = src.get_server()
    info = src.get_info()

    number = int(ctx.get("number"))
    server.reply(info, f"功能还没实现～")



def build_command():
    c = Literal(cmdprefix).runs(lambda src: help(src))
    c.then(Literal("list").runs(lambda src, ctx: ls(src, ctx)))
    c.then(Literal("backup").runs(lambda src, ctx: backup(src, ctx)))
    c.then(Literal("bakmsg").then(QuotableText("msg").runs(lambda src, ctx: backup_msg(src, ctx))))
    c.then(Literal("rollback").then(Integer("number").runs(lambda src, ctx: rollback(src, ctx))))
    return c


# rcon_query("save-all") 的输出不会到这来。
# 改用 server.execute()
def on_info(server, info):
    global SAVED_THE_GAME
    if info.source == 0 and info.content == "Saved the game":
        SAVED_THE_GAME.release()
        server.logger.info("标记到 `Saved th game`")
    else:
        server.logger.info(f"都看到了啥？＝＝> {info.content}")


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

