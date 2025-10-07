#!/usr/bin/env python3
# coding=utf-8
# date 2021-07-24 15:42:24
# author calllivecn <calllivecn@outlook.com>

import re
import time
import configparser
from pathlib import Path


from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import (
    RText,
    RColor,
    RAction,
    RStyle,
    RTextList,
)

# mcdr_v2.x 还不能拿到 插件元数据
# from mcdreforged.plugin.meta.metadata import Metadata

# mcdr_v1.x
# from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer

# mcdr_v2.x
from mcdreforged.command.builder.nodes.basic import Literal, ArgumentNode
from mcdreforged.command.builder.common import ParseResult
from mcdreforged.command.builder.exception import CommandSyntaxError
from mcdreforged.command.builder.nodes.arguments import QuotableText, Text, GreedyText, Integer, Float

from mcdreforged.permission.permission_level import PermissionLevel

from mcdreforged.api.types import PluginServerInterface, Info, PlayerCommandSource


CMDPREFIX="."
# mcdr_v1.x 
# CONFIG_DIR = Path(__file__).parent.parent / "config"
# mcdr_v2.x
CONFIG_DIR = Path(__file__).parent.parent.parent.parent / "config"
#print(f"{CONFIG_DIR=}")


def readcfg(filename, init_context=None):
    conf = configparser.ConfigParser()
    if filename.exists():
        conf.read(str(filename))
        return conf
    else:
        if init_context is None:
            raise Exception(f"初始化配置文本没有提供: {init_context}")
        else:
            with open(filename, "w") as fp:
                fp.write(init_context)

            conf.read_string(init_context)
            return conf


def __get(src):
    return src.get_server(), src.get_info()

def timestamp():
    return int(time.time())

def permission(func):
    def warp(*args, **kwargs):
        # print(f"*args {args}  **kwargs {kwargs}", file=sys.stdout)
        server, info = __get(args[0])
        perm = server.get_permission_level(info)

        # print(f"warp(): {args} {kwargs}", file=sys.stdout)
        if perm >= PermissionLevel.USER:
            func(*args, **kwargs)
 
    return warp

def permission_admin(func):
    def warp(*args, **kwargs):
        # print(f"*args {args}  **kwargs {kwargs}", file=sys.stdout)
        server, info = __get(args[0])
        perm = server.get_permission_level(info)

        # print(f"warp(): {args} {kwargs}", file=sys.stdout)
        if perm >= PermissionLevel.ADMIN:
            func(*args, **kwargs)
 
    return warp


def match(re_str, s_str, groups=(0,)) -> tuple:
    lg = []
    result = re.match(re_str, s_str)
    if result:
        for i in groups:
            lg.append(result.group(i))

    return tuple(lg)

def check_rcon(server):

    rcon_result = server.rcon_query("list")
    if rcon_result is None:
        prompt = RText("rcon 没有开启, 请分别server.properties, MCDR/config.yml 开启。", RColor.red)
        server.logger.warning(prompt)
        server.say(RText("RCON 没有配置成功，请联系服主。", RColor.red))
        return False


def playsound(server, player):
    server.rcon_query(f"execute at {player} run playsound minecraft:entity.player.levelup player {player}")

def get_players(server):
    # 获取在线玩家
    result = server.rcon_query("list")
    server.logger.debug(f"result = server.rcon_query('list') -->\n{result}")

    players, playernames = match("There are ([0-9]+) of a max of ([0-9]+) players online:(.*)", result, (1, 3))
    if players == "0":
        return []

    players = []
    for s in playernames.split(","):
        players.append(s.strip())
    
    return players

def player_online(server, player):

    #result = server.rcon_query(f"data get entity {player} Name")
    result = server.rcon_query(f"experience query {player} points")

    #if re.search("No entity was found", result).group():
    if re.search(f"{player} has ([0-9]+) experience points", result):
        return True
    else:
        return False


def check_level(server, info):
    # 查看玩家的等级够不够
    level = server.rcon_query(f"experience query {info.player} levels")
    if not level:
        server.reply(info, RText("无法查询到你的经验，请联系服主。", RColor.red))
        return False

    lvl = re.match(f"{info.player} has ([0-9]+) experience levels", level)
    if not lvl:
        server.reply(info, RText("无法查询到你的经验，请联系服主。", RColor.red))
        return False

    level_value = lvl.group(1)

    server.logger.debug(f"玩家 {info.player} 等级： {level_value}")

    if int(level_value) < 1:
        server.reply(info, RText("经验不足，至少需要1级", RColor.red))
        return False
    else:
        # 扣掉1级
        server.rcon_query(f"experience add {info.player} -1 levels")
        return True


# 竖项格式化
def fmt(ls, delimite=10):
    ls_len = len(ls)

    c, i = divmod(ls_len, delimite)
    if i > 0:
        c+=1
    
    if ls_len < delimite:
        range_delimite = ls_len
    else:
        range_delimite = delimite

    output_list = []
    for j in range(range_delimite):
        line = ""
        for i in range(c):
            l = j + delimite * i

            if l >= ls_len:
                break

            line += ls[l] + RText(",  ")
            # line += ls[l] + RText(",\t")

        if j < (range_delimite - 1):
            line = line + RText("\n")

        output_list.append(line)
    return output_list


## 只找只有一层{}中括号的物品， 目的是排除玩家身上容器里面的物品。
def item_body(result):
    """
    param: 一般是 "/data get entity {player} Inventory" 后的结果
    return: 由"," 隔开的每个物品组成的字符串
    """
    items=[]
    stack = []
    start = 0 
    end = 0
    stack1_flag=True

    for i, c in enumerate(result):
        if c == "{":
            stack.append("}")
            start = i

        elif c == "}":
            if stack1_flag and len(stack) == 1:
                end = i
                stack.pop()
                items.append(result[start:end+1])

            elif not stack1_flag and len(stack) == 1:
                stack1_flag = True
                start, end = i, i 
                stack.pop()

            elif len(stack) > 1:
                start, end = i, i 
                stack1_flag=False
                stack.pop()
    
    return ",".join(items)


# 配合 showhealth 数据包检测玩家死亡事件
def event_player_death(server, info):
    result = re.match(rf"\* (.*) 死了", info)
    if result:
        # player 死亡
        player = result.group(1)
        result = server.rcon_query(f"data get entity {player} DeathTime")
        if result:
            deathtime = re.match(f"{player} has the following entity data: (.*)s", result)
            t = deathtime.group(1)
            server.logger.debug(f"玩家 {player} 的死亡时间计数：{deathtime}")
            if t != "0":
                server.logger.info(f"检测到玩家 {player} 死亡")
                return player
    
    return None
