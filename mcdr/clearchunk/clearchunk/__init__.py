#!/usr/bin/env python3
# coding=utf-8
# date 2025-06-28 21:25:17
# author calllivecn <calllivecn@outlook.com>

import re
import os
import time
import json


from clearchunk.funcs import (
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


@new_thread("clerchunk")
def run(pos1, pos2, pos3, unique_id):

    rcon_result = server.rcon_query(f"data get entity {info.player} Dimension")
    if rcon_result is None:
        server.reply(info, RText("无法获取玩家维度信息，rcon返回None。", RColor.red))
        server.logger.error("rcon_query returned None when getting player dimension.")
        return

    match = re.match(fr'{info.player} has the following entity data: "(.*)"', rcon_result)
    if not match:
        server.reply(info, RText("无法解析玩家维度信息。", RColor.red))
        server.logger.error(f"Failed to match dimension info from rcon_result: {rcon_result}")
        return

    world = match.group(1)

    # 掉落物的收取区域增加3格
    r = 3

    step_r = 30

    scale_r = 16

    x1, y1, z1 = pos1


    block_cmd_suffix_list = (
        (("灵魂沙", "minecraft:soul_sand destroy"), ("岩浆块", "minecraft:magma_block destroy")),
        (("水草", "minecraft:seagrass strict"), ("水草", "minecraft:tall_seagrass strict")),
        (("海带", "minecraft:kelp_plant destroy"), ("海带", "minecraft:kelp destroy")),
        (("水", "minecraft:water destroy"), ("岩浆", "minecraft:lava destroy")),
    )

    y_up = 319 # 上边界
    y_down = -63 # 上下边界

    if world == "minecraft:overworld":
        pass

    elif world == "minecraft:the_nether":
        block_cmd_suffix_list =("岩浆", "minecraft:lava destroy")
        y_up = 124
        y_down = 1 # 上下边界
    
    elif world == "minecraft:the_end":
        block_cmd_suffix_list = tuple()
        y_up = 255
        y_down = 0 # 上下边界

    y1 = y1 if y1 < y_down else y_down
    y1 = y1 if y1 > y_up else y_up

    pos2[1] = pos2[1] if pos2[1] < y_down else y_down
    pos2[1] = pos2[1] if pos2[1] > y_up else y_up


    for block_cmd_suffix in block_cmd_suffix_list:
        server.reply(info, RText(f"现在清理 {block_cmd_suffix[0][0]} 和 {block_cmd_suffix[1][0]} 。", RColor.green))

        # 预清理整个区域的灵魂沙和岩浆块。 清水区域，要比指定区域边界大8.
        for y in range(pos2[1]+scale_r, y1-scale_r-1, -step_r):
            for x in range(x1-scale_r, pos2[0]+scale_r+1, step_r):
                for z in range(z1-scale_r, pos2[2]+scale_r+1, step_r):

                    y2 = (y - step_r) if y - step_r > y1 - scale_r else y1 - scale_r
                    x2 = (x + step_r) if x + step_r < pos2[0] + scale_r else pos2[0] + scale_r
                    z2 = (z + step_r) if z + step_r < pos2[2] + scale_r else pos2[2] + scale_r


                    server.reply(info, RText(f"现在清理坐标范围: {x} {y2} {z} {x2} {y} {z2}", RColor.yellow))

                    result = server.rcon_query(f"execute in {world} run fill {x} {y2} {z} {x2} {y} {z2} minecraft:air replace {block_cmd_suffix[0][1]}")
                    if result is None:
                        err = f"清理区域 {block_cmd_suffix[0][0]} 时发生异常退出。"
                        server.reply(info, RText(err, RColor.red))
                        server.logger.error(err)
                        return

                    result = server.rcon_query(f"fill {x} {y2} {z} {x2} {y} {z2} minecraft:air replace {block_cmd_suffix[1][1]}")
                    if result is None:
                        err = f"清理区域 {block_cmd_suffix[1][0]} 时发生异常退出。"
                        server.reply(info, RText(err, RColor.red))
                        server.logger.error(err)
                        return

                server.rcon_query(f"execute as @e[type=item,x={x1-r-8},y={y1-r-scale_r},z={z1-r-scale_r},dx={pos2[0]-x1+r+scale_r},dy={pos2[1]-y1+r+scale_r},dz={pos2[2]-z1+r+scale_r}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")


    # 正式清理整个区域的方块。 这里步长不能30，只能10。
    step_r = 10
    for y in range(pos2[1], y1-1, -step_r):
        for x in range(x1, pos2[0]+1, step_r):
            for z in range(z1, pos2[2]+1, step_r):

                y2 = y - step_r if y - step_r > y1 else y1
                x2 = x + step_r if x + step_r < pos2[0] else pos2[0]
                z2 = z + step_r if z + step_r < pos2[2] else pos2[2]

                result = server.rcon_query(f"fill {x} {y2} {z} {x2} {y} {z2} minecraft:air destroy")
                if result is None:
                    server.reply(info, RText("清理区域 方块 时发生异常退出。", RColor.red))
                    server.logger.error("清理区域 方块 时发生异常")
                    return

                time.sleep(0.3)
                server.rcon_query(f"execute as @e[type=item,x={x1-r},y={y1-r},z={z1-r},dx={pos2[0]-x1+r},dy={pos2[1]-y1+r},dz={pos2[2]-z1+r}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")
                server.rcon_query(f"execute as @e[type=minecraft:experience_orb,x={x1-r},y={y1-r},z={z1-r},dx={pos2[0]-x1+r},dy={pos2[1]-y1+r},dz={pos2[2]-z1+r}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")

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
