#!/usr/bin/env python3
# coding=utf-8
# date 2021-05-17 15:53:15
# author calllivecn <c-all@qq.com>


import re
import ssl
import sys
import time
import json
import ipaddress
import binascii
import socket
from threading import Lock
from pathlib import Path
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

from mcdreforged.api.decorator import new_thread
# from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer
from mcdreforged.permission.permission_level import PermissionLevel

PLUGIN_METADATA = {
    # ID（即插件ID）是您插件的身份字符串。它应该由小写字母，数字和下划线组成，长度为1到64
    'id': 'speedrun', 
    'version': '0.1.0',
    'name': '大逃杀',
    'description': '由一名玩家扮逃亡者，1~3名玩家扮追杀者的小游戏。',
    'author': [
        'calllivecn'
   ],
    'link': 'https://github.com/calllivecn/mc-hangup/mcdr',
    'dependencies': {
        'mcdreforged': '>=1.3.0',
    }
}

cmdprefix = "." + PLUGIN_METADATA["id"]

# 
TEAM = None

class Team:
    teamname = "tmp"

    def __init__(self, server):
        self.server = server
        self.server.rcon_query(f"""team add {self.teamname}""")
        # 关闭团队PVP
        self.server.cron_query(f"team modify {self.teamname} friendlyFire false")

        # team 已建好
        self.team = True

        # 玩家列表
        self.players = []

        self.readys = set()
        self.unreadys = set()

    def join(self, player):
        self.players.append(player)
        self.server.rcon_query(f"team join {self.teamname} {player}")

        welcome_title = f"{player} 欢迎来来大逃杀~！"
        self.server.rcon_query(f"""title {player} title [{"text":"{welcome_title}","bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false}]""")
        self.server.rcon_query(f"gamemode {player} adventure")

        self.unreadys.add(player)
    

    def ready(self, player):
        self.readys.add(player)
        self.unreadys.discard(player)

        if len(self.unreadys) == 0 and len(self.readys) > 0:
            self.game_start()
    
    def unready(self, player):
        self.unreadys.add(player)
        self.readys.discard(player)

    @new_thread("Speed run thread")
    def game_start(self):
        pass
    

    def game_end(self):
        pass
    


def get_pos(server, name):
        # 查询坐标
        rcon_result = server.rcon_query(f"data get entity {name} Pos")
        position = re.match(f"{name} has the following entity data: \[(-?[0-9\.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]", rcon_result)
        x, y, z = position.group(1), position.group(2), position.group(3)
        x, y, z = round(float(x)), round(float(y)), round(float(z))

        return x, y, z


def on_server_startup(server):
    global TEAM
    server.logger.info("Speed Run Server running")
    TEAM = Team(server)


def on_player_joined(server, player, info):
    TEAM.join(player)


def on_info(server, info):

    if info.source == 0 and info.content == "ready":
        TEAM.ready(info.player)

    elif info.source == 0 and info.content == "unready":
        TEAM.unready(info.player)

def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, "大逃杀", PermissionLevel.USER)


