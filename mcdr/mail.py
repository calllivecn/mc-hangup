#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-08 12:46:15
# author calllivecn <calllivecn@outlook.com>

import re
import os
import json

from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer

PLUGIN_METADATA = {
    # ID（即插件ID）是您插件的身份字符串。它应该由小写字母，数字和下划线组成，长度为1到64
    'id': 'mail', 
    'version': '0.1.0',
    'name': '给玩家发送邮件(离线信息)',
    'author': [
        'calllivecn'
   ],
    'link': 'https://github.com/calllivecn/mc-hangup',
    'dependencies': {
        'mcdreforged': '>=1.3.0',
    }
}

cmdprefix = "." + plugin_id


def help_and_run(src):
    server, info = __get(src)

    line1 = f"{'='*10} 使用方法 {'='*10}"
    line2 = f"{cmdprefix}                      查看方法和使用"
    line3 = f"{cmdperifx} store <number>       存储number瓶经验(7经验/瓶)"
    line4 = f"{cmdperifx} store-all            存储全部经验"
    line5 = f"{cmdperifx} store-30             存储多出30级的经验"


def build_command():
    c = Literal(cmdprefix).runs(help)
    c.then(Literal("store").then(Integer("number").runs(ls)))
    c.then(Literal("store-all").then(Integer("number").runs(store_all)))
    c.then(Literal("store-30").then(Integer("number").runs(store_30)))
    return c


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
