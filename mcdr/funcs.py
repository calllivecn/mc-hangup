#!/usr/bin/env python3
# coding=utf-8
# date 2021-07-24 15:42:24
# author calllivecn <c-all@qq.com>

import re
import time
from pathlib import Path


from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
from mcdreforged.permission.permission_level import PermissionLevel


CMDPREFIX="."

CONFIG_DIR = Path(__file__).parent.parent / "config"

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

def match(re_str, s_str, group=0):

    result = re.match(re_str, s_str)
    if result:
        return result.group(group)
    else:
        return None


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
