#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-14 16:01:21
# author calllivecn <c-all@qq.com>


import re
import time

from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList


from funcs import (
    CMDPREFIX,
    CONFIG_DIR,
    permission,
    PermissionLevel,
)

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



CMD = CMDPREFIX + PLUGIN_METADATA["id"]

SOUL_DIR = CONFIG_DIR / PLUGIN_METADATA["id"]

players_deathcount = {}

def init_player(server):
    result = server.rcon_query("list")
    # server.logger.info(f"players() server.rcon_query() --> {result}")
    match = re.match("There are [0-9]+ of a max of ([0-9]+) players online: (.*)", result)
    players_raw = match.group(1).split(",")
    for p in players_raw:
        players_deathcount.append(p.strip())
    
    for p in players_deathcount.keys():
        result = server.rcon_query(f"scoreboard players get {p} death")
        if result:
            death = re.match(f"{p} has ([0-9]+) \[死亡记数\]", result)
            deathcount = int(death.group(1))
            players_deathcount[p] = deathcount
        else:
            server.rcon_query(f"scoreboard players set {p} death 0")
            players_deathcount[p] = 0


"""
/attribute zx minecraft:generic.max_health base set 40
"""

def haveplayer(server, content):
    # 排除玩家在线时，关服的情况。排除玩家退出的情况。
    if re.search("(.*) lost connection", content) or re.match(f"(.*) left the game", content):
        return None

    for player in players_deathcount.keys():
        result = re.search(player, content)
        if result:
            return player
    
    return None


# 根本拿不到死亡信息
# def on_death_message(server, death_message):
    # server.logger.info(f"什么信息--> {death_message}")

# 等玩家重生
@new_thread
def life(server, player):
    while True:
        time.sleep(0.2)
        result = server.rcon_query(f"data get entity {player} DeathTime")
        deathtime = re.match(f"{player} has the following entity data: ([0-9]+)s", result)
        # 说明玩家以选择重生
        if int(deathtime.group(1)) == 0:
            server.rcon_query(f"attribute {player} minecraft:generic.max_health base set 40")
            server.rcon_query(f"effect give {player} minecraft:instant_health 1 40")
            break

        time.sleep(1)

def on_info(server, info):
    if info.source == 0:
        death_player = haveplayer(server, info.content)
        if death_player:
            result = server.rcon_query(f"scoreboard players get {death_player} death")
            count = re.match(f"{death_player} has ([0-9]+) \[死亡记数\]", result)

            if death_player and count:
                c = int(count.group(1))

                if players_deathcount[death_player] != c:
                    players_deathcount[death_player] = c
                    server.logger.info(f"检测到玩家：{death_player} 死亡, 次数为：{count.group(1)}")

        players_deathcount[info.player] = int(count.group(1))
    else:
        players_deathcount[info.player] = 0
    
    server.logger.info(f"输出玩家字典 --> {players_deathcount}")

def on_player_left(server, player):
    if player in players_deathcount:
        players_deathcount.pop(player)


# def build_command():
    # return LiteraCMD(prefix}").runs(lambda src, ctx: soul(src, ctx))

def on_load(server, old_plugin):
    server.register_help_messag(CMD, RText("最大血量", RColor.yellow), PermissionLevel.USER)

    # 如果是第一次启动
    if old_plugin == None:
        init_player(server)
    else:
        players_deathcount.update(old_plugin.players_deathcount)

    # server.register_command()