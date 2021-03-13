#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-08 14:29:15
# author calllivecn <c-all@qq.com>

import os
import re
import sys
import json
import time
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

cmdprefix = "." + "backup"

cur_dir = Path(os.path.dirname(os.path.dirname(__file__)))

config_file = cur_dir / "config" / "backup.json"

# 默认目录 和 备份路径(相对mcdr的路径)
BACKUP_DIR = Path("backup")
AUTOBACKUP_DIR = BACKUP_DIR / "autobackup"
WORLD_DIR = Path("server") / "world"

# 配置文件

CFG = {
    "world_dir": str(WORLD_DIR),
    "backup_dir": str(BACKUP_DIR),
    "backup_interval": 30 * 60,
    "backup_seq": [2, 6, 16, 48, 144]
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
    
    #
    # backup_seq 必须是单调递增的
    seq = CFG["backup_seq"]
    if seq[0] < 2:
        server.logger.warning(f"{config_file} 中 backup_seq[0]: {seq} 配置错误；必须大于等 2")

    for i in range(len(seq) - 1):
        if seq[i] >= seq[i+1]:
            server.logger.warning(f"{config_file} 中 backup_seq: {seq} 配置错误；backup_seq 必须是单调递增且不相等的,")
            return False
    
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
    
    def is_locked(self):
        return self._lock.locked()
    
    def __enter__(self):
        self._lock.acquire()
    

    def __exit__(self, typ, value, traceback):
        self._lock.release()


SAVED_THE_GAME = False
PLUGIN_RELOAD = False
BI = BackupInternal()

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
    try:
        # subprocess.check_call(["rsync", "-av", "--delete", source, target])
        subprocess.check_call(["rsync", "-a", "--delete", source, target])
    except FileNotFoundError as e:
        raise e



def autobackup(server):
    archivename = BACKUP_DIR / time.strftime("%Y-%m-%d_%H:%M:%S")

    server.say(RTextList(RText("开始备份存档： "), RText(f"{archivename} ", RColor.yellow), RText("...")))

    t1 = time.time()
    # save-off
    # server.rcon_query("save-off")
    server.execute("save-off")
    # server.rcon_query("save-all flush")

    # 这个可能是阻塞的？ 不是
    #result = server.rcon_query("save-all")
    server.execute("save-all")

    # wait saved the game
    global SAVED_THE_GAME
    c = 0
    while not SAVED_THE_GAME:
        # server.logger.info(f"server.rcon_query() ==> {result}")
        time.sleep(1)

        if c >= 60:
            server.say(RText("服务器可能 过于卡顿 备份失败。。。", RColor.red))
            return
        c += 1

    try:

        with BI:
            backup2current(str(WORLD_DIR), str(AUTOBACKUP_DIR))

    except Exception as e:
        raise e        
    
    server.execute("save-on")

    SAVED_THE_GAME = False

    t2 = time.time()

    server.say(RTextList(RText("备份存档： "), RText(f"{archivename}", RColor.yellow), RText(" 完成 "), RText(f"耗时：{round(t2-t1, 2)}s", RColor.yellow)))

    with BI:
        backup2current(str(AUTOBACKUP_DIR), str(archivename))



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
        BI.value = 0
        while BI.value < minute30:

            time.sleep(60)
            if player_online(server):
                BI.value += 1
            
            if PLUGIN_RELOAD:
                server.logger.info("backup Timer 线程退出")
                return
            
        autobackup(server)

        # 这里之后加上，轮替的处理



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
    f"{cmdprefix} rollback <序号>     恢复到指定备份",
    ]
    server.reply(info, "\n".join(msg))

@permission
def ls(src, ctx):
    server = src.get_server()
    info = src.get_info()
    
    msg=[f"{'='*10} 当前存档 {'='*10}"]

    i = 0
    for archive in os.listdir(BACKUP_DIR):

        if archive == "autobackup":
            continue

        msg.append(f"[{i}] 存档： {archive}")

        i += 1
    
    msg.append(f"{'-'*30}")
    msg.append(f"使用： {cmdprefix} rollback <序号> 回滚")

    server.reply(info, "\n".join(msg))


@permission
def backup(src, ctx):

    server = src.get_server()
    info = src.get_info()

    if BI.is_locked():
        server.say(RText("已有任务，正在备份中...", RColor.red))
    else:
        server.say(RText("手动触发备份存档 ..."))
        autobackup(server)



@permission
def rollback(src, ctx):

    server = src.get_server()
    info = src.get_info()

    server.say(f"功能还没实现～")



def build_command():
    c = Literal(cmdprefix).runs(lambda src: help(src))
    c.then(Literal("list").runs(lambda src, ctx: ls(src, ctx)))
    c.then(Literal("backup").runs(lambda src, ctx: backup(src, ctx)))
    c.then(Literal("rollback").then(Integer("number").runs(lambda src, ctx: rollback(src, ctx))))
    return c


# 在 rcon_query() 中执行的输出不会到这来。
# 改用 server.execute()
def on_info(server, info):
    global SAVED_THE_GAME
    if info.source == 0 and info.content == "Saved the game":
        SAVED_THE_GAME = True
        server.logger.info("标记到 `Saved th game`")


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
        BI.value = old_plugin.BI.value

def on_unload(server):
    global PLUGIN_RELOAD
    PLUGIN_RELOAD = True

def on_player_joined(server, player, info):
    pass

def on_player_left(server, player):
    pass

