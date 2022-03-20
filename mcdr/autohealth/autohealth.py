#!/usr/bin/env python3
# coding=utf-8
# date 2021-09-20 06:27:00
# author calllivecn <c-all@qq.com>


import re
import time

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
    new_thread,
    permission,
    PermissionLevel,
)

ID_NAME = "autohealth"
PLUGIN_NAME = "可使背包里的：面包，鸡肉，牛肉，猪肉，自动回血3分钟或者没有食物为止。"

CMD = CMDPREFIX + ID_NAME

FOOD = {
    "minecraft:cooked_bread": 1,
    "minecraft:cooked_chicken": 1,
    "minecraft:cooked_beef": 2,
    "minecraft:cooked_porkchop": 2,
    "minecraft:cooked_cod": 1,
}

def check_food(server, player):
    text = server.rcon_query(f"data get entity {player} Invetory")

    for food in FOOD.items():
        count = re.findall(f"""Slot: ([0-9]+)b, id: {food}, Count: ([0-9]+)b""", text)
        total = sum([int(x[1]) for x in count])
        if total > 1:
            server.logger.debug(f"玩家 {player} 回血食物 {food}：{total}")
            return food
        else:
            return None
    
    return None


@new_thread("auto health")
def add_health(server, player):
    while True:
        #calllivecn has the following entity data: 20.0f
        text = server.rcon_query(f"data get entity {player} Health")
        result = re.findall(f"""{player} has the following entity data: (.*)f""", text)
        health = float(result.group(1))
        if health < 20:
            food = check_food(server, player)
            if food:
                server.rcon_query(f"clear {player} {food} {FOOD[food]}")
                server.rcon_query(f"effect give {player} minecraft:instant_health 1 {FOOD[food]}")
            else:
                server.tell(player, RText(f"背包当前食物不够了!!!", RColor.red))
                server.tell(player, RText(f"自动回血技能结束。", RColor.red))
                break
        else:
            time.sleep(0.1)



@permission
def help_and_run(src):
    server, info = __get(src)

    line1 = f"{'='*10} 使用方法 {'='*10}"
    line2 = f"{CMD}                      查看方法和使用"
    line3 = f"{CMD} <number>             支持运行时间(后面需要添加上时间限制)"
    # line4 = RText(f"{CMD} all                  使用背包全部的绿宝石购买", RColor.yellow)

    server.reply(info, "\n".join([line1, line2, line3]))


@permission
def shopping(src, ctx):
    server, info = __get(src)
    number = int(ctx.get("number"))
    add_health(server, info.player)

def build_command():
    c = Literal(CMD).runs(lambda src: help_and_run(src))
    c.then(Integer("number").runs(lambda src, ctx: shopping(src, ctx)))
    return c

def on_load(server, old_plugin):
    server.register_help_message(CMD, PLUGIN_NAME, PermissionLevel.USER)
    server.register_command(build_command())
