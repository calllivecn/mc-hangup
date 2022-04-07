#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-14 16:01:21
# author calllivecn <c-all@qq.com>


import re
import time



from funcs import (
    CMDPREFIX,
    CONFIG_DIR,
    RText,
    RColor,
    RAction,
    RStyle,
    RTextList,
    new_thread,
    permission,
    PermissionLevel,
    # event_player_death,
)


CMD = CMDPREFIX + "maxhealth"

SOUL_DIR = CONFIG_DIR / "maxhealth"


"""
/attribute zx minecraft:generic.max_health base set 40
/effect give {player} minecraft:instant_health 1 0 # 一次加4心
"""

# 根本拿不到死亡信息
# def on_death_message(server, death_message):
    # server.logger.info(f"什么信息--> {death_message}")

def event_player_death(server, info):
    result = re.match(f"\* (.*) 死了", info)
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
            server.rcon_query(f"effect give {player} minecraft:instant_health 1 5")
            break

        time.sleep(1)

def on_info(server, info):
    if info.source == 0:
        player = event_player_death(server, info.content)
        if player:
            life(server, player)


# def build_command():
    # return LiteraCMD(prefix}").runs(lambda src, ctx: soul(src, ctx))

def on_load(server, old_plugin):
    # server.register_help_messag(CMD, RText("最大血量", RColor.yellow), PermissionLevel.USER)
    pass