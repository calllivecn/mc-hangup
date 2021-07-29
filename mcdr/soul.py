#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-09 11:18:15
# author calllivecn <c-all@qq.com>

import re
import os
import time
import json

from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer
from mcdreforged.permission.permission_level import PermissionLevel

from funcs import (
    CMDPREFIX,
    CONFIG_DIR,
    __get,
    timestamp,
    permission
)

PLUGIN_METADATA = {
    # ID（即插件ID）是您插件的身份字符串。它应该由小写字母，数字和下划线组成，长度为1到64
    'id': 'soul', 
    'version': '0.1.0',
    'name': '灵魂出窍',
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

SOUL_SPELL = [
    "मम्मी मम्मी सह",
    "भाई भगवान, उन लोगों के लिए दया करो जो कल्पित बौने हैं",
    "इस व्यक्ति की आत्मा को बुलाओ ~",
]

# 一次灵魂出窍时间
SOUL_TIME=180

if not SOUL_DIR.exists():
    os.makedirs(SOUL_DIR)

def get_soul_info(player):
    soul_player = SOUL_DIR / (player + ".json")
    if soul_player.exists():
        with open(soul_player) as f:
            return json.load(f)
    else:
        return {}

def set_soul_info(player, soul_info):
    soul_player = SOUL_DIR / (player + ".json")
    with open(soul_player, "w+") as f:
        return json.dump(soul_info, f, ensure_ascii=False, indent=4)

def condition(server, info):
    soul_player = SOUL_DIR / (info.player + ".json")
    if soul_player.exists():
        return True
    else:
        result = server.rcon_query(f"experience query {info.player} levels")
        level = int(re.search(f"{info.player} has ([0-9]+) experience levels", result).group(1))

        if level < 30:
            server.reply(info, RText("等你到一定等级了在来找我吧！", RColor.green))
            return False
        else:
            server.rcon_query(f"execute at {info.player} run experience add {info.player} -30 levels")
            server.rcon_query(f"execute at {info.player} run playsound minecraft:entity.player.levelup player {info.player}")
            server.reply(info, RText("你现在已经学习会了～", RColor.green))
            set_soul_info(info.player, {"timestamp": timestamp()})
            return True

@new_thread("soul")
def timing(server, player):

    # time.sleep(10) # 测试

    # 留出10秒，给倒计时。
    time.sleep(SOUL_TIME - 10)

    rcon_result = server.rcon_query(f"data get entity {player} playerGameType")
    result = re.match(f"{player} has the following entity data: ([0-9]+)", rcon_result)

    # 如果玩家退出
    if result is None:
        return 

    gamemode = result.group(1)
    if gamemode == "3":
        pass
    else:
        return 
    

    server.tell(player, RText(f"10秒后，返回身体.", RColor.green))
    time.sleep(5)

    for i in range(5, 0, -1):
       server.tell(player, RText(f"{i}秒后，返回身体.", RColor.green))
       time.sleep(1)

    player_soul = get_soul_info(player)
    if player_soul:
        world = player_soul["world"]
        x = player_soul["x"]
        y = player_soul["y"]
        z = player_soul["z"]

        server.rcon_query(f"execute at {player} in {world} run teleport {player} {x} {y} {z}")
        server.rcon_query(f"execute at {player} run gamemode survival {player}")
    else:
        server.tell(player, RText("出了点问题，请联系管理员。", RColor.red))
        server.logger.warning(f"玩家 {player} 被卡在灵魂模式了。。。")


@permission
def soul(src, ctx):
    server, info = __get(src)

    if not condition(server, info):
        return


    # 查询游戏模式
    rcon_result = server.rcon_query(f"data get entity {info.player} playerGameType")

    if rcon_result is None:
        prompt = "rcon 没有开启, 请分别server.properties, MCDR/config.yml 开启。"
        server.logger.warning(prompt)
        server.reply(info, RText(f"{CMD} 插件没有配置成功，请联系服主。", RColor.red))

        return
    
    gamemode = re.match(f"{info.player} has the following entity data: ([0-9]+)", rcon_result).group(1)

    # "Survival" == "0"
    # "Creative" == "1"
    # "Adventure" == "2"
    # "Spectator" == "3"
    if gamemode == "0":

        # 查询等级
        result = server.rcon_query(f"experience query {info.player} levels")
        level = int(re.search(f"{info.player} has ([0-9]+) experience levels", result).group(1))
        if level < 1:
            server.reply(info, RText("经验不足，至少需要1级", RColor.red))
            return

        # 查询世界
        rcon_result = server.rcon_query(f"data get entity {info.player} Dimension")

        world = re.match('{} has the following entity data: "(.*)"'.format(info.player), rcon_result).group(1)

        # 查询坐标
        rcon_result = server.rcon_query(f"data get entity {info.player} Pos")
        position = re.search(f"{info.player} has the following entity data: \[(-?[0-9\.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]", rcon_result)
        x, y, z = position.group(1), position.group(2), position.group(3)

        #x, y, z = round(float(x), 1), round(float(y), 1), round(float(z), 1)
        # 向上加0.5格，修复返回原地时，可能从不完整方块下落。
        x, y, z = round(float(x), 1), round(float(y), 1) + 0.3, round(float(z), 1)

        set_soul_info(info.player, {"timestamp": timestamp(), "world": world, "x": x, "y": y, "z": z})

        # 扣掉1级
        server.rcon_query(f"experience add {info.player} -1 levels")

        server.rcon_query(f"execute at {info.player} run gamemode spectator {info.player}")
        server.rcon_query(f"execute at {info.player} run effect give {info.player} minecraft:night_vision {SOUL_TIME} 0 true")
        server.rcon_query(f"execute at {info.player} run playsound minecraft:entity.player.levelup player {info.player}")

        server.reply(info, RText("注意！3分钟后会回到你的身体！(输入指令可提前返回)", RColor.yellow))
        timing(server, info.player)

    elif gamemode == "3":
        player_soul = get_soul_info(info.player)
        if player_soul:
            world = player_soul["world"]
            x = player_soul["x"]
            y = player_soul["y"]
            z = player_soul["z"]

            server.rcon_query(f"execute at {info.player} in {world} run teleport {info.player} {x} {y} {z}")
            server.rcon_query(f"execute at {info.player} run effect clear {info.player} minecraft:night_vision")
            server.rcon_query(f"execute at {info.player} run gamemode survival {info.player}")

        else:
            server.reply(info, RText("出了点问题，请联系管理员。", RColor.red))
            server.logger.warning(f"玩家 {info.player} 被卡在灵魂模式了。。。")

    
    else:
        return

# def on_user_info(server, info):
    # pass

def on_player_joined(server, player, info):

    soul_player = get_soul_info(player)
    if not soul_player:
        return

    rcon_result = server.rcon_query(f"data get entity {player} playerGameType")
    gamemode = re.match(f"{player} has the following entity data: ([0-9]+)", rcon_result).group(1)

    if gamemode == "3":
        t = timestamp()
        if (t - soul_player["timestamp"]) >= 180:
        # if (t - soul_player["timestamp"]) >= 25:
            world = soul_player["world"]
            x, y, z = soul_player["x"], soul_player["y"], soul_player["z"]
            server.rcon_query(f"execute at {player} in {world} run teleport {player} {x} {y} {z}")
            server.rcon_query(f"execute at {player} run gamemode survival {player}")
            #server.reply(f"你在灵魂状态太久，已回到身体。")

def build_command():
    return Literal(CMD).runs(lambda src, ctx: soul(src, ctx))

def on_load(server, old_plugin):
    server.register_help_message(CMD, RText(PLUGIN_METADATA["name"], RColor.yellow), PermissionLevel.USER)
    server.register_command(build_command())
