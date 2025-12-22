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
    player_dimension,
    player_pos,
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

EXIT = False

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


class Sleep:
    def __init__(self):

        js = get_progress_info()
        self.sleep_time = js.get("sleep_time")

    def sleep_if_needed(self):
        if self.sleep_time is not None:
            time.sleep(self.sleep_time)


@new_thread("clearchunk")
def start(pos1, pos2, unique_id=0):

    msg = []
    msg.append(RText(f"开始清理区域: {pos1} -> {pos2}", RColor.green))
    msg.append("\n")
    msg.append(RText(f"清理任务ID: {unique_id}", RColor.yellow))
    server.reply(info, RTextList(*msg))

    st = Sleep()

    js = get_progress_info()

    if js and "收集坐标点" in js:
        pos3 = [ js["收集坐标点"]["x"], js["收集坐标点"]["y"], js["收集坐标点"]["z"] ]
    else:
        pos3 = None

    world = js.get("world")
    if world is None:
        world = player_dimension(server, info)

    block_cmd_suffix_list = (
        (("灵魂沙", "minecraft:soul_sand destroy"), ("岩浆块", "minecraft:magma_block destroy")),
        (("水草", "minecraft:seagrass strict"), ("水草", "minecraft:tall_seagrass strict")),
        (("海带", "minecraft:kelp_plant destroy"), ("海带头", "minecraft:kelp destroy")),
        (("水", "minecraft:water destroy"), ("岩浆", "minecraft:lava destroy")),
    )

    x1, y1, z1 = pos1
    x2, y2, z2 = pos2

    # 外扩后的边界
    x6, y6, z6 = x1-1, y1-1, z1-1
    x7, y7, z7 = x2+1, y2+1, z2+1


    if world == "minecraft:overworld":
        y_world_up = 319 # 上边界
        y_world_down = -63 # 上下边界

    elif world == "minecraft:the_nether":
        y_world_up = 126
        y_world_down = 1 # 上下边界
    
    elif world == "minecraft:the_end":
        y_world_up = 255
        y_world_down = 0 # 上下边界
    
    else:
        server.reply(info, RText("不支持的维度。", RColor.red))
        server.logger.error(f"不支持的维度。: {world}")
        return


    step_r = 8

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

                if EXIT:
                    server.reply(info, RText("清理任务被中止。", RColor.red))
                    return

                if x + step_r < x2f:
                    x2_t = x + step_r
                else:
                    x2_t = x2f
                
                result = server.rcon_query(f"execute in {world} run fill {x} {y2_t} {z} {x2_t} {y} {z2_t} minecraft:glass replace minecraft:lava")
                if result is None:
                    err = "清理区域 岩浆 时发生异常退出。"
                    server.reply(info, RText(err, RColor.red))
                    server.logger.error(err)
                    return
                # msg = []
                # msg.append(RText(f"现在清理 岩浆 坐标范围: [{x},{y2_t},{z}] [{x2_t},{y},{z2_t}] ", RColor.yellow))
                # msg.append(RText(result, RColor.yellow))
                # server.reply(info, RTextList(*msg))


                result = server.rcon_query(f"execute in {world} run fill {x} {y2_t} {z} {x2_t} {y} {z2_t} minecraft:glass replace minecraft:water")
                if result is None:
                    err = "清理区域 水 时发生异常退出。"
                    server.reply(info, RText(err, RColor.red))
                    server.logger.error(err)
                    return
                # msg = []
                # msg.append(RText(f"现在清理 水 坐标范围: [{x},{y2_t},{z}] [{x2_t},{y},{z2_t}] ", RColor.yellow))
                # msg.append(RText(result, RColor.yellow))
                # server.reply(info, RTextList(*msg))
                
                st.sleep_if_needed()

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
            
            xr = (x2 - x1)
            yr = (y2 - y1)
            zr = (z2 - z1)

            if pos3 is None:
                # 不收集的情况下，清理其他item
                result = server.rcon_query(f"execute in {world} run kill @e[type=item,x={x1},y={y1},z={z1},dx={xr},dy={yr},dz={zr}]")
                # if result:
                    # server.reply(info, RText(f"清理物品: {result}", RColor.green))

            for x in inclusive_range(x1, x2, step_r):

                if EXIT:
                    server.reply(info, RText("清理任务被中止。", RColor.red))
                    return

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

                # msg = []
                # msg.append(RText(f"现在清理 方块 坐标范围: [{x},{y2_t},{z}] [{x2_t},{y},{z2_t}] ", RColor.yellow))
                # msg.append(RText(result, RColor.yellow))
                # server.reply(info, RTextList(*msg))


                if pos3 is not None:
                    # time.sleep(0.2)
                    st.sleep_if_needed()
                    server.rcon_query(f"execute in {world} as @e[type=item,x={x1},y={y1},z={z1},dx={xr},dy={yr},dz={zr}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")
                    server.rcon_query(f"execute in {world} as @e[type=minecraft:experience_orb,x={x1},y={y1},z={z1},dx={xr},dy={yr},dz={zr}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")
                
                st.sleep_if_needed()

                if x2_t == x2:
                    break
            if z2_t == z2:
                break
        if y2_t == y1_down:
            break

    server.reply(info, RText("清理区域完成执行完成", RColor.green))


@permission
def pos(src, ctx):
    global server, info
    server, info = __get(src)

    unique_id = time.monotonic_ns()

    args = ctx["args"].split()
    # print(f"{args=}")

    pos1 = [ floor(float(i)) for i in args[0].split(",") ]
    pos2 = [ floor(float(i)) for i in args[1].split(",") ]

    if pos1[0] > pos2[0] or pos1[1] > pos2[1] or pos1[2] > pos2[2]:
        server.reply(info, RText("起点坐标不能大于终点坐标", RColor.red))
        return
    
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
    x, y, z = player_pos(server, info)

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

    # 获取玩家所在维度
    world = player_dimension(server, info)

    if ctx is None:
        # 配置当前玩家位置为收集点
        x, y, z = player_pos(server, info)
        x, y, z = floor(float(x)), floor(float(y)), floor(float(z))
    
    else:
        x, y, z = floor(float(ctx["x"])), floor(float(ctx["y"])), floor(float(ctx["z"]))

    config = {
        "x": x,
        "y": y,
        "z": z,
    }


    # 检测回收坐标是否是空气
    rcon_result = server.rcon_query(f"execute in {world} if block {x} {y} {z} minecraft:air")
    # print(f"{rcon_result=} {config=} {json.dumps(config)=}")

    if rcon_result == "Test passed": # or rcon_result == "Test failed":
        # server.rcon_query(f"data modify storage minecraft:clearchunk 收集坐标点 set value {json.dumps(config)}")

        set_progress_info({"world": world,"收集坐标点": config})

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

    js = get_progress_info()
    if js.get("收集坐标点"):
        js.pop("收集坐标点")
        set_progress_info(js)

    server.reply(info, RText("移除收集点", RColor.green))


@permission
def sleep_set(src: CommandSource, ctx: dict):
    global server, info
    server, info = __get(src)

    # print(f"{ctx=}")

    sleep_time = float(ctx["time"])

    js = get_progress_info()

    js["sleep_time"] = sleep_time

    set_progress_info(js)

    server.reply(info, RText(f"设置每次清理后休眠时间为 {sleep_time} 秒", RColor.green))


@permission
def sleep_clear(src: CommandSource, ctx: dict):
    global server, info
    server, info = __get(src)

    js = get_progress_info()

    if js.get("sleep_time"):
        js.pop("sleep_time")
        set_progress_info(js)

    server.reply(info, RText("清除每次清理后休眠时间设置", RColor.green))


def help(src: CommandSource):
    global server, info
    server, info = __get(src)

    msg=[
        f"{CMD}    查看使用方法",
        f"{'='*10} center 使用方法 {'='*10}",
        f"{CMD} center R y_up y_down    以玩家当前位置为中心，清理半径R的正方形区域，y_up为上边界，y_down为下边界",
        f"{'='*10} 设置收集点 {'='*10}",
        f"{CMD} setcfg x y z    配置掉落物回收位置(会把掉落物收集到这个位置，一般在漏斗上方。)",
        f"{CMD} getcfg    查看掉落物回收位置",
        f"{CMD} delcfg    删除掉落物回收位置(不产生掉落物+不收集掉落物)",
        f"{'='*10} 设置sleep {'='*10}",
        f"{CMD} setsleep float    设置每次sleep时间，单位秒",
        f"{CMD} delsleep    清理sleep",
        f"{'='*10} 使用绝对坐标位置 {'='*10}",
        f"{CMD} pos x1,y1,z1 x2,y2,z2",
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
        # print(f"{text=}")
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
        Literal("setsleep")
        .then(
            Number("time").runs(lambda src, ctx: sleep_set(src, ctx))
        )
    )
    c.then(
        Literal("delsleep").runs(lambda src, ctx: sleep_clear(src, ctx))
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
            GreedyText("args").runs(lambda src, ctx: pos(src, ctx))
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
    global EXIT
    EXIT = True
    # server_src.unregister_help_message(CMD)
    server.logger.info(RText(f"{PLUGIN_NAME} 插件卸载成功", RColor.green))

