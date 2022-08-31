#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-08 14:29:15
# author calllivecn <c-all@qq.com>

import os
import re
import time
import shutil
import subprocess
from pathlib import Path
from threading import Lock

# from mcdreforged import config
# from mcdreforged.api.decorator import new_thread

from funcs import (
    CMDPREFIX,
    CONFIG_DIR,
    __get,
    RText,
    RColor,
    RTextList,
    Literal,
    QuotableText,
    Integer,
    new_thread,
    permission,
    PermissionLevel,
    readcfg,
    get_players,
)

CMD = CMDPREFIX + "bak"
PLUGIN_NAME = "服务端自动备份工具(rsync)"

CONF_FILE = CONFIG_DIR / "backup.conf"

# 配置文件

cfg_text = """\
[backup]
# 默认目录备份路径(相对mcdr的路径)
world_dir = server/world
backup_dir = backup

# 多长时间备份一次, 单位分钟。 需要>=10, 小于10会固定在10
backup_interval = 30
# 最多保留多少份备份。需要>=1, 小于1会固定在1
backup_count = 24
"""

conf = readcfg(CONF_FILE, cfg_text)

# 默认目录 和 备份路径(相对mcdr的路径)
WORLD_DIR = Path(conf.get("backup", "world_dir"))
BACKUP_DIR = Path(conf.get("backup", "backup_dir"))
BACKUP_INTERVAL = conf.getint("backup", "backup_interval")
BACKUP_COUNT = conf.getint("backup", "backup_count")

if BACKUP_INTERVAL < 10:
    BACKUP_INTERVAL = 10

if BACKUP_COUNT < 1:
    BACKUP_COUNT = 1

if not BACKUP_DIR.exists():
    BACKUP_DIR.mkdir()


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


PLUGIN_RELOAD = False
B = BackupInternal()
backing = Lock()


### 定义 


def backup2current(latest: Path, source: Path, target: Path):
    latest_ = str(latest.absolute())
    source_ = str(source)
    target_ = str(target)

    if not source_.endswith("/"):
        source_ = source_ + "/"
    
    print(f"rsync: {source} ==> {target}")
    try:
        subprocess.run(["rsync", "-a", "--delete", "--link-dest", latest_, source_, target_])
    except FileNotFoundError as e:
        raise e
    except Exception as e:
        raise e
    
    latest_symlink = target.parts[-1]
    # 把软链指向最新备份目录
    if latest.is_symlink():
        os.remove(latest)
        latest.symlink_to(latest_symlink)
    else:
        latest.symlink_to(latest_symlink)


class BackInfo:

    def __init__(self, server):

        self.server = server

        self.cur_timestamp = time.strftime("%Y-%m-%d_%H:%M:%S")
        self.cur = BACKUP_DIR / self.cur_timestamp

        self.backup_list = os.listdir(BACKUP_DIR)
        self.backup_list.sort()

        self.latest = BACKUP_DIR / "latest"


    def list(self):
        ls = []

        for b in self.backup_list:
            bak = BACKUP_DIR / b
            if bak.is_dir() and not bak.is_symlink():
                filename = Path(str(bak) + ".msg")
                msg = self.__readmsg(filename)
                ls.append((b, msg))

        ls.reverse()
        return ls


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
            self.server.rcon_query("save-on")
            return

        try:
            backup2current(self.latest, WORLD_DIR, self.cur)
        except Exception as e:
            self.server.say(RText("插件内部错误。。。", RColor.red))
            raise e
        finally:
            self.server.rcon_query("save-on")

        t2 = time.time()

        # 写下备注
        if msg:
            self.__write(msg)

        self.server.say(RTextList(RText("备份存档： "), RText(f"{self.cur_timestamp}", RColor.yellow), RText(" 完成 "), RText(f"耗时：{round(t2-t1, 2)}s", RColor.yellow)))

        self.autoremove()


    def rollback(self, number):
        tm, msg = self.list()[number]

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
                time.sleep(1)
        
        # 备份下
        self.autobackup("上一次 rollback 时的备份")

        
        if self.server.is_server_running():
            self.server.logger.info("关闭服务器中...")
            self.server.stop()
            self.server.wait_for_start()
            self.server.logger.info("等待服务器，关闭后，执行回滚.")
        else:
            self.server.logger.info("服务器没有运行")
            return

        bak = str(BACKUP_DIR / tm)
        if not bak.endswith("/"):
            bak = bak + "/"

        try:
            subprocess.run(["rsync", "-a", "--delete", bak, str(WORLD_DIR)])
        except Exception as e:
            self.server.say(RText("插件内部错误。。。", RColor.red))
            raise e
        
        self.server.start()
    

    def remove(self, number):
        baks = self.list()
        tm, msg = baks[number]

        bak = BACKUP_DIR / tm
        shutil.rmtree(bak)
        filename = Path(str(bak) + ".msg")
        if filename.exists():
            os.remove(filename)
        
        # 如果删除最新的备份，需要把latest 指向倒数第2个
        if number == 0 and len(baks) > 2:
            os.remove(self.latest)
            self.latest.symlink_to(baks[1][0])
    
    def autoremove(self):
        baks = self.list()
        for bak in baks[BACKUP_COUNT-1:]:
            shutil.rmtree(BACKUP_DIR / bak[0])


    def __readmsg(self, filename: Path):
        if filename.is_file():
            with open(filename, "r") as f:
                return f.read()
        else:
            return ""


    def __write(self, msg: str):
        filename = Path(str(self.cur) + ".msg")
        with open(filename, "w") as f:
            f.write(msg)


@new_thread("backup auto backup")
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

@new_thread("bakcup manual backup")
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


@new_thread("backup rollback")
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


@new_thread("backup remove")
def th_remove(server, number):
    bi = BackInfo(server)
    bi.remove(number)


def player_online(server):

    players = get_players(server)
    if players == 0:
        return False
    else:
        return True


@new_thread("backup Timer")
def wait30minute(server):

    while True:

        # 每分钟检测有没有有玩家 在线，并累计。
        B.value = 0
        while B.value < BACKUP_INTERVAL:

            time.sleep(60)
            if server.is_server_running():
                try:
                    if player_online(server):
                        B.value += 1
                except BaseException as e:
                    server.logger.warning(f"刚rollbak完启动时rcon_query可能还没连接好: {e}")
            
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
    f"{CMD}                    查看使用方法",
    f"{CMD} list               列出所有备份",
    f"{CMD} backup             手动触发创建备份",
    f"{CMD} backupmsg <备注>    手动触发创建备份, 添加注释",
    f"{CMD} remove <序号>       删除备份",
    f"{CMD} rollback <序号>     恢复到指定备份",
    ]
    server.reply(info, "\n".join(msg))

@permission
def ls(src, ctx):
    server = src.get_server()
    info = src.get_info()
    
    msg=[f"{'='*10} 当前存档 {'='*10}"]

    bi = BackInfo(server)
    archives = bi.list()
    baks = []
    for i, archive in enumerate(archives):
        if archive[1] == "":
            baks.append(f"[{i}]存档: {archive[0]}")
        else:
            baks.append(f"[{i}]存档: {archive[0]} 注释: {archive[1]}")

    baks.reverse()
    msg += baks

    msg.append(f"{'-'*30}")
    msg.append(f"使用: {CMD} rollback <序号> 回滚")
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
        server.reply(info, RText(f"备份号，只能在 0-{ls_len - 1} 范围", RColor.red))
        return
    
    rollback_lock(server, number)


@permission
def remove(src, ctx):
    server = src.get_server()
    number = int(ctx.get("number"))
    info = src.get_info()

    bi = BackInfo(server)
    ls = bi.list()
    ls_len = len(ls)
    if 0 > number or number > ls_len - 1:
        server.reply(info, RText(f"备份号，只能在 0-{ls_len - 1} 范围", RColor.red))
        return
        
    th_remove(server, number)

def build_command():
    c = Literal(CMD).runs(lambda src: help(src))
    c.then(Literal("list").runs(lambda src, ctx: ls(src, ctx)))
    c.then(Literal("backup").runs(lambda src, ctx: backup(src, ctx)))
    c.then(Literal("backupmsg").then(QuotableText("msg").runs(lambda src, ctx: backup_msg(src, ctx))))
    c.then(Literal("remove").then(Integer("number").runs(lambda src, ctx: remove(src, ctx))))
    c.then(Literal("rollback").then(Integer("number").runs(lambda src, ctx: rollback(src, ctx))))
    return c


# rcon_query("save-all") 的输出不会到这来。
def on_info(server, info):
    pass

def on_load(server, old_plugin):
    server.register_help_message(CMD, PLUGIN_NAME, PermissionLevel.ADMIN)
    server.register_command(build_command())

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

