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
    else:
        return {}


def soul(server, info):
    # 查询游戏模式
    result = server.rcon_query(f"data get enetity {info.player} Gamemode")
    if rcon_result is None:
        prompt = "rcon 没有开启, 请分别server.properties, MCDR/config.yml 开启。"
        server.logger.warning(prompt)
        server.reply(info, RText(f"{cmdprefix} 插件没有配置成功，请联系服主。", RColor.red))
    
    gamemode = re.match("还没写", result).group(1)
    
    if gamemode == "survival":

    elif gamemode == "spectator":
    
    else:
        server.reply(info, RText(f"哦~天哪，你不在五行中，我帮不了你...", RColor.green))


    # 查询世界
    rcon_result = server.rcon_query(f"data get entity {info.player} Dimension")

    world = re.match('{} has the following entity data: "(.*)"'.format(info.player), rcon_result).group(1)

    # 查询坐标
    rcon_result = server.rcon_query(f"data get entity {info.player} Pos")
    position = re.search(r"\[.*\]", rcon_result).group()
    x, y, z = position.strip("[]").split(",")
    x, y, z = round(float(x.strip(" d")), 1), round(float(y.strip(" d")), 1), round(float(z.strip(" d")), 1)


def on_user_info(server, info):
    permission = info.get_permission_level(info)

    if permission >= 1:
        soul(server, info)
    else:
        server.reply(info, RText("没有权限", RColor.red))

def on_player_joined(server, info):


def build_command():
    return Literal(f"{cmdprefix}").runs(soul)

def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, RText("招唤出你的灵魂", RColor.yellow))
    server.register_command(build_command())