#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-08 14:29:15
# author calllivecn <c-all@qq.com>

import os
import sys
import json
from pathlib import Path
import subprocess

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
BACKUP_DIR = Path("bakcup")
WORLD_DIR = Path("server") / "world"

# 配置文件

BACKUP_CFG = {
    "world_dir": WORLD_DIR,
    "backup_dir": BACKUP_DIR,
    "backup_interval": 30 * 60,
    "backup_seq": [2, 6, 16, 48, 144]
}

def read_cfg(server):
    global BACKUP_CFG

    if config_file.exists():
        with open(config_file) as f:
            BACKUP_CFG = json.load(f)
    else:
        with open(config_file, "w") as f:
            json.dump(BACKUP_CFG, f, ensure_ascii=False, indent=4)

    # init
    if not BACKUP_DIR.exists():
        os.makedirs(BACKUP_DIR)
    
    #
    # backup_seq 必须是单调递增的
    seq = BACKUP_CFG["bakcup_seq"]
    if seq[0] < 2:
        server.logger.warning(f"{BACKUP_CFG} 中 backup_seq[0]: {seq} 配置错误；必须大于等 2")

    for i in range(len(seq) - 1):
        if seq[i] >= seq[i+1]:
            server.logger.warning(f"{BACKUP_CFG} 中 backup_seq: {seq} 配置错误；backup_seq 必须是单调递增且不相等的,")
            return False
    
    return True



SAVED_THE_GAME = False

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

def rsync(source, backup):
    try:
        subprocess.check_call(["rsync", "-a", "--delete", source, backup])

    except FileNotFoundError as e:
        pass

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
    pass

@permission
def backup(src, ctx):
    pass

@permission
def rollback(src, ctx):
    pass

def build_command():
    c = Literal(cmdprefix).runs(lambda src: help(src))
    c.then(Literal("list").runs(lambda src, ctx: ls(src, ctx)))
    c.then(Literal("backup").runs(lambda src, ctx: backup(src, ctx)))
    c.then(Literal("rollback").then(Integer("number").runs(lambda src, ctx: backup(src, ctx))))
    return c


def on_info(server, info):
    if info.source == 0 and info.content == "Saved the game":
        SAVED_THE_GAME = True


def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, PLUGIN_METADATA["name"], PermissionLevel.ADMIN)
    server.register_command(build_command())

def on_unload(server):
    pass

def on_player_joined(server, player, info):
    pass

def on_player_left(server, player):
    pass

