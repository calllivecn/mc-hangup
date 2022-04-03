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
    readcfg,
    RText,
    RTextList,
    RColor,
    RAction,
    Literal,
    Integer,
    Float,
    new_thread,
    permission,
    PermissionLevel,
)

ID_NAME = "autohealth"
PLUGIN_NAME = "可使背包里的：面包，鸡肉，牛肉，猪肉，自动回血3分钟或者没有食物为止。"

CMD = CMDPREFIX + ID_NAME


# config file
CONF_INIT="""\
[autohealth]
# 检测血量时间间隔单位秒 min: , max: 15
Interval=1
# 0.1 ~ 1 之间
HealthPercentage=0.8

[minecraft]
cooked_bread = 2
cooked_chicken= 2
cooked_cod = 2
cooked_beef = 1
cooked_porkchop = 1
"""

CONF_FILENAME=CONFIG_DIR / (ID_NAME + ".conf")

conf = readcfg(CONF_FILENAME, init_context=CONF_INIT)

# auto health 配置
Interval = conf.getfloat("autohealth", "Interval")

if Interval < 1:
    Interval = 1
elif Interval > 15:
    Interval = 15

HealthPercentage = conf.getfloat("autohealth", "Interval")


FOOD = {}
for node in conf.sections():

    if node == "autohealth":
        continue

    for k, v in conf.items(node):
        FOOD[":".join([node, k])] =  int(v)

"""
FOOD = {
    "minecraft:cooked_bread": 2,
    "minecraft:cooked_chicken": 2,
    "minecraft:cooked_cod": 2,
    "minecraft:cooked_beef": 1,
    "minecraft:cooked_porkchop": 1,
}
"""

# 结束flag
EXIT=False

def check_food(server, player):
    text = server.rcon_query(f"data get entity {player} Inventory")

    for food, value in FOOD.items():
        count = re.findall(f"""Slot: ([0-9]+)b, id: "{food}", Count: ([0-9]+)b""", text)
        total = sum([int(x[1]) for x in count])
        if total >= value:
            server.logger.debug(f"玩家 {player} 回血食物 {food}：{total}")
            return food
    
    return None


@new_thread("auto health")
def add_health(server, player, number):
    server.logger.info(f"{player} 自动回血技能启动。")
    server.tell(player, RText(f"自动回血技能启动", RColor.yellow))

    # 拿到玩家当前的最大血量
    result = server.rcon_query(f"attribute {player} minecraft:generic.max_health base get")
    re_match = re.match(f"Base value of attribute Max Health for entity calllivecn is (.*)", result)
    max_health = float(re_match.group(1))

    global EXIT
    while EXIT:
        #calllivecn has the following entity data: 20.0f
        text = server.rcon_query(f"data get entity {player} Health")
        result = re.match(f"""{player} has the following entity data: (.*)f""", text)
        health = float(result.group(1))
        cmp = health / max_health
        if cmp <= number:
            food = check_food(server, player)
            if food:
                result = server.rcon_query(f"clear {player} {food} {FOOD[food]}")
                if re.match(f"No items were found on player {player}", result):
                    server.tell(player, RText(f"背包当前食物不够了!!!", RColor.red))
                    EXIT=False
                else:
                    # server.rcon_query(f"effect give {player} minecraft:instant_health 1 {FOOD[food]} true")
                
                    # 状态效果等级是从0开始的
                    server.rcon_query(f"effect give {player} minecraft:instant_health 1 0 true")
                    # server.rcon_query(f"effect give {player} minecraft:regeneration 1 3 true") 不行，太慢
                    # /effect give calllivecn minecraft:regeneration 1 3 true
                    time.sleep(0.2)
            else:
                server.tell(player, RText(f"背包当前食物不够了!!!", RColor.red))
                EXIT=False
        else:
            time.sleep(Interval)

    server.logger.info(f"{player} 自动回血技能结束。")
    server.tell(player, RText(f"自动回血技能结束。", RColor.yellow))


@permission
def help_and_run(src):
    server, info = __get(src)

    line1 = f"{'='*10} 使用方法 {'='*10}"
    line2 = f"{CMD}                      查看方法和使用"
    line3 = f"{CMD} <百分比>              血量低于多少时开始回血(后面需要添加上时间限制)"
    line4 = f"{CMD} stop                 结束技能"

    server.reply(info, "\n".join([line1, line2, line3, line4]))


@permission
def auto(src, ctx):
    server, info = __get(src)
    number = float(ctx.get("number"))

    global EXIT
    if EXIT is True:
        server.reply(info, f"自动回血技能已经发动，可以stop后重新发动。")
    else:
        EXIT = True
        if 0.01<= number <= 0.99:
            add_health(server, info.player, number)
        else:
            server.reply(info, f"number的有效范围: 0.01<= number < 0.99")



@permission
def stop(src, ctx):
    server, info = __get(src)
    global EXIT
    EXIT = False
    server.reply(info, f"自动回血技能结束。")

def build_command():
    c = Literal(CMD).runs(lambda src: help_and_run(src))
    c.then(Float("number").runs(lambda src, ctx: auto(src, ctx)))
    c.then(Literal("stop").runs(lambda src, ctx: stop(src, ctx)))
    return c

def on_load(server, old_plugin):
    global EXIT
    if old_plugin is not None:
        old_plugin.EXIT=False
    server.register_help_message(CMD, PLUGIN_NAME, PermissionLevel.USER)
    server.register_command(build_command())
