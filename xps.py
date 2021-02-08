#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-08 10:10:15
# author calllivecn <c-all@qq.com>

import re
import os
import json

from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer

PLUGIN_METADATA = {
    # ID（即插件ID）是您插件的身份字符串。它应该由小写字母，数字和下划线组成，长度为1到64
    'id': 'xps', 
    'version': '0.1.0',
    'name': '把经验存在附魔瓶',
    'author': [
        'calllivecn'
   ],
    'link': 'https://github.com/calllivecn/mcdr/xps.py',
    'dependencies': {
        'mcdreforged': '>=1.0.0',
    }
}

cmdprefix = "." + plugin_id


def __get(src):
    return src.get_server(), src.get_info()

LEVEL30TOTAL = 2.5* 30**2 - 40.5*30 + 360
EXPERIENCE_BOTTLE = 7

def __get_xp_total(server, player):
    result = server.rcon_query(f"experience query {info.player} levels")
    level_str = re.match(f"{info.player} has ([0-9]+) experience levels", result).group(1)
    level = int(level_str)

    result = server.rcon_query(f"experience query {info.player} points")
    xp_str = re.match(f"{info.player} has ([0-9]+) experience points", result).group(1)
    xp = int(xp_str)

    xp_total = 0
    if level <= 16:
        xp_total += level**2 + 6*level + 7    
    elif 16 < level <=31:
        xp_total += 2.5* level**2 - 40.5*level + 360
    else:
        xp_total += 4.5* level**2 - 162.5*level + 2220

    return xp_total += xp


def __store_space(xp):
    if xp <= 0:
        return 0, 0

    number = xp // EXPERIENCE_BOTTLE


    storespace, s = divmod(number, 64)
    if s > 0:
        storespace += 1 

    return number, storespace


def help_and_run(src):
    server, info = __get(src)

    line1 = f"{'='*10} 使用方法 {'='*10}"
    line2 = f"{cmdprefix}                      查看方法和使用"
    line3 = f"{cmdperifx} store <number>       存储number瓶经验(7经验/瓶)"
    line4 = f"{cmdperifx} store-all            存储全部经验"
    line5 = f"{cmdperifx} store-30             存储多出30级的经验"

    xp_total = __get_xp_total(info.player)

    number_all, space_all = __store_space(xp_total)

    number_30, space_all = __store_space(xp_total - LEVEL30TOTAL)
    
    line5.set_hover_text(RTextList("当前能存:", RText(f"{number_all}", RColor.green), "瓶(", RText(f"{space_all}", RColor.blue), ")格"))
    if number_all > 0:
        line4.set_click_event(RAction.run_command, f"{cmdprefix} store {number_all}")

    line5.set_hover_text(RTextList("当前能存:", RText(f"{number_30}", RColor.green), "瓶(", RText(f"{space_30}", RColor.blue), ")格"))
    if number_30 > 0:
        line5.set_click_event(RAction.run_command, f"{cmdprefix} store {number_30}")

    server.reply(info, "\n".join([line1, line2, line3]
    server.reply(RTextList(RText(line4, RColor.yellow), "\n", RText(line5, RColor.yellow))


def store(src, ctx):
    server, info = __get(src)

    number = int(ctx.get("number"))

    xp_total = __get_xp_total(info.player)

    number_all, _ = __store_space(xp_total)

    if number_all < number:
        server.reply(info, RText(f"当前最多只能存储{number_all}瓶", RColor.red))
    else:
        reduce_xp = number_all * EXPERIENCE_BOTTLE
        server.rcon_query(f"execute at {info.player} experience add {info.player} -{reduce_xp} points")
        server.rcon_query(f"execute at {info.player} run give {info.player} minecraft:experience_bottle {number_all}")
        server.cron_query()

def store_all(src, ctx):
    server, info = __get(src)
    number = int(ctx.get("number"))
    server.rcon_query(f"{cmdprefix} {number}")

    
def store_30(src, ctx):
    server, info = __get(src)
    number = int(ctx.get("number"))
    server.rcon_query(f"{cmdprefix} {number}")

def build_command():
    c = Literal(cmdprefix).runs(help)
    c.then(Literal("store").then(Integer("number").runs(ls)))
    c.then(Literal("store-all").then(Integer("number").runs(store_all)))
    c.then(Literal("store-30").then(Integer("number").runs(store_30)))
    return c


def on_unload(server):
    pass

def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, PLUGIN_METADATA["name"])
    server.register_command(build_command())

def on_player_joined(server, player):
    pass

def on_player_joined(server, player, info):
    pass

def on_player_left(server, player):
    pass
