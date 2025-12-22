#!/usr/bin/env python3
# coding=utf-8
# date 2025-06-28 21:25:17
# author calllivecn <calllivecn@outlook.com>

import os
import time
import json
from math import floor


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


def inclusive_range(start, stop, step):
    if step == 0:
        raise ValueError("step must not be zero")
    
    current = start
    if step > 0:
        while current < stop:
            yield current
            current += step
        if current != stop:
            yield stop
    else:  # step < 0
        while current > stop:
            yield current
            current += step  # step 是负数，所以实际是减
        if current != stop:
            yield stop


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

    block_cmd_suffix_list = (
        (("灵魂沙", "minecraft:soul_sand destroy"), ("岩浆块", "minecraft:magma_block destroy")),
        (("水草", "minecraft:seagrass strict"), ("水草", "minecraft:tall_seagrass strict")),
        (("海带", "minecraft:kelp_plant destroy"), ("海带头", "minecraft:kelp destroy")),
        (("水", "minecraft:water destroy"), ("岩浆", "minecraft:lava destroy")),
    )

    x1, y1, z1 = pos1
    x2, y2, z2 = pos2

    x6, y6, z6 = x1-1, y1-1, z1-1
    x7, y7, z7 = x2+1, y2+1, z2+1

    # 外扩后的边界
    # 定义六个面（每个面是一个 (x1,y1,z1, x2,y2,z2) 元组）
    # faces = [
    #     # Y+
    #     (x6, y7+1, z6, x7, y7+1, z7),
    #     # Y-
    #     (x6, y6-1, z6, x7, y6-1, z7),
    #     # X+
    #     (x7+1, y6, z6, x7+1, y7, z7),
    #     # X-
    #     (x6-1, y6, z6, x6-1, y7, z7),
    #     # Z+
    #     (x6, y6, z7+1, x7, y7, z7+1),
    #     # Z-
    #     (x6, y6, z6-1, x7, y7, z6-1),
    # ]

    faces = [
        # Y+
        (x6, y7, z6, x7, y7, z7),
        # Y-
        (x6, y6, z6, x7, y6, z7),
        # X+
        (x7, y6, z6, x7, y7, z7),
        # X-
        (x6, y6, z6, x6, y7, z7),
        # Z+
        (x6, y6, z7, x7, y7, z7),
        # Z-
        (x6, y6, z6, x7, y7, z6),
    ]

    print(f"{pos1=} {pos2=}")
    for f in faces:
        print(f"{f}")


    if world == "minecraft:overworld":
        y_world_up = 319 # 上边界
        y_world_down = -63 # 上下边界

    elif world == "minecraft:the_nether":
        block_cmd_suffix_list =("岩浆", "minecraft:lava destroy")
        y_world_up = 124
        y_world_down = 1 # 上下边界
    
    elif world == "minecraft:the_end":
        block_cmd_suffix_list = tuple()
        y_world_up = 255
        y_world_down = 0 # 上下边界
    
    else:
        server.reply(info, RText("不支持的维度。", RColor.red))
        server.logger.error(f"不支持的维度。: {world}")
        return


    # 掉落物的收取区域增加3格
    r = 3
    step_r = 8

    # for block_cmd_suffix in block_cmd_suffix_list:
        # server.reply(info, RText(f"现在清理 {block_cmd_suffix[0][0]} 和 {block_cmd_suffix[1][0]} 。", RColor.green))
    
    # for x1f, y1f, z1f, x2f, y2f, z2f in faces:
    #     y1f = min(y1f, y_world_up)
    #     y1f = max(y1f, y_world_down)

    #     y2f = min(y2f, y_world_up)
    #     y2f = max(y2f, y_world_down)

        # # 测试用，填充玻璃
        # result = server.rcon_query(f"execute in {world} run fill {x1f} {y1f} {z1f} {x2f} {y2f} {z2f} minecraft:glass")
        # server.reply(info, RText(f"现在清理 面 坐标范围: [{x1f},{y1f},{z1f}] [{x2f},{y2f},{z2f}] ", RColor.yellow))
        # server.reply(info, RText(result, RColor.yellow))
        # time.sleep(3)
        # continue

    x1f, y1f, z1f = x6, max(y6, y_world_down), z6
    x2f, y2f, z2f = x7, min(y7, y_world_up), z7
    # 预清理整个区域的水和岩浆。清水区域，要比指定区域边界大8。
    for y in inclusive_range(y2f, y1f, -step_r):
        if y - step_r > y1f:
            y2_t = y - step_r
        else:
            y2_t = y1f
                
        for z in inclusive_range(z1f, z2f, step_r):
            if z + step_r < z2f:
                z2_t = z + step_r
            else:
                z2_t = z2f

            for x in inclusive_range(x1f, x2f, step_r):
                if x + step_r < x2f:
                    x2_t = x + step_r
                else:
                    x2_t = x2f
                
                server.reply(info, RText("有执行吗？", RColor.yellow))

                result = server.rcon_query(f"execute in {world} run fill {x} {y2_t} {z} {x2_t} {y} {z2_t} minecraft:glass replace minecraft:lava")
                if result is None:
                    err = "清理区域 岩浆 时发生异常退出。"
                    server.reply(info, RText(err, RColor.red))
                    server.logger.error(err)
                    return
                msg = []
                msg.append(RText(f"现在清理 岩浆 坐标范围: [{x},{y2_t},{z}] [{x2_t},{y},{z2_t}] ", RColor.yellow))
                msg.append(RText(result, RColor.yellow))
                server.reply(info, RTextList(*msg))


                result = server.rcon_query(f"execute in {world} run fill {x} {y2_t} {z} {x2_t} {y} {z2_t} minecraft:glass replace minecraft:water")
                if result is None:
                    err = "清理区域 水 时发生异常退出。"
                    server.reply(info, RText(err, RColor.red))
                    server.logger.error(err)
                    return
                msg = []
                msg.append(RText(f"现在清理 水 坐标范围: [{x},{y2_t},{z}] [{x2_t},{y},{z2_t}] ", RColor.yellow))
                msg.append(RText(result, RColor.yellow))
                server.reply(info, RTextList(*msg))
                
                # time.sleep(1)

                if x2_t == x2f:
                    break
            if z2_t == z2f:
                break
        if y2_t == y1f:
            break


    y1_down = max(y1, y_world_down)
    y2_up = min(y2, y_world_up)
    # 正式清理整个区域的方块。 这里步长不能30太大。
    step_r = 8
    for y in inclusive_range(y2_up, y1_down, -step_r):
        if y - step_r > y1_down:
            y2_t = y - step_r
        else:
            y2_t = y1_down
                
        for z in inclusive_range(z1, z2, step_r):
            if z + step_r < z2:
                z2_t = z + step_r
            else:
                z2_t = z2
            
            if pos3 is None:
                xr = (x2 - x1) // 2
                yr = (y2 - y1) // 2
                zr = (z2 - z1) // 2
                # 不收集的情况下，清理其他item
                result = server.rcon_query(f"execute in {world} run kill @e[type=item,x={x1+xr},y={y1+yr},z={z1+zr},dx={xr},dy={yr},dz={zr}]")
                if result:
                    server.reply(info, RText(f"清理物品: {result}", RColor.green))

            for x in inclusive_range(x1, x2, step_r):

                if x + step_r < x2:
                    x2_t = x + step_r
                else:
                    x2_t = x2
                
                if pos3 is None:
                    result = server.rcon_query(f"execute in {world} run fill {x} {y2_t} {z} {x2_t} {y} {z2_t} minecraft:air replace")
                else:
                    result = server.rcon_query(f"execute in {world} run fill {x} {y2_t} {z} {x2_t} {y} {z2_t} minecraft:air destroy")

                if result is None:
                    server.reply(info, RText("清理区域 方块 时发生异常退出。", RColor.red))
                    server.logger.error("清理区域 方块 时发生异常")
                    return

                msg = []
                msg.append(RText(f"现在清理 方块 坐标范围: [{x},{y2_t},{z}] [{x2_t},{y},{z2_t}] ", RColor.yellow))
                msg.append(RText(result, RColor.yellow))
                server.reply(info, RTextList(*msg))


                if pos3 is not None:
                    time.sleep(0.2)
                    server.rcon_query(f"execute in {world} as @e[type=item,x={x1-r},y={y1-r},z={z1-r},dx={pos2[0]-x1+r},dy={pos2[1]-y1+r},dz={pos2[2]-z1+r}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")
                    server.rcon_query(f"execute in {world} as @e[type=minecraft:experience_orb,x={x1-r},y={y1-r},z={z1-r},dx={pos2[0]-x1+r},dy={pos2[1]-y1+r},dz={pos2[2]-z1+r}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")
                
                # time.sleep(1)

                if x2_t == x2:
                    break
            if z2_t == z2:
                break
        if y2_t == y1_down:
            break

    server.reply(info, RText("清理区域完成执行完成", RColor.green))


@permission
def main(src, ctx):
    global server, info
    server, info = __get(src)

    unique_id = time.monotonic_ns()

    args = ctx["args"].split()
    # print(f"{args=}")

    pos1 = [ floor(float(i)) for i in args[0].split(",") ]
    pos2 = [ floor(float(i)) for i in args[1].split(",") ]

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

    x1, y1, z1 = floor(float(x)) - R, y_down, floor(float(z)) - R
    x2, y2, z2 = floor(float(x)) + R, y_up, floor(float(z)) + R

    start([x1, y_down, z1], [x2, y_up, z2])


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
        x, y, z = floor(float(x)), floor(float(y)), floor(float(z))

    
    else:
        x, y, z = floor(float(ctx["x"])), floor(float(ctx["y"])), floor(float(ctx["z"]))
    

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
