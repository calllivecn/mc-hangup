#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-09 11:18:15
# author calllivecn <c-all@qq.com>

import re
import os
import json
from pathlib import Path

from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer
from mcdreforged.permission.permission_level import PermissionLevel

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



cmdprefix = "." + PLUGIN_METADATA["id"]

cur_dir = os.path.dirname(os.path.dirname(__file__))
SOUL_DIR = Path(cur_dir) / "config" / PLUGIN_METADATA["id"]

SOUL_SPELL = [
    "मम्मी मम्मी सह",
    "भाई भगवान, उन लोगों के लिए दया करो जो कल्पित बौने हैं",
    "इस व्यक्ति की आत्मा को बुलाओ ~",
]

if not SOUL_DIR.exists():
    os.makedirs(SOUL_DIR)

def get_soul_info(player):
    soul_player = SOUL_DIR / (player + ".json")
    if soul_player.exists():
        with open(soul_player) as f:
            return json.load(f)
        os.remove(soul_player)
    else:
        return {}

def set_soul_info(player, soul_info):
    soul_player = SOUL_DIR / (player + ".json")
    with open(soul_player, "w+") as f:
        return json.dump(soul_info, f, ensure_ascii=False, indent=4)

def __get(src):
    return src.get_server(), src.get_info()


def soul(server, info):
    # 查询游戏模式
    rcon_result = server.rcon_query(f"data get entity {info.player} playerGameType")

    if rcon_result is None:
        prompt = "rcon 没有开启, 请分别server.properties, MCDR/config.yml 开启。"
        server.logger.warning(prompt)
        server.reply(info, RText(f"{cmdprefix} 插件没有配置成功，请联系服主。", RColor.red))

        return
    
    gamemode = re.match('{} has the following entity data: ([0-9]+)'.format(info.player), rcon_result).group(1)

    # "Survival" == "0"
    # "Creative" == "1"
    # "Adventure" == "2"
    # "Spectator" == "3"
    if gamemode == "0":

        # 查询世界
        rcon_result = server.rcon_query(f"data get entity {info.player} Dimension")

        world = re.match('{} has the following entity data: "(.*)"'.format(info.player), rcon_result).group(1)

        # 查询坐标
        rcon_result = server.rcon_query(f"data get entity {info.player} Pos")
        position = re.search(f"{info.player} has the following entity data: \[(-?[0-9\.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]", rcon_result)
        x, y, z = position.group(1), position.group(2), position.group(3)
        x, y, z = round(float(x), 1), round(float(y), 1), round(float(z), 1)

        set_soul_info(info.player, {"world": world, "x": x, "y": y, "z": z})

        server.rcon_query(f"execute at {info.player} run gamemode spectator {info.player}")


    elif gamemode == "3":
        player_soul = get_soul_info(info.player)
        if player_soul:
            world = player_soul["world"]
            x = player_soul["x"]
            y = player_soul["y"]
            z = player_soul["z"]

            server.rcon_query(f"execute at {info.player} in {world} run teleport {info.player} {x} {y} {z}")
            server.rcon_query(f"execute at {info.player} run gamemode survival {info.player}")

        else:
            server.reply(info, RText("出了点问题，请联系管理员。", RColor.red))
            server.logger.warning(f"玩家 {info.player} 被卡在灵魂模式了。。。")

    
    else:
        server.reply(info, RText(f"哦~天哪，你不在五行中，我帮不了你...", RColor.green))
        return


def soul_runs(src, ctx):
    server, info = __get(src)

    perm = server.get_permission_level(info) 
    #server.logger.info(f"info --> {info}\n permission --> {perm}")

    if perm >= PermissionLevel.USER:
        soul(server, info)

def on_user_info(server, info):
    pass

def on_player_joined(server, player, info):
    pass

def build_command():
    return Literal(f"{cmdprefix}").runs(soul_runs)

def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, RText("招唤出你的灵魂", RColor.yellow), PermissionLevel.USER)
    server.register_command(build_command())
