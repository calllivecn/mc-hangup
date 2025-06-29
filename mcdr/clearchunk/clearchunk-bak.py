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
    ArgumentNode,
    ParseResult,
    CommandSyntaxError,
    new_thread,
    timestamp,
    permission,
    PermissionLevel,
    PluginServerInterface,
    Info,
)

from mcdreforged.command.builder import command_builder_utils

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
    fluid_name = "水源" if fluid == "water" else "熔岩源"

    water_found = set()  # 用集合来存储找到的水源方块
    water_found.add((x0, y0, z0))

    water_found_next = set()  # 用来存储下一个循环中找到的水源方块

    water_count = 0  # 计数器，记录找到的水源方块数量


    while len(water_found) > 0:

        # 取出一个水源方块
        for x1, y1, z1 in water_found:

            # 把相连的水流方块添加进去
            for x, y, z in connected_blocks(x1, y1, z1):
                # 是水源。不区分会更好。
                # rcon_result = server.rcon_query(f"execute if block {x} {y} {z} minecraft:{fluid}[level=0]")
                rcon_result = server.rcon_query(f"execute if block {x} {y} {z} minecraft:{fluid}")
                if rcon_result == "Test passed":
                    water_found_next.add((x, y, z))
            
        water_count += len(water_found)
        for x, y, z in water_found:
            server.rcon_query(f"setblock {x} {y} {z} minecraft:air strict")
        

        server.reply(info, RText(f"本次小轮清理 {fluid_name}: {len(water_found)} 个", RColor.green))

        # 把上一轮已经检测过的去掉
        for pos in water_found:
            water_found_next.discard(pos)
        
        # 清理完当前找到的水源方块后，更新 water_found
        water_found = water_found_next
        water_found_next = set()  # 清空下一个循环的集合

    server.reply(info, RText(f"本次大轮总共清理 {fluid_name}: {water_count} 个", RColor.green))


def check_destroy_block(x, y, z) -> bool:
    # 检测是不是空气。
    rcon_result = server.rcon_query(f"execute if block {x} {y} {z} minecraft:air")
    if rcon_result == "Test passed": # or rcon_result == "Test failed":
        # server.tell(info.player, RText(f"位置 {x} {y} {z} 已经是空气了。", RColor.red))
        return True

    elif rcon_result == "That position is not loaded":
        server.reply(info, RText(f"位置 {x} {y} {z} 未加载，请先加载该区域。", RColor.red))
        return True

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

    # 掉落物的收取区域增加3格
    r = 3

    x1, y1, z1 = pos1

    item_count = 0  # 掉落物计数器

    # 从上向下清理？
    for y in range(pos2[1], y1-1, -1):
        for x in range(x1, pos2[0] + 1):
            for z in range(z1, pos2[2] + 1):
                try:
                    check_destroy_block(x, y, z)
                    item_count += 1
                except Exception as e:
                    server.reply(info, RText("异常退出。", RColor.red))
                    server.logger.error(f"清理区域时发生异常: {e}")
                    return

                if item_count % 20 == 0:
                    # 每清理10格就回收一次掉落物
                    time.sleep(1)
                    server.rcon_query(f"execute as @e[type=item,x={x1-r},y={y1-r},z={z1-r},dx={pos2[0]-x1+r},dy={pos2[1]-y1+r},dz={pos2[2]-z1+r}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")


    time.sleep(1)
    server.rcon_query(f"execute as @e[type=item,x={x1-r},y={y1-r},z={z1-r},dx={pos2[0]-x1+r},dy={pos2[1]-y1+r},dz={pos2[2]-z1+r}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")
    server.reply(info, RText("清理区域完成执行完成", RColor.green))


# @permission
def main(src, ctx):
    global server, info
    server, info = __get(src)

    # 检测权限
    perm = server.get_permission_level(info)
    if perm < PermissionLevel.USER:
        server.reply(info, RText(f"你没有权限执行此命令. 当前权限：{perm=}", RColor.red))
        return


    server.say(RText("开始清理区域...", RColor.green))

    unique_id = time.monotonic_ns()

    args = ctx["pos"]
    # print(f"{args=}")

    pos1 = tuple(map(int, args[0].split(",")))
    pos2 = tuple(map(int, args[1].split(",")))
    pos3 = tuple(map(int, args[2].split(",")))

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


def help(src):
    global server, info
    server, info = __get(src)

    msg=[f"{'='*10} 使用说明 {'='*10}",
    "x1,y1,z1          起点位置坐标",
    "x2,y2,z2          手动触发创建备份",
    "x3,y3,z3          掉落物回收位置(会把掉落物收集到这个位置，一般在漏斗上方。)",
    f"{'='*10} 使用方法 {'='*10}",
    f"{CMD}                   查看使用方法",
    f"{CMD} x1,y1,z1 x2,y2,z2 x3,y3,z3",
    ]
    server.reply(info, "\n".join(msg))


# def on_user_info(server_src, player, info_src):
    # pass

class Invaild(CommandSyntaxError):
    def __init__(self, char_read: int):
        super().__init__("无效参数", char_read)

class Incomplete(CommandSyntaxError):
    def __init__(self, char_read: int):
        super().__init__('不完整', char_read)

class PointArgument(ArgumentNode):
    def parse(self, text: str) -> ParseResult:
        total_read = 0
        coords = []
        for i in range(6):
            total_read += len(text[total_read:]) - len(command_builder_utils.remove_divider_prefix(text[total_read:]))
            value, read = command_builder_utils.get_float(text[total_read:])
            if read == 0:
                raise Invaild(total_read)

            total_read += read

            if value is None:
                raise Incomplete(total_read)

            coords.append(value)
        return ParseResult(coords, total_read)


class PosArgument(ArgumentNode):
    def parse(self, text: str) -> ParseResult:
        total_read = 0
        coords = []
        print(f"{text=}")
        for i in range(3):
            total_read += len(text[total_read:]) - len(command_builder_utils.remove_divider_prefix(text[total_read:]))

            arg = command_builder_utils.get_element(text[total_read:])
            try:
                value = str(arg)
            except ValueError:
                value = None

            value, read = value, len(arg)

            if read == 0:
                raise Invaild(total_read)

            total_read += read
            if value is None:
                raise Incomplete(total_read)

            coords.append(value)
        return ParseResult(coords, total_read)


def build_command():
    # c = Literal(CMD).runs(help)
    # c.then(Literal("start").runs(lambda src, ctx: main(src, ctx)))
    # c.then(Literal("backup").runs(lambda src, ctx: backup(src, ctx)))

    """
    c = c.then(Integer("x1"), 
                Integer("y1"), 
                Integer("z1"), 
                Integer("x2"), 
                Integer("y2"), 
                Integer("z2"), 
                Integer("x3"), 
                Integer("y3"), 
                Integer("z3").runs(lambda src, ctx: main(src, ctx)))
    """
    """
    c.then(Integer("x1")
    .then(Integer("y1"))
    .then(Integer("z1"))
    .then(Integer("x2"))
    .then(Integer("y2"))
    .then(Integer("z2"))
    .then(Integer("x3"))
    .then(Integer("y3"))
    .then(Integer("z3"))
    .runs(lambda src, ctx: main(src, ctx)))
    """

    """
    c.then(Integer("x1"))
    c.then(Integer("y1"))
    c.then(Integer("z1"))
    c.then(Integer("x2"))
    c.then(Integer("y2"))
    c.then(Integer("z2"))
    c.then(Integer("x3"))
    c.then(Integer("y3"))
    c.then(Integer("z3"))
    c.runs(main)
    """
    
    # c = Literal(CMD).then(PointArgument("pos").runs(main))
    c = Literal(CMD).then(PosArgument("pos").runs(main))
    return c


def on_load(server_src, old_plugin):

    server_src.register_help_message(CMD, RText(PLUGIN_NAME, RColor.yellow), PermissionLevel.USER)
    server_src.register_command(build_command())

    server_src.say(RText(f"{PLUGIN_NAME} 插件加载成功", RColor.green))

    if old_plugin is not None:
        CLEARCHUNK_PROGRESS = old_plugin.CLEARCHUNK_PROGRESS
