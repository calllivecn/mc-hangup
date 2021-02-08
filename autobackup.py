#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-08 14:29:15
# author calllivecn <c-all@qq.com>

import re
import os
import json
from pathlib import Path
import subprocess

from mcdreforged import config
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer

PLUGIN_METADATA = {
    # ID（即插件ID）是您插件的身份字符串。它应该由小写字母，数字和下划线组成，长度为1到64
    'id': 'autobackup', 
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

cur_dir = Path(os.path.dirname(os.path.dirname(__file__))
world_dir = cur_dir / "server" / "world"


def on_unload(server):
    pass

def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, PLUGIN_METADATA["name"])
    server.register_command(build_command())

def on_player_joined(server, player):
    pass

def on_player_joined(server, player, info):
    pass

def on_player_left(server, player):
    pass
