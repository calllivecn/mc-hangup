#!/usr/bin/env python3
# coding=utf-8
# date 2021-07-24 15:42:24
# author calllivecn <c-all@qq.com>

import re
import time
import configparser
from pathlib import Path


from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
from mcdreforged.api.decorator import new_thread

# mcdr_v2.x 还不能拿到 插件元数据
# from mcdreforged.plugin.meta.metadata import Metadata

# mcdr_v1.x
# from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer
# mcdr_v2.x
from mcdreforged.command.builder.nodes.basic import Literal
from mcdreforged.command.builder.nodes.arguments import QuotableText, Text, GreedyText, Integer

from mcdreforged.permission.permission_level import PermissionLevel


CMDPREFIX="."
# mcdr_v1.x 
# CONFIG_DIR = Path(__file__).parent.parent / "config"
# mcdr_v2.x
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"


# 

def readcfg(filename, init_context=None):
    if filename.exists():
        conf = configparser.ConfigParser()
        return conf.read_file(filename)
    else:
        return 



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


def match(re_str, s_str, group=0):

    result = re.match(re_str, s_str)
    if result:
        return result.group(group)
    else:
        return None


def check_rcon(server):

    rcon_result = server.rcon_query(f"list")
    if rcon_result is None:
        prompt = RText("rcon 没有开启, 请分别server.properties, MCDR/config.yml 开启。", RColor.red)
        server.logger.warning(prompt)
        server.say(RText(f"RCON 没有配置成功，请联系服主。", RColor.red))
        return False


def playsound(server, player):
    server.rcon_query(f"execute at {player} run playsound minecraft:entity.player.levelup player {player}")

def get_players(server):
    # 获取在线玩家
    result = server.rcon_query("list")
    server.logger.debug(f"result = server.rcon_query('list') -->\n{result}")

    match = re.match("There are ([0-9]+) of a max of ([0-9]+) players online:(.*)", result)

    if match.group(1) == "0":
        return []

    ls = match.group(3) 

    players = []
    for s in ls.split(","):
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

    l = re.match(f"{info.player} has ([0-9]+) experience levels", level).group(1)

    server.logger.debug(f"玩家 {info.player} 等级： {l}")

    if int(l) < 1:
        server.reply(info, RText("经验不足，至少需要1级", RColor.red))
        return False
    else:
        # 扣掉1级
        server.rcon_query(f"experience add {info.player} -1 levels")
        return True


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

        if j < (range_delimite - 1):
            line = line + RText("\n")

        output_list.append(line)
    return output_list
