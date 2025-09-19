#!/usr/bin/env python3
# coding=utf-8
# date 2025-06-02 21:50:37
# author calllivecn <calllivecn@outlook.com>

import re
import time
import json


from disenchantment.funcs import (
    CMDPREFIX,
    CONFIG_DIR,
    __get,
    RText,
    RColor,
    Literal,
    permission,
    PermissionLevel,
)

ID_NAME = "disenchantment"
PLUGIN_NAME = '拆解附魔'

CMD = CMDPREFIX + ID_NAME

SOUL_DIR = CONFIG_DIR / ID_NAME


@permission
def disenchantment(src, ctx):
    server, info = __get(src)

    # rcon_result = server.rcon_query(f"data get entity {info.player} SelectedItem")
    rcon_result = server.rcon_query(f"data get entity {info.player} SelectedItem.components")
    cmd = f"{info.player} has the following entity data: (.*)"
    result = re.match(cmd, rcon_result)
    # 一个正确结果的示例
    # calllivecn has the following entity data: {"minecraft:stored_enchantments": {"minecraft:fire_protection": 4, "minecraft:density": 4}}
    # 二个正确结果的示例
    # {"minecraft:enchantments": {"minecraft:mending": 1}, "minecraft:damage": 63}

    if result is None:
        server.reply(info, RText(f"1:主手上没有已附魔物品可以拆解。", RColor.red))
        # server.reply(info, RText(f"主手上没有物品。", RColor.red))
        # server.tell(player, RText(f"10秒后，返回身体.", RColor.green))
        return
    
    # 转换为普通的 Python dict（可选）
    js1 = json.loads(result.group(1))

    enchantments = js1.get("minecraft:stored_enchantments", None)
    if enchantments is None:
        enchantments = js1.get("minecraft:enchantments", None)
        if enchantments is None:
            server.reply(info, RText(f"2:主手上没有已附魔物品可以拆解。", RColor.red))
            return

    enchantments_count = len(enchantments)

    # 检测副手上有没>=数量的空白书籍。 在1.21.x 上没有找到检测副手物品方法
    cmd = f"""data get entity {info.player} Inventory[{{"Slot": 0b}}]"""
    print(f"{cmd=}")
    rcon_result = server.rcon_query(cmd)

    # 这样就是不行？？。。
    # rcon_result = server.rcon_query(f"""data get entity {info.player} Inventory[{{"Slot": 102b}}]""")  # 副手物品栏

    print(f"{rcon_result=}")

    result = re.match(f"{info.player} has the following entity data: (.*)", rcon_result)
    if result is None:
        server.reply(info, RText(f"1:第一个物品栏没书籍。", RColor.red))
        return

    print("1:第一个物品栏没书籍。过了。")

    cmd = f"""{{count: (.*), Slot: 0b, id: "minecraft:book"}}"""
    item = re.match(cmd, result.group(1))
    if item is None:
        server.reply(info, RText(f"2:第一个物品栏没书籍。", RColor.red))
        return
    
    print(f"{item=}")
    item_count = item.group(1)
    if item_count is None:
        server.reply(info, RText(f"报错了。", RColor.red))
        return
    
    if int(item_count) < enchantments_count:
        server.reply(info, RText(f"副手上没有足够的空白书籍。", RColor.red))
        return

    # give 附魔物品语法
    # /give @s enchanted_book[minecraft:enchantments={"minecraft:fire_protection": 4, "minecraft:depth_strider": 1}]
    for enchantment, level in enchantments.items():
        # 生成指令
        server.rcon_query(f"""give {info.player} minecraft:enchanted_book[minecraft:stored_enchantments={{"{enchantment}": {level}}}]""")
        time.sleep(0.1)
    
    # 清除主手物品的附魔
    # server.rcon_query(f"""item replace entity @s weapon.mainhand with minecraft:diamond_sword components {"minecraft:item_name": "{"text":"我的剑"}"}""")
    server.rcon_query(f"""item replace entity {info.player} weapon.mainhand with minecraft:air""")

    server.rcon_query(f"""clear {info.player} minecraft:book {enchantments_count}""")  # 清除副手书籍

    server.reply(info, RText(f"拆解附魔完成。", RColor.green))


def build_command():
    return Literal(CMD).runs(lambda src, ctx: disenchantment(src, ctx))

def on_load(server, old_plugin):
    server.register_help_message(CMD, RText(PLUGIN_NAME, RColor.yellow), PermissionLevel.USER)
    server.register_command(build_command())
