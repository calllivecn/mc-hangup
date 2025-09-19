#!/usr/bin/env python3
# coding=utf-8
# date 2021-07-31 14:06:17
# author calllivecn <calllivecn@outlook.com>

import re
import os
import time
import json
import copy
from pathlib import Path

from blockload.funcs import (
    RText,
    RTextList,
    Literal,
    RColor,
    RStyle,
    RAction,
    QuotableText,
    Text,
    CMDPREFIX,
    CONFIG_DIR,
    __get,
    permission,
    permission_admin,
    PermissionLevel,
    check_level,
    fmt,
)

PLAYER_MAX_BLOCK = 10

ID_NAME = "blockload"
PLUGIN_NAME = "使用forceload命令加载区块"

CMD = CMDPREFIX + ID_NAME
BL_CONFIG_DIR = CONFIG_DIR / ID_NAME

if not BL_CONFIG_DIR.exists():
    BL_CONFIG_DIR.mkdir()

def player_save(player, data):
    fullpathname = BL_CONFIG_DIR / (player + ".json")
    with open(fullpathname, "w+") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def player_load(player):
    fullpathname = BL_CONFIG_DIR / (player + ".json")

    if not fullpathname.exists():
        with open(fullpathname, "w") as f:
            f.write("""{}""")
        return {}

    with open(fullpathname, "r") as f:
        return json.load(f)


def click_text(player, label_name, world, x, y, z):
    r = RText(label_name, RColor.yellow)
    r.set_hover_text(RText(f"区块位置： {world} --> [{x}, {z}]", RColor.green))
    # r.set_click_event(RAction.run_command, f"{CMD} {label_name}")
    return r

@permission
def help(src):
    server, info = __get(src)

    msg=[f"{'='*10} 使用方法 {'='*10}",
    f"{CMD}                          查看使用方法",
    f"{CMD} list                     列出所有强制加载区块",
    f"{CMD} add <名字>                添加或修改当前位置的区块为强制加载区块",
    f"{CMD} remove <名字>             删除当前强制加载区块",
    f"{CMD} rename <旧名字> <新名字>   修改名字",
    f"{CMD} listall                  列出所有加载区块(管理员)",
    ]
    server.reply(info, "\n".join(msg))

"""
/forceload query<\n>
"A force loaded chunk was found in minecraft:overworld at: [19, -2]"

# 查询，当前坐标的区块， 有没强制加载。
/forceload query <x> <z>
"Chunk at [16, -2] in minecraft:overworld is not marked for force loading"

# 查询，当前坐标的区块， 有没强制加载。
/forceload query <x> <z>
"Chunk at [19, -2] in minecraft:overworld is marked for force loading"

# 添加
"Marked chunk [16, -2] in minecraft:overworld to be force loaded"

# 已经添加
"No chunks were marked for force loading"

# 删除
"Unmarked chunk [16, -2] in minecraft:overworld for force loading"
"""

@permission
def ls(src, ctx):
    server, info = __get(src)

    u = player_load(info.player)

    msg = [
    f"{'='*10} 当前没有强制加载区块, 快使用下面命令添加一个吧。 {'='*10}",
    f"{CMD} add <名字>",
    ]

    if u == {}:
        server.reply(info, "\n".join(msg))
    else:
        msg1 = [RText(f"{'='*10} 强制加载区块 {'='*10}\n", RColor.white)]
        msg2 = []
        for label_name, data in u.items():
            msg2.append(click_text(info.player, label_name, data["world"], data["x"], data["y"], data["z"]))

        msg = msg1 + fmt(msg2)
        server.reply(info, RTextList(*msg))

    server.logger.debug(f"list ctx -------------->\n{ctx}")


@permission_admin
def listall(src, ctx):
    server, info = __get(src)
    result = server.rcon_query(f"execute at {info.player} run forceload query")
    server.reply(info, result)


@permission
def add(src, ctx):
    server, info = __get(src)

    # 查看玩家的等级够不够
    if not check_level(server, info):
        server.reply(info, RText(f"当前等级不足，至少需要1级。", RColor.red))
        return

    # 查询坐标
    rcon_result = server.rcon_query(f"data get entity {info.player} Pos")
    position = re.search(rf"{info.player} has the following entity data: [(-?[0-9\.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d]", rcon_result)
    x, y, z = position.group(1), position.group(2), position.group(3)
    x, y, z = round(float(x)), round(float(y)), round(float(z))


    rcon_result = server.rcon_query(f"forceload add {x} {z}")
    load = re.match(f"Marked chunk [(-?[0-9]+), (-?[0-9]+)] in (.*) to be force loaded", rcon_result)

    if load is None:
        check = re.match("No chunks were marked for force loading", rcon_result)
        server.logger.error(f"{rcon_result=}")

        if check is None:
            server.reply(info, RText(f"未知错误，请报告服主。", RColor.red))
            server.logger.error(f"{check=}")
        else:
            server.reply(info, RText(f"当前区块已经强制加载！(可能是其他人加载)", RColor.yellow))

    else:

        #
        world = load.group(3)

        label_name = ctx["label_name"]

        u = player_load(info.player)

        u[label_name] = {"world": world, "x": x, "y": y, "z":z}

        server.tell(info.player, RTextList("强制加载区块: ", RText(label_name, RColor.yellow), " 添加成功"))

        player_save(info.player, u)

        if len(u) > PLAYER_MAX_BLOCK:
            server.reply(info, RText(f"强制加载区块已到最大数： {PLAYER_MAX_BLOCK} 请删除后添加", RColor.red))
            return 

    server.logger.debug(f"add ctx -------------->\n{ctx}")


@permission
def remove(src, ctx):
    server, info = __get(src)

    u = player_load(info.player)

    if u == {}:
        server.tell(info.player, RText(f"当前没有强制加载区块.", RColor.red))
    else:
        label_name = ctx.get("label_name")

        label = u.get(label_name)

        if label is None:
            server.reply(info, RTextList(RText("没有 "), RText(label_name, RColor.yellow), RText("强制加载区块")))
            return

        position = u.pop(label_name)
        world = position["world"]
        x, z = position["x"], position["z"]

        #
        rcon_result = server.rcon_query(f"execute in {world} run forceload remove {x} {z}")
        unload = re.match(f"Unmarked chunk [(-?[0-9]+), (-?[0-9]+)] in (.*) for force loading", rcon_result)

        if unload is None:
            server.reply(info, RText(f"未知错误，请报告服主。", RColor.red))
            server.logger.error(f"{rcon_result=}")
        
        else:
            player_save(info.player, u)
            server.reply(info, RTextList("强制加载区块: ", RText(label_name, RColor.yellow, RStyle.strikethrough), " 删除成功"))

    server.logger.debug(f"remove ctx -------------->\n{ctx}")


@permission
def rename(src, ctx):
    server, info = __get(src)

    u = player_load(info.player)

    if u == {}:
        server.tell(info.player, RText(f"当前没有强制加载区块.", RColor.red))
    else:
        label_name = ctx["label_name"]
        label = u.get(label_name)

        if label is None:
            server.reply(info, RText(f"没有 {label_name} 强制加载区块", RColor.red))
        else:
            if check_level(server, info):
                v = u.pop(label_name)
                u[ctx["label_name2"]] = v
                player_save(info.player, u)
                server.reply(info, RText("修改名称成功", RColor.green))

    server.logger.debug(f"rename ctx -------------->\n{ctx}")


def build_command():
    c = Literal(CMD).runs(lambda src: help(src))
    c.then(Literal("list").runs(lambda src, ctx: ls(src, ctx)))
    c.then(Literal("add").then(QuotableText("label_name").runs(lambda src, ctx: add(src, ctx))))
    c.then(Literal("remove").then(QuotableText("label_name").runs(lambda src, ctx: remove(src, ctx))))
    c.then(Literal("rename").then(QuotableText("label_name").then(QuotableText("label_name2").runs(lambda src, ctx: rename(src, ctx)))))
    c.then(Literal("listall").runs(lambda src, ctx: listall(src, ctx)))
    return c


def on_unload(server):
    server.logger.info(f"{ID_NAME} 卸载.")


def on_load(server, old_plugin):
    server.logger.info(f"{CMD} 的配置目录: {BL_CONFIG_DIR}")

    #while not server.is_server_startup():
    #    server.logger.debug("等待server启动完成")
    #    time.sleep(1)

    server.register_help_message(CMD, PLUGIN_NAME, PermissionLevel.USER)
    server.register_command(build_command())
