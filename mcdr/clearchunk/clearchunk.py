#!/usr/bin/env python3
# coding=utf-8
# date 2025-06-28 21:25:17
# author calllivecn <calllivecn@outlook.com>

import re
import os
import time
import json


from funcs import (
    CMDPREFIX,
    CONFIG_DIR,
    __get,
    RText,
    RColor,
    Literal,
    Integer,
    new_thread,
    timestamp,
    permission,
    PermissionLevel,
    PluginServerInterface,
    Info,
)

ID_NAME = "clearchunk"
PLUGIN_NAME = "一步步清空指定区域"

CMD = CMDPREFIX + ID_NAME

CLEARCHUNK_DIR = CONFIG_DIR / ID_NAME

CLEARCHUNK_PROGRESS = {}


server: PluginServerInterface
info: Info


if not CLEARCHUNK_DIR.exists():
    os.makedirs(CLEARCHUNK_DIR)

def get_progress_info(player):
    j = CLEARCHUNK_DIR / (player + ".json")
    if j.exists():
        with open(j) as f:
            return json.load(f)
    else:
        return {}

def set_progress_info(player, progress):
    j = CLEARCHUNK_DIR / (player + ".json")
    with open(j, "w+") as f:
        return json.dump(progress, f, ensure_ascii=False, indent=4)

def connected_blocks(x, y, z) -> list[tuple[int, int, int]]:
    # 相连六面的方块坐标
    pos = [
        (x, y, z-1),  # 前
        (x, y, z+1),  # 后
        (x-1, y, z),  # 左
        (x+1, y, z),  # 右
        (x, y+1, z),  # 上
        (x, y-1, z),  # 下
    ]
    return pos


def clear_fluid(x0, y0, z0, fluid: str = "water") -> None:
    # 清理流体，这里主要是 水源或熔岩源

    water_found = set((x0, y0, z0))  # 用集合来存储找到的水源方块

    water_found_next = set()  # 用来存储下一个循环中找到的水源方块

    water_count = 0  # 计数器，记录找到的水源方块数量

    while len(water_found) > 0:

        # 取出一个水源方块
        for x, y, z in water_found:

            # 把相连的水流方块添加进去
            Pos = connected_blocks(x, y, z)
            for x, y, z in Pos:
                # 是水源。不区分会更好。
                # rcon_result = server.rcon_query(f"execute if block {x} {y} {z} minecraft:{fluid}[level=0]")
                rcon_result = server.rcon_query(f"execute if block {x} {y} {z} minecraft:{fluid}")
                if rcon_result == "Test passed":
                    water_found_next.add((x, y, z))
            
        water_count += len(water_found)
        for x, y, z in water_found:
            server.rcon_query(f"setblock {x} {y} {z} minecraft:air strict")
        
        # 清理完当前找到的水源方块后，更新 water_found
        water_found = water_found_next
        water_found_next = set()  # 清空下一个循环的集合

    server.reply(info, RText(f"清理: {len(water_found)} 个数的水流", RColor.green))


def check_destroy_block(x, y, z) -> bool:
    # 检测是不是空气。
    rcon_result = server.rcon_query(f"execute if block {x} {y} {z} minecraft:air")
    if rcon_result == "Test passed": # or rcon_result == "Test failed":
        # server.tell(info.player, RText(f"位置 {x} {y} {z} 已经是空气了。", RColor.red))
        return True

    elif rcon_result == "That position is not loaded":
        server.reply(info, RText(f"位置 {x} {y} {z} 未加载，请先加载该区域。", RColor.red))
        return False

    # 检测是水源
    # rcon_result = server.rcon_query(f"execute if block {x} {y} {z} minecraft:water[level=0]")
    rcon_result = server.rcon_query(f"execute if block {x} {y} {z} minecraft:water")
    if rcon_result == "Test passed":
        #尝试清理所有相连的水(一个方块的六个相连的方块)
        clear_fluid(x, y, z, "water")
        return True

    # 检测是熔岩源
    # rcon_result = server.rcon_query(f"execute if block {x} {y} {z} minecraft:lava[level=0]")
    rcon_result = server.rcon_query(f"execute if block {x} {y} {z} minecraft:lava")
    if rcon_result == "Test passed":
        #尝试清理所有相连的熔岩(一个方块的六个相连的方块)
        clear_fluid(x, y, z, "lava")
        return True

    # 检测是基岩跳过
    rcon_result = server.rcon_query(f"execute if block {x} {y} {z} minecraft:bedrock")
    if rcon_result == "Test passed":
        return True

    rcon_result = server.rcon_query(f"setblock {x} {y} {z} minecraft:air destroy")
    if rcon_result == "Could not set the block":
        #说明原本就是空气
        pass
    elif rcon_result.startswith("Changed the block at"): # Changed the block at 1051, 117, 1014  
        #说明清理成功
        pass

    return True


@new_thread("clerchunk")
def run(pos1, pos2, pos3, unique_id):

    x1, y1, z1 = pos1

    # 从上向下清理？
    for y in range(pos2[1], y1-1, -1):
        for x in range(x1, pos2[0] + 1):
            for z in range(z1, pos2[2] + 1):
                if not check_destroy_block(x, y, z):
                    return
                # 每清理10格就回收一次掉落物
                server.rcon_query(f"execute as @e[type=item,x={x1},y={y1},z={z1},dx={pos2[0]-x1},dy={pos2[1]-y1},dz={pos2[2]-z1}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")


    server.reply(info, RText("清理区域完成执行完成", RColor.green))


@permission
def main(src, ctx):

    unique_id = time.monotonic_ns()

    pos1 = (int(ctx.get("x1")), int(ctx.get("y1")), int(ctx.get("y1")))
    pos2 = (int(ctx.get("x2")), int(ctx.get("y2")), int(ctx.get("y2")))
    pos3 = (int(ctx.get("x3")), int(ctx.get("y3")), int(ctx.get("y3")))

    if pos1[0] > pos2[0] or pos1[1] > pos2[1] or pos1[2] > pos2[2]:
        server.reply(info, RText("起点坐标不能大于终点坐标", RColor.red))
        return

    # 检测回收坐标是否是空气
    rcon_result = server.rcon_query(f"execute if block {pos3[0]} {pos3[1]} {pos3[2]} minecraft:air")
    if rcon_result == "Test passed": # or rcon_result == "Test failed":
        pass

    elif rcon_result == "Test failed":
        server.reply(info, RText(f"回收位置 {pos3} 不是空气，请检查坐标是否正确。", RColor.red))
        return

    elif rcon_result == "That position is not loaded":
        server.reply(info, RText(f"回收位置 {pos3} 未加载，请先加载该区域。", RColor.red))
        return

    server.reply(info, RText(f"开始清理区域: {pos1} -> {pos2}，掉落物回收位置: {pos3}", RColor.green))
    server.reply(info, RText(f"清理任务ID: {unique_id}", RColor.yellow))

    run(pos1, pos2, pos3, unique_id)


def help():
    msg=[f"{'='*10} 使用说明 {'='*10}",
    "x1 y1 z1          起点位置坐标",
    "x2 y2 z2          手动触发创建备份",
    "x3 y3 z2          掉落物回收位置(会把掉落物收集到这个位置，一般在漏斗上方。)"
    f"{'='*10} 使用方法 {'='*10}",
    f"{CMD}                   查看使用方法",
    f"{CMD} x1 y1 z1 x2 y2 z2 x3 y3 z2",
    ]
    server.reply(info, "\n".join(msg))


# def on_user_info(server_src, player, info_src):
    # pass


def build_command():
    c = Literal(CMD).runs(lambda src: help())
    # c.then(Literal("start").runs(lambda src, ctx: main(src, ctx)))
    # c.then(Literal("backup").runs(lambda src, ctx: backup(src, ctx)))

    c.then(Integer("x1"))
    c.then(Integer("y1"))
    c.then(Integer("z1"))
    c.then(Integer("x2"))
    c.then(Integer("y2"))
    c.then(Integer("z2"))
    c.then(Integer("x3"))
    c.then(Integer("y3"))
    c.then(Integer("z3"))
    c.runs(lambda src, ctx: main(src, ctx))

    # c.then(Literal("rollback").then(Integer("number").runs(lambda src, ctx: rollback(src, ctx))))
    return c



def on_load(server_src, old_plugin):
    global server, info
    server, info = __get(server_src)

    server_src.register_help_message(CMD, RText(PLUGIN_NAME, RColor.yellow), PermissionLevel.USER)
    server_src.register_command(build_command())

    if old_plugin is not None:
        CLEARCHUNK_PROGRESS = old_plugin.CHEARCHUNK_PROGRESS
