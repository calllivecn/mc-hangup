#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-08 10:10:15
# author calllivecn <calllivecn@outlook.com>

import re

from funcs import (
    CMDPREFIX,
    __get,
    RText,
    RColor,
    RAction,
    RTextList,
    Literal,
    Integer,
    permission,
    PermissionLevel,
)


ID_NAME = "xps"
PLUGIN_NAME = "存储和共享经验(附魔瓶)"

cmdprefix = CMDPREFIX + ID_NAME


LEVEL30TOTAL = 2.5* 30**2 - 40.5*30 + 360
EXPERIENCE_BOTTLE = 7

def __get_xp_total(server, player):
    result = server.rcon_query(f"experience query {player} levels")
    level_str = re.match(f"{player} has ([0-9]+) experience levels", result).group(1)
    level = int(level_str)

    result = server.rcon_query(f"experience query {player} points")
    xp_str = re.match(f"{player} has ([0-9]+) experience points", result).group(1)
    xp = int(xp_str)

    xp_total = 0
    if level <= 16:
        xp_total += level**2 + 6*level + 7    

    if 16 < level <=31:
        xp_total += (2.5*(level**2) - 40.5*level + 360)

    if 31 < level:
        xp_total += (4.5*(level**2) - 162.5*level + 2220)

    return xp_total + xp


def __store_space(xp):
    if xp <= 0:
        return 0, 0

    number = xp // EXPERIENCE_BOTTLE


    storespace, s = divmod(number, 64)
    if s > 0:
        storespace += 1 

    return int(number), int(storespace)


@permission
def help_and_run(src):
    server, info = __get(src)

    line1 = f"{'='*10} 使用方法 {'='*10}"
    line2 = f"{cmdprefix}                      查看方法和使用"
    line3 = f"{cmdprefix} store <number>       存储number瓶经验(7经验/瓶)"
    line4 = RText(f"{cmdprefix} store-all            存储全部经验", RColor.yellow)
    line5 = RText(f"{cmdprefix} store-30             存储多出30级的经验", RColor.yellow)

    xp_total = __get_xp_total(server, info.player)

    number_all, space_all = __store_space(xp_total)

    number_30, space_30 = __store_space(xp_total - LEVEL30TOTAL)
    
    line4.set_hover_text(RTextList("当前能存:", RText(f"{number_all}", RColor.green), "瓶(", RText(f"{space_all}", RColor.blue), ")格"))
    if number_all > 0:
        line4.set_click_event(RAction.run_command, f"{cmdprefix} store {number_all}")

    line5.set_hover_text(RTextList("当前能存:", RText(f"{number_30}", RColor.green), "瓶(", RText(f"{space_30}", RColor.blue), ")格"))
    if number_30 > 0:
        line5.set_click_event(RAction.run_command, f"{cmdprefix} store {number_30}")

    server.reply(info, "\n".join([line1, line2, line3]))
    server.reply(info, RTextList(line4, "\n", line5))

@permission
def store(src, ctx):
    server, info = __get(src)

    number = int(ctx.get("number"))

    if number <= 0:
        server.reply(info, RText("不能这样存储经验", RColor.red))
        return

    xp_total = __get_xp_total(server, info.player)

    server.logger.debug(f"玩家 {info.player} 当前总经验 {xp_total}")

    number_all, _ = __store_space(xp_total)

    if number_all < number:
        server.reply(info, RText(f"当前最多只能存储{number_all}瓶", RColor.red))
    else:
        reduce_xp = number * EXPERIENCE_BOTTLE
        server.rcon_query(f"execute at {info.player} run experience add {info.player} -{reduce_xp} points")
        server.rcon_query(f"execute at {info.player} run give {info.player} minecraft:experience_bottle {number}")

@permission
def store_all(src, ctx):
    server, info = __get(src)
    number = int(ctx.get("number"))
    server.rcon_query(f"{cmdprefix} {number}")
    #server.rcon_query(f"execute at {info.player} run say {cmdprefix} {number}")

    
@permission
def store_30(src, ctx):
    server, info = __get(src)
    number = int(ctx.get("number"))
    server.rcon_query(f"{cmdprefix} {number}")
    #server.rcon_query(f"execute at {info.player} run say {cmdprefix} {number}")


def build_command():
    c = Literal(cmdprefix).runs(lambda src: help_and_run(src))
    c.then(Literal("store").then(Integer("number").runs(lambda src, ctx: store(src, ctx))))
    c.then(Literal("store-all").then(Integer("number").runs(lambda src, ctx: store_all(src, ctx))))
    c.then(Literal("store-30").then(Integer("number").runs(lambda src, ctx: store_30(src, ctx))))
    return c



def on_unload(server):
    pass

def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, PLUGIN_NAME, PermissionLevel.USER)
    server.register_command(build_command())

def on_player_joined(server, player, info):
    pass

def on_player_left(server, player):
    pass
