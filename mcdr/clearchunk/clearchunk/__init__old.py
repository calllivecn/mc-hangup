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
    rematch,
    RText,
    RTextList,
    RColor,
    Literal,
    Text,
    QuotableText,
    GreedyText,
    Integer,
    Number,
    ArgumentNode,
    ParseResult,
    CommandSyntaxError,
    new_thread,
    timestamp,
    permission,
    permission_admin,
    PermissionLevel,
    PluginServerInterface,
    ServerInterface,
    Info,
    CommandSource,
)

from mcdreforged.command.builder import command_builder_utils

ID_NAME = "clearchunk"
PLUGIN_NAME = "一步步清空指定区域"

CMD = CMDPREFIX + ID_NAME

CLEARCHUNK_DIR = CONFIG_DIR / ID_NAME

CLEARCHUNK_PROGRESS = {}


# server: PluginServerInterface
server: ServerInterface
info: Info


if not CLEARCHUNK_DIR.exists():
    os.makedirs(CLEARCHUNK_DIR)

def get_progress_info():
    j = CLEARCHUNK_DIR / (ID_NAME + ".json")
    if j.exists():
        with open(j) as f:
            return json.load(f)
    else:
        return {}

def set_progress_info(data: dict):
    j = CLEARCHUNK_DIR / (ID_NAME + ".json")
    with open(j, "w+") as f:
        return json.dump(data, f, ensure_ascii=False, indent=4)

def del_progress_info():
    j = CLEARCHUNK_DIR / (ID_NAME + ".json")
    if j.exists():
        os.remove(j)


@new_thread("clearchunk")
def start(pos1, pos2, unique_id=0):

    js = get_progress_info()

    if js and "收集坐标点" in js:
        pos3 = [ js["收集坐标点"]["x"], js["收集坐标点"]["y"], js["收集坐标点"]["z"] ]
    else:
        pos3 = None

    """
    result = server.rcon_query("data get storage minecraft:clearchunk 收集坐标点")

    r_result = rematch(r"Found no elements matching (.*)", result)
    if r_result:
        # server.reply(info, RText("没有配置收集点, 不做自动收集。", RColor.red))
        pos3 = None
    
    r_result = rematch(r"Storage minecraft:clearchunk has the following contents: (.*)", result, (1,))
    if r_result:
        pos3 = json.loads(r_result[0])
    """

    
    rcon_result = server.rcon_query(f"data get entity {info.player} Dimension")
    if rcon_result is None:
        server.reply(info, RText("无法获取玩家维度信息，rcon返回None。", RColor.red))
        server.logger.error("rcon_query returned None when getting player dimension.")
        return

    r = rematch(fr'{info.player} has the following entity data: "(.*)"', rcon_result, (1,))
    if not r:
        server.reply(info, RText("无法解析玩家维度信息。", RColor.red))
        server.logger.error(f"Failed to match dimension info from rcon_result: {rcon_result}")
        return

    world = r[0]

    # 确保 pos1 是 min，pos2 是 max
    #x_min = min(pos1[0], pos2[0])
    #x_max = max(pos1[0], pos2[0])
    #y_min = min(pos1[1], pos2[1])
    #y_max = max(pos1[1], pos2[1])
    #z_min = min(pos1[2], pos2[2])
    #z_max = max(pos1[2], pos2[2])

    # 掉落物的收取区域增加3格
    r = 3

    step_r = 30

    scale_r = 16

    x1, y1, z1 = pos1


    block_cmd_suffix_list = (
        (("灵魂沙", "minecraft:soul_sand destroy"), ("岩浆块", "minecraft:magma_block destroy")),
        (("水草", "minecraft:seagrass strict"), ("水草", "minecraft:tall_seagrass strict")),
        (("海带", "minecraft:kelp_plant destroy"), ("海带头", "minecraft:kelp destroy")),
        (("水", "minecraft:water destroy"), ("岩浆", "minecraft:lava destroy")),
    )


    if world == "minecraft:overworld":
        y_up = 319 # 上边界
        y_down = -63 # 上下边界

    elif world == "minecraft:the_nether":
        block_cmd_suffix_list =("岩浆", "minecraft:lava destroy")
        y_up = 124
        y_down = 1 # 上下边界
    
    elif world == "minecraft:the_end":
        block_cmd_suffix_list = tuple()
        y_up = 255
        y_down = 0 # 上下边界
    
    else:
        server.reply(info, RText("不支持的维度。", RColor.red))
        server.logger.error(f"不支持的维度。: {world}")
        return

    y1 = min(y1, y_up)
    y1 = max(y1, y_down)

    pos2[1] = min(pos2[1], y_up)
    pos2[1] = max(pos2[1], y_down)


    for block_cmd_suffix in block_cmd_suffix_list:
        server.reply(info, RText(f"现在清理 {block_cmd_suffix[0][0]} 和 {block_cmd_suffix[1][0]} 。", RColor.green))

        # 计算预清理区域的边界
        y1_max_scale_r = pos2[1] + scale_r
        y1_max_scale_r = min(y1_max_scale_r, y_up)
        y1_min_scale_r = y1 - scale_r
        y1_min_scale_r = max(y1_min_scale_r, y_down)

        # 预清理整个区域的灵魂沙和岩浆块。清水区域，要比指定区域边界大8。
        for y in range(y1_max_scale_r, y1_min_scale_r - 1, -step_r):
            for x in range(x1 - scale_r, pos2[0] + scale_r + 1, step_r):
                for z in range(z1 - scale_r, pos2[2] + scale_r + 1, step_r):

                    y2 = max(y - step_r, y1_min_scale_r)
                    x2 = min(x + step_r, pos2[0] + scale_r)
                    z2 = min(z + step_r, pos2[2] + scale_r)

                    result = server.rcon_query(f"execute in {world} run fill {x} {y2} {z} {x2} {y} {z2} minecraft:air replace {block_cmd_suffix[0][1]}")

                    # msg = []
                    # msg.append(RText(f"现在清理坐标范围: {x} {y2} {z} {x2} {y} {z2} ", RColor.yellow))
                    # msg.append(RText(result, RColor.yellow))
                    # server.reply(info, RTextList(*msg))

                    if result is None:
                        err = f"清理区域 {block_cmd_suffix[0][0]} 时发生异常退出。"
                        server.reply(info, RText(err, RColor.red))
                        server.logger.error(err)
                        return

                    result = server.rcon_query(f"execute in {world} run fill {x} {y2} {z} {x2} {y} {z2} minecraft:air replace {block_cmd_suffix[1][1]}")
                    if result is None:
                        err = f"清理区域 {block_cmd_suffix[1][0]} 时发生异常退出。"
                        server.reply(info, RText(err, RColor.red))
                        server.logger.error(err)
                        return

                if pos3 is not None:
                    server.rcon_query(f"execute in {world} as @e[type=item,x={x1-r-8},y={y1-r-scale_r},z={z1-r-scale_r},dx={pos2[0]-x1+r+scale_r},dy={pos2[1]-y1+r+scale_r},dz={pos2[2]-z1+r+scale_r}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")


    # 正式清理整个区域的方块。 这里步长不能30太大。
    step_r = 8
    for y in range(pos2[1], y1 - 1, -step_r):
        for x in range(x1, pos2[0] + 1, step_r):
            for z in range(z1, pos2[2] + 1, step_r):

                y2 = max(y - step_r, y1)
                x2 = min(x + step_r, pos2[0])
                z2 = min(z + step_r, pos2[2])

                if pos3 is None:
                    result = server.rcon_query(f"execute in {world} run fill {x} {y2} {z} {x2} {y} {z2} minecraft:air replace")
                else:
                    result = server.rcon_query(f"execute in {world} run fill {x} {y2} {z} {x2} {y} {z2} minecraft:air destroy")

                if result is None:
                    server.reply(info, RText("清理区域 方块 时发生异常退出。", RColor.red))
                    server.logger.error("清理区域 方块 时发生异常")
                    return

                if pos3 is not None:
                    time.sleep(0.2)
                    server.rcon_query(f"execute in {world} as @e[type=item,x={x1-r},y={y1-r},z={z1-r},dx={pos2[0]-x1+r},dy={pos2[1]-y1+r},dz={pos2[2]-z1+r}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")
                    server.rcon_query(f"execute in {world} as @e[type=minecraft:experience_orb,x={x1-r},y={y1-r},z={z1-r},dx={pos2[0]-x1+r},dy={pos2[1]-y1+r},dz={pos2[2]-z1+r}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")

    server.reply(info, RText("清理区域完成执行完成", RColor.green))


@permission
def main(src, ctx):
    global server, info
    server, info = __get(src)

    unique_id = time.monotonic_ns()

    args = ctx["args"].split()
    # print(f"{args=}")

    pos1 = [ int(float(i)) for i in args[0].split(",") ]
    pos2 = [ int(float(i)) for i in args[1].split(",") ]

    if len(args) < 3:
        pos3 = None
    else:
        pos3 = list(map(int, args[2].split(",")))

    if pos1[0] > pos2[0] or pos1[1] > pos2[1] or pos1[2] > pos2[2]:
        server.reply(info, RText("起点坐标不能大于终点坐标", RColor.red))
        return

    msg = []
    msg.append(RText(f"开始清理区域: {pos1} -> {pos2}，掉落物回收位置: {pos3}", RColor.green))
    msg.append("\n")
    msg.append(RText(f"清理任务ID: {unique_id}", RColor.yellow))

    server.reply(info, RTextList(*msg))

    start(pos1, pos2)


@permission
def center(src: CommandSource, ctx: dict):
    global server, info
    server, info = __get(src)

    # print(f"{ctx=}")
    # x, z 正方形半径
    R = int(ctx["R"])
    y_up = int(ctx["y_up"]) # 上边界
    y_down = int(ctx["y_down"]) # 下边界


    # 玩家当前坐标
    rcon_result = server.rcon_query(f"data get entity {info.player} Pos")
    # calllivecn has the following entity data: [399.0120798914333d, 97.55602869034644d, 214.32347470479664d]
    cmd = fr"{info.player} has the following entity data: \[(-?[0-9\.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]"
    x, y, z = rematch(cmd, rcon_result, (1, 2, 3))

    x1, y1, z1 = int(float(x)) - R, y_down, int(float(z)) - R
    x2, y2, z2 = int(float(x)) + R, y_up, int(float(z)) + R

    start([x1, y1, z1], [x2, y2, z2])


@permission
def collection_point(src: CommandSource, ctx: dict):
    """
    配置参数：x1,y1,z1 做为收集掉落物的位置 
    """
    global server, info
    server, info = __get(src)

    # print(f"{ctx=}")

    if ctx is None:
        # 配置当前玩家位置为收集点
        rcon_result = server.rcon_query(f"data get entity {info.player} Pos")
        cmd = fr"{info.player} has the following entity data: \[(-?[0-9\.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]"
        x, y, z = rematch(cmd, rcon_result, (1, 2, 3))
        x, y, z = int(float(x)), int(float(y)), int(float(z))

    
    else:
        # x, y, z = int(float(args[1])), int(float(args[2])), int(float(args[3]))
        x, y, z = int(float(ctx["x"])), int(float(ctx["y"])), int(float(ctx["z"]))
    

    config = {
        "x": x,
        "y": y,
        "z": z,
    }


    # 检测回收坐标是否是空气
    rcon_result = server.rcon_query(f"execute if block {x} {y} {z} minecraft:air")
    # print(f"{rcon_result=} {config=} {json.dumps(config)=}")

    if rcon_result == "Test passed": # or rcon_result == "Test failed":
        # server.rcon_query(f"data modify storage minecraft:clearchunk 收集坐标点 set value {json.dumps(config)}")

        set_progress_info({"收集坐标点": config})

        server.reply(info, RText(f"配置回收坐标点：[{x}, {y}, {z}] ", RColor.green))

    elif rcon_result == "Test failed":
        server.reply(info, RText(f"回收位置 [{x}, {y}, {z}] 不是空气，请检查坐标是否正确。", RColor.red))

    elif rcon_result == "That position is not loaded":
        server.reply(info, RText(f"回收位置 [{x}, {y}, {z}] 未加载，请先加载该区域。", RColor.red))

    else:
        server.reply(info, RText(f"无法检测回收位置 [{x}, {y}, {z}] 是否为空气，rcon命令返回: {rcon_result}", RColor.red))


@permission
def collection_point_get(src: CommandSource, ctx: dict):
    global server, info
    server, info = __get(src)

    js = get_progress_info()

    if js and "收集坐标点" in js:
        pos3 = js["收集坐标点"]
        server.reply(info, RText(f"当前回收坐标点：[{pos3['x']}, {pos3['y']}, {pos3['z']}] ", RColor.green))
    else:
        server.reply(info, RText("未配置回收坐标点。", RColor.red))

@permission
def collection_point_clear(src: CommandSource):
    global server, info
    server, info = __get(src)

    # server.rcon_query("data remove storage minecraft:clearchunk 收集坐标点")
    del_progress_info()
    server.reply(info, RText("移除收集点", RColor.green))



def help(src: CommandSource):
    global server, info
    server, info = __get(src)

    msg=[
        f"{'='*10} 使用方法 {'='*10}",
        f"{CMD} center R y_up y_down    以玩家当前位置为中心，清理半径R的正方形区域，y_up为上边界，y_down为下边界",
        f"{'='*10} 使用方法 {'='*10}",
        f"{CMD} setcfg x y z    配置掉落物回收位置(会把掉落物收集到这个位置，一般在漏斗上方。)",
        f"{CMD} getcfg    查看掉落物回收位置",
        f"{CMD} delcfg    删除掉落物回收位置(不产生掉落物+不收集掉落物)",
        f"{'='*10} 使用方法 {'='*10}",
        f"{CMD}    查看使用方法",
        f"{CMD} pos x1,y1,z1 x2,y2,z2 x3,y3,z3",
        f"{'='*10} 使用说明 {'='*10}",
        "x1,y1,z1    起点位置坐标",
        "x2,y2,z2    结束位置坐标",
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
    # c = Literal(CMD).then(PointArgument("pos").runs(main))

    c = Literal(CMD).runs(help)
    c.then(
        Literal("setcfg").runs(lambda src: collection_point(src, None))
        .then(
            Number("x").then(
                Number("y").then(
                    Number("z").runs(lambda src, ctx: collection_point(src, ctx))
                )
            )
        )
    )
    c.then(
        Literal("getcfg").runs(lambda src, ctx: collection_point_get(src, ctx))
    )
    c.then(
        Literal("delcfg").runs(lambda src: collection_point_clear(src))
    )

    c.then(
        Literal("center")
        .then(
            Number("R")
            .then(
                Number("y_up")
                .then(
                    Number("y_down").runs(lambda src, ctx: center(src, ctx)))
            )
        )
    )
    c.then(
        Literal("pos").then(
            GreedyText("args").runs(lambda src, ctx: main(src, ctx))
        )
    )
    return c


def on_load(server: PluginServerInterface, old_plugin):
    server.register_help_message(CMD, RText(PLUGIN_NAME, RColor.yellow), PermissionLevel.USER)
    server.register_command(build_command())

    global CLEARCHUNK_PROGRESS
    if old_plugin is not None:
        CLEARCHUNK_PROGRESS = old_plugin.CLEARCHUNK_PROGRESS


def on_unload(server: PluginServerInterface):
    # server_src.unregister_help_message(CMD)
    server.logger.info(RText(f"{PLUGIN_NAME} 插件卸载成功", RColor.green))
