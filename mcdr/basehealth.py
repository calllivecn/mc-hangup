#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-14 16:01:21
# author calllivecn <c-all@qq.com>


import re
import os
# import sys
import time
import json
from pathlib import Path

from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer
from mcdreforged.permission.permission_level import PermissionLevel

PLUGIN_METADATA = {
    # ID（即插件ID）是您插件的身份字符串。它应该由小写字母，数字和下划线组成，长度为1到64
    'id': 'maxhealth', 
    'version': '0.1.0',
    'name': '最大血量',
    'author': [
        'calllivecn'
   ],
    'link': 'https://github.com/calllivecn/mc-hangup',
    'dependencies': {
        'mcdreforged': '>=1.3.0',
    }
}



cmdprefix = "." + PLUGIN_METADATA["id"]

cur_dir = os.path.dirname(os.path.dirname(__file__))
SOUL_DIR = Path(cur_dir) / "config" / PLUGIN_METADATA["id"]

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

"""
/attribute zx minecraft:generic.max_health base set 200
"""
def on_death_message(server, death_message):
    server.logger.info(f"什么信息--> {death_message}")
    

def on_user_info(server, info):
    pass

def on_player_joined(server, player, info):
    pass

def build_command():
    return Literal(f"{cmdprefix}").runs(lambda src, ctx: soul(src, ctx))

def on_load(server, old_plugin):
    # server.register_help_message(cmdprefix, RText("招唤出你的灵魂", RColor.yellow), PermissionLevel.USER)
    # server.register_command()
    pass