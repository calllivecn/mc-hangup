#!/usr/bin/env python3
# coding=utf-8
# date 2021-09-20 06:27:00
# author calllivecn <c-all@qq.com>


import re

from funcs import (
    CMDPREFIX,
    CONFIG_DIR,
    __get,
    RText,
    RTextList,
    RColor,
    RAction,
    Literal,
    Integer,
    permission,
    PermissionLevel,
    item_body,
)

ID_NAME = "totem"
PLUGIN_NAME = "可使用用绿宝石，购买不死图腾。"

CMD = CMDPREFIX + ID_NAME

# 7个绿宝石买一个不死图腾
UNIT_PRICE=7

def emerald(server, player):
    result = server.rcon_query(f"data get entity {player} Inventory")

    text = item_body(result)

    count = re.findall(f"""Slot: ([0-9]+)b, id: "minecraft:emerald", Count: ([0-9]+)b""", text)
    emerald_total = sum([int(x[1]) for x in count])
    server.logger.debug(f"查询到的玩家绿宝石总数：{emerald_total}")

    return emerald_total


@permission
def help_and_run(src):
    server, info = __get(src)

    line1 = f"{'='*10} 使用方法 {'='*10}"
    line2 = f"{CMD}                      查看方法和使用"
    line3 = f"{CMD} <number>             购买number个不死图腾(7绿宝石/个)"
    line4 = RText(f"{CMD} all                   使用背包全部的绿宝石购买", RColor.yellow)

    total = emerald(server, info.player)

    number_all, _ = divmod(total, UNIT_PRICE)

    line4.set_hover_text(RTextList("当前能购买:", RText(f"{number_all}", RColor.green), "/个"))
    if number_all > 0:
        line4.set_click_event(RAction.run_command, f"{CMD} {number_all}")
    else:
        server.reply(info, RText("你当前背包绿宝石不够", RColor.red))

    server.reply(info, "\n".join([line1, line2, line3]))
    server.reply(info, RTextList(line4))


@permission
def shopping(src, ctx):
    server, info = __get(src)
    number = int(ctx.get("number"))

    emerald_total = emerald(server, info.player)

    number_all, _ = divmod(emerald_total, UNIT_PRICE)

    if number > number_all:
        server.reply(info, RText(f"当前最多只能买{number_all}个", RColor.red))
    else:
        reduce_emerald = number * UNIT_PRICE
        server.rcon_query(f"execute at {info.player} run clear {info.player} minecraft:emerald {reduce_emerald}")
        server.rcon_query(f"execute at {info.player} run give {info.player} minecraft:totem_of_undying {number}")


@permission
def shopping_all(src, ctx):
    server, info = __get(src)
    number = int(ctx.get("number"))
    server.rcon_query(f"{CMD} {number}")

def build_command():
    c = Literal(CMD).runs(lambda src: help_and_run(src))
    c.then(Integer("number").runs(lambda src, ctx: shopping(src, ctx)))
    c.then(Literal("all").then(Integer("number").runs(lambda src, ctx: shopping_all(src, ctx))))
    return c

def on_load(server, old_plugin):
    server.register_help_message(CMD, PLUGIN_NAME, PermissionLevel.USER)
    server.register_command(build_command())
