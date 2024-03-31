#!/usr/bin/env python3
# coding=utf-8
# date 2021-09-20 06:27:00
# author calllivecn <calllivecn@outlook.com>


import re
import time
import copy

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
    item_body,
)

ID_NAME = "autohealth"
PLUGIN_NAME = "自动回血3分钟或者到没有食物为止。"

CMD = CMDPREFIX + ID_NAME


# config file
CONF_INIT="""\
[autohealth]
# 检测血量时间间隔单位秒 min: , max: 15
Interval=1
# 0.1 ~ 1 之间
HealthPercentage=0.8

[minecraft]
bread = 2
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

# HealthPercentage = conf.getfloat("autohealth", "HealthPercentage")


FOOD = []
for node in conf.sections():

    if node == "autohealth":
        continue

    for k, v in conf.items(node):
        FOOD.append((":".join([node, k]), int(v)))



# 结束flag
EXIT=False
PLAYERS = {}


def check_food(server, player, food_local):
    result = server.rcon_query(f"data get entity {player} Inventory")

    # 只找只有一层{}中括号的物品， 目的是排除玩家身上容器里面的物品。
    text = item_body(result)

    server.logger.debug(f"FOOD: {food_local}")

    for index, (food, value) in enumerate(food_local):
        re_findall=f"""{{Slot: ([0-9]+)b, id: "{food}", Count: ([0-9]+)b}}"""
        server.logger.debug(re_findall)
        count = re.findall(re_findall, text)

        total = sum([int(x[1]) for x in count])
        server.logger.debug(f"查找玩家 {player} 回血食物 {food}：{total}")
        if total >= value:
            # 当前找到后，把它放到最前面，
            food_local[0], food_local[index] = food_local[index], food_local[0]
            return True
    
    return None

# 使用倍率加血，回血快。
def index_health(need, food, food_v):
    i = 0 # 加血倍率 0~28
    t_need = 0 
    reduce_food = 0 
    while True:
        t_n = (4<<i)
        t_f = food_v*(1<<i+1)
        if need >= t_n and food >= t_f:
            i+=1
            t_need, reduce_food = t_n, t_f 
        else:
            break

    return (i, reduce_food)


# 这样不行，clear 是最多减 v 个。
def clear_food(server, player, food_local):

    for index, (food, v) in enumerate(food_local):
        result = server.rcon_query(f"clear {player} {food} {v}")
        if re.match(f"No items were found on player {player}", result):
            continue
        else:
            # 当前找到后，把它放到最前面，
            food_local[0], food_local[index] = food_local[index], food_local[0]
            return True

    return False


def add_health_thread(server, player, number):
    # copy 一份 FOOD
    food_local = copy.deepcopy(FOOD)

    server.logger.info(f"{player} 自动回血技能启动。")
    server.tell(player, RText(f"自动回血技能启动", RColor.yellow))

    # 拿到玩家当前的最大血量
    result = server.rcon_query(f"attribute {player} minecraft:generic.max_health base get")

    re_match = re.match(f"Base value of attribute Max Health for entity {player} is (.*)", result)
    max_health = float(re_match.group(1))

    while (p := PLAYERS.get(player)):

        #calllivecn has the following entity data: 20.0f
        text = server.rcon_query(f"data get entity {player} Health")

        result = re.match(f"""{player} has the following entity data: (.*)f""", text)
        health = float(result.group(1))
        cmp = health / max_health
        if cmp <= number:

            index = check_food(server, player, food_local)
            food, v = food_local[0]
            if index:
                server.rcon_query(f"clear {player} {food} {v}")
                # result = server.rcon_query(f"clear {player} {food} {v}")
                # if re.match(f"No items were found on player {player}", result):

                # /effect give calllivecn minecraft:regeneration 1 3 true
                # 状态效果等级是从0开始的
                server.rcon_query(f"effect give {player} minecraft:instant_health 1 0 true")
                # server.rcon_query(f"effect give {player} minecraft:regeneration 1 3 true") 不行，太慢
                time.sleep(0.1)
            else:
                server.tell(player, RText(f"背包当前食物不够了!!!", RColor.red))
                PLAYERS.pop(player)
        else:
            time.sleep(Interval)


@new_thread("auto health")
def add_health(server, player, number):
    try:
        add_health_thread(server, player, number)
    except AttributeError:
        server.logger.info(f"玩家 {player} 下线, 自动回血技能结束。")
        if PLAYERS.get(player):
            PLAYERS.pop(player)


@permission
def help_and_run(src):
    server, info = __get(src)

    line = [
        f"{'='*10} 使用方法 {'='*10}",
        "可使用背包里的：面包，鸡肉，牛肉，猪肉，自动回血3分钟或者没有食物为止。",
        f"{CMD}                      查看方法和使用(一次回复2心，4点血。)",
        f"{CMD} <百分比>              血量低于多少时开始回血(建议0.8,后面需要添加上时间限制)",
        f"{CMD} stop                 结束技能",
    ]

    server.reply(info, "\n".join(line))


@permission
def auto(src, ctx):
    server, info = __get(src)
    number = float(ctx.get("number"))

    if PLAYERS.get(info.player):
        server.reply(info, f"自动回血技能已经发动，可以stop后重新发动。")
    else:
        PLAYERS[info.player] = 1
        if 0.01<= number <= 0.99:
            add_health(server, info.player, number)
        else:
            server.reply(info, f"number的有效范围: 0.01<= number < 0.99")



@permission
def stop(src, ctx):
    server, info = __get(src)
    if PLAYERS.get(info.player):
        PLAYERS.pop(info.player)
        server.reply(info, f"自动回血技能结束。")
    else:
        server.reply(info, f"自动回血技能未启动。")



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
