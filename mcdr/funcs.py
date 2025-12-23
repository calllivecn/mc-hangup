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
from mcdreforged.command.builder.nodes.arguments import QuotableText, Text, GreedyText, Integer, Float, Number

from mcdreforged.permission.permission_level import PermissionLevel

from mcdreforged.api.types import PluginServerInterface, ServerInterface, Info, PlayerCommandSource, CommandSource, InfoCommandSource


CMDPREFIX="."
# mcdr_v1.x 
# CONFIG_DIR = Path(__file__).parent.parent / "config"
# mcdr_v2.x
CONFIG_DIR = Path(__file__).parent.parent.parent.parent / "config"
#print(f"{CONFIG_DIR=}")


"""
    可以在 def on_load() 中获取插件的元数据
    meta = server.get_self_metadata()
    plugin_id = meta.id
    version = meta.version
    name = meta.name
    author = meta.author
"""


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


def __get(src: CommandSource):
    return src.get_server(), src.get_info() # type: ignore

def timestamp():
    return int(time.time())

def permission(func):
    """
    在使用时，必须在 .runs(lambda src, crx: func(src, crx)) 这样使用
    """

    def warp(*args, **kwargs):
        # print(f"*args {args}  **kwargs {kwargs}")
        server, info = __get(args[0])
        perm = server.get_permission_level(info)

        # print(f"warp(): {args} {kwargs}")
        if perm >= PermissionLevel.USER:
            func(*args, **kwargs)
        else:
            server.reply(info, RText(f"你没有权限执行此命令. 当前权限：{perm=}", RColor.red))
 
    return warp

def permission_admin(func):
    def warp(*args, **kwargs):
        # print(f"*args {args}  **kwargs {kwargs}")
        server, info = __get(args[0])
        perm = server.get_permission_level(info)

        # print(f"warp(): {args} {kwargs}")
        if perm >= PermissionLevel.ADMIN:
            func(*args, **kwargs)
        else:
            server.reply(info, RText(f"你没有权限执行此命令. 当前权限：{perm=}", RColor.red))
 
    return warp


"""
# 这是关键字，不要用作函数名
def match(re_str, s_str, groups=(0,)) -> tuple:
    print("这是旧的函数名称，不要用作函数名。 请使用 rematch() 函数。")
    lg = []
    result = re.match(re_str, s_str)
    if result:
        for i in groups:
            lg.append(result.group(i))

    return tuple(lg)
"""

def rematch(re_str, s_str, groups=(0,)) -> tuple:
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


def playsound(server: ServerInterface, player: str):
    server.rcon_query(f"execute at {player} run playsound minecraft:entity.player.levelup player {player}")


def get_players(server: ServerInterface) -> list[str]:
    # 获取在线玩家
    result = server.rcon_query("list")
    server.logger.debug(f"result = server.rcon_query('list') -->\n{result}")

    players, playernames = rematch("There are ([0-9]+) of a max of ([0-9]+) players online: (.*)", result, (1, 3))
    if players == "0":
        return []

    players = []
    for s in playernames.split(","):
        players.append(s.strip())
    
    return players

def player_online(server, player) -> bool:
    """
    检测玩家是否在线
    """

    result = server.rcon_query(f"experience query {player} points")

    if rematch(f"{player} has ([0-9]+) experience points", result):
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
def event_player_death(server: ServerInterface, info: Info) -> str|None:
    result = rematch(r"\* (.*) 死了", info, (1,))
    if result:
        # player 死亡
        player = result[0]
        result = server.rcon_query(f"data get entity {player} DeathTime")
        if result:
            deathtime = rematch(f"{player} has the following entity data: (.*)s", result, (1,))
            t = deathtime[0]
            server.logger.debug(f"玩家 {player} 的死亡时间计数：{deathtime}")
            if t != "0":
                server.logger.info(f"检测到玩家 {player} 死亡")
                return player
    
    return None


def player_dimension(server: ServerInterface, info: Info) -> str|None:
    rcon_result = server.rcon_query(f"data get entity {info.player} Dimension")
    if rcon_result is None:
        server.reply(info, RText("无法获取玩家维度信息，rcon返回None。", RColor.red))
        server.logger.error("rcon_query returned None when getting player dimension.")
        return

    r = rematch(fr'{info.player} has the following entity data: "(.*)"', rcon_result, (1,))
    if not r:
        server.reply(info, RText("无法解析玩家维度信息。", RColor.red))
        server.logger.error(f"Failed to match dimension info from rcon_result: {rcon_result}")
        return

    return r[0]


def player_pos(server: PluginServerInterface, info: Info) -> tuple[float,float,float]|None:
    rcon_result = server.rcon_query(f"data get entity {info.player} Pos")
    if rcon_result is None:
        server.reply(info, RText("无法获取玩家坐标信息，rcon返回None。", RColor.red))
        server.logger.error("rcon_query returned None when getting player position.")
        return

    cmd = fr"{info.player} has the following entity data: \[(-?[0-9\.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]"
    r = rematch(cmd, rcon_result, (1,2,3))
    if not r:
        server.reply(info, RText("无法解析玩家坐标信息。", RColor.red))
        server.logger.error(f"Failed to match position info from rcon_result: {rcon_result}")
        return

    return (float(r[0]), float(r[1]), float(r[2]))
