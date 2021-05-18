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
import random
import binascii
import socket
from threading import Lock
from pathlib import Path
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
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


def get_pos(server, name):
        # 查询坐标
        rcon_result = server.rcon_query(f"data get entity {name} Pos")
        position = re.match(f"{name} has the following entity data: \[(-?[0-9\.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]", rcon_result)
        x, y, z = position.group(1), position.group(2), position.group(3)
        x, y, z = round(float(x)), round(float(y)), round(float(z))

        return x, y, z


class Team:
    teamname = "tmp"

    def __init__(self, server):
        self.server = server
        self.server.rcon_query(f"""team add {self.teamname}""")
        # 关闭团队PVP
        self.server.rcon_query(f"team modify {self.teamname} friendlyFire false")

        # team 已建好
        self.team = True

        # 玩家列表
        self.players = set()

        self.readys = set()
        self.unreadys = set()

        # 设置记分板
        self.server.rcon_query(f"""scoreboard objectives add death deathCount ["死亡次数"]""")
        self.server.rcon_query(f"""scoreboard objectives setdisplay sidebar death""")

    def join(self, player):
        self.players.add(player)
        self.server.rcon_query(f"team join {self.teamname} {player}")
        # 死记记数设置为0
        self.server.rcon_query(f"scoreboard players set {player} death 0")

        welcome_title = f"{player} 欢迎来来大逃杀~！"
        self.server.rcon_query(f"""title {player} title {{"text":"{welcome_title}","bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false}}""")
        self.server.rcon_query(f"gamemode adventure {player}")

        self.unreadys.add(player)
    

    def leave(self, player):
        self.players.discard(player)
        self.unreadys.discard(player)
        self.readys.discard(player)
    

    def ready(self, player):
        self.readys.add(player)
        self.unreadys.discard(player)

        if len(self.unreadys) == 0 and len(self.readys) > 1:
            self.game_start()
        else:
            # check 玩家人数，够不够开局
            self.server.say(f"还有人没有准备好，或人数不够。")
    
    def unready(self, player):
        self.unreadys.add(player)
        self.readys.discard(player)

    @new_thread("Speed run thread")
    def game_start(self):
        # 选出一个逃亡者
        ps = list(self.players)
        rand = random.randint(0, len(ps) - 1)
        self.player_running = ps[rand]

        # self.server.say()

        # 10秒后游戏开始
        for i in range(10, 0, -1):
            self.server.say(RTextList(RText(f"{i}", RColor.green), " 秒钟后游戏开始, 请不要中途退出。"))
            time.sleep(1)
        
        self.server.rcon_query(f"team empty {self.teamname}")
        for player in self.players:
            self.server.rcon_query(f"gamemode survival {player}")
        
        self.game_started = True

        self.server.rcon_query("execute at @a run playsound minecraft:item.totem.use player @a")
        self.server.rcon_query("""title @a subtitle {"text":"游戏开始！", "bold": true, "color":"red"}""")
        self.server.rcon_query(f"""title @a title {{"text":"逃亡者是：{self.player_running}","bold":true, "color": "yellow"}}""")

        # 如果 逃亡者存活过30分钟，逃亡者胜利。
        for i in range(6):
            time.sleep(5*60)

            # 广播逃亡者位置，并高亮1分钟。
            x, y, z = get_pos(self.server, self.player_running)
            self.server.say(RTextList("逃亡者:", RText(self.player_running, RColor.yellow), "现在的位置是:", RText(f"x:{x} y:{y} z:{z}", RColor.green)))
            self.server.rcon_query(f"effect give {self.player_running} minecraft:glowing 60")

        # 怎么结束？不好检测，玩家死亡。
        # 1. 使用 scoresbaord 记录玩家死亡数。
        # 2. 每次有玩家死亡，就拿到他的死亡计数，看看是否是逃亡者死亡。

        self.server.rcon_query(f"""title @a subtitle {{"text":"逃亡者 {self.player_running} 胜利", "bold": true, "color":"red"}}""")
        self.server.rcon_query("""title @a title {"text":"游戏时间到!","bold":true, "color": "yellow"}""")

    def game_end(self):
        pass
    



def on_server_startup(server):
    server.logger.info("Speed Run Server running")


def on_player_joined(server, player, info):
    global TEAM

    if TEAM == None:
        TEAM = Team(server)

    TEAM.join(player)

def on_player_left(sever, player):
    global TEAM
    TEAM.leave(player)

def on_info(server, info):

    if info.source == 0 and info.content == "ready":
        TEAM.ready(info.player)

    elif info.source == 0 and info.content == "unready":
        TEAM.unready(info.player)

def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, "大逃杀", PermissionLevel.USER)


