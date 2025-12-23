#!/usr/bin/env python3
# coding=utf-8
# date 2025-06-28 21:25:17
# author calllivecn <calllivecn@outlook.com>

import os
import time
import json
from math import floor
from threading import Lock

from typing import (
    Any,
    Literal as PyLiteral,
)


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

"""
    block_cmd_suffix_list = (
        (("灵魂沙", "minecraft:soul_sand destroy"), ("岩浆块", "minecraft:magma_block destroy")),
        (("水草", "minecraft:seagrass strict"), ("水草", "minecraft:tall_seagrass strict")),
        (("海带", "minecraft:kelp_plant destroy"), ("海带头", "minecraft:kelp destroy")),
        (("水", "minecraft:water destroy"), ("岩浆", "minecraft:lava destroy")),
    )

"""

ID_NAME = "clearchunk"
PLUGIN_NAME = "一步步清空指定区域"

CMD = CMDPREFIX + ID_NAME

CLEARCHUNK = CONFIG_DIR / (ID_NAME + ".json")

EXIT = False

# server: PluginServerInterface
server: ServerInterface
info: Info


def get_progress_info():
    j = CLEARCHUNK
    if j.exists():
        with open(j) as f:
            return json.load(f)
    else:
        return {}

def set_progress_info(data: dict):
    j = CLEARCHUNK
    with open(j, "w+") as f:
        return json.dump(data, f, ensure_ascii=False, indent=4)

def del_progress_info():
    j = CLEARCHUNK
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


Progress = PyLiteral[
    "world",
    "clearchunk",
    "progress",
    "water",
    "block",
    "continue",
    "sleep_time",
    "sleep_water",
    "collection",
]

"""
js_clearchunk = [
    [x, y, z], [x, y, z]
]

js_progress = "water" or "block"
js_water = {
    "water": {
        "x": 0,
        "y": 0,
        "z": 0,
    }
}
js_block = {
    "block": {
        "x": 0,
        "y": 0,
        "z": 0,
    }
}
"""

class Sleep:
    def __init__(self):

        # 当前是否有任务在运行
        self.task_lock = Lock()

        self._sleep_lock = Lock()
        self._water_lock = Lock()

        js = get_progress_info()

        with self._sleep_lock:
            self.sleep_time = js.get("sleep_time")

        with self._water_lock:
            self.sleep_water = js.get("sleep_water")

    def sleep_if_needed(self):
        if self.sleep_time is not None:
            with self._sleep_lock:
                time.sleep(self.sleep_time)
    
    def modify_sleep(self, sleep_time: float|None=None):

        self.save("sleep_time", sleep_time)

        with self._sleep_lock:
            self.sleep_time = sleep_time
    
    def water_sleep_if_needed(self):
        if self.sleep_water is not None:
            with self._water_lock:
                time.sleep(self.sleep_water)
    
    def modify_water_sleep(self, sleep_time: float):

        self.save("sleep_water", sleep_time)
        with self._water_lock:
            self.sleep_water = sleep_time
    
    def save(self, typ: Progress, value: dict|Any):
        js = get_progress_info()
        js[typ] = value
        set_progress_info(js)
    
    def load(self, typ: Progress) -> dict:
        js = get_progress_info()
        if js:
            return js.get(typ, dict())
        return {}
    
    def clear(self, typ: Progress):
        js = get_progress_info()
        if js.get(typ):
            js.pop(typ)
            set_progress_info(js)

SLEEP = Sleep()

def check_progress(server: ServerInterface) -> bool:

    # 查看是否有未完成的任务
    step_word = SLEEP.load("progress")
    if not step_word:
        return False

    step = SLEEP.load(step_word) # type:ignore
    if step:
        world = SLEEP.load("world")
        clearchunk = SLEEP.load("clearchunk")

        msg = []
        msg.append(RText(f"之前有中断的任务: {world} -> {clearchunk}", RColor.red))
        msg.append("\n")
        msg.append(RText(f"如果需要断续之前中断的任务: {CMD} cfg continue", RColor.red))
        msg.append("\n")
        msg.append(RText(f"或者，删除之前中断的任务: {CMD} cfg taskclear", RColor.red))
        server.reply(info, RTextList(*msg))
        return True
    else:
        return False


@new_thread("clearchunk")
def start():

    world = SLEEP.load("world")
    clearchunk = SLEEP.load("clearchunk")

    # 当前是否在运行的任务
    if SLEEP.task_lock.locked():
        server.reply(info, RText(f"请等待已有任务执行完成：{world} -> {clearchunk}", RColor.red))
        return
    else:
        SLEEP.task_lock.acquire()


    # 查看是否有未完成的任务
    step_word = SLEEP.load("progress")
    if step_word and SLEEP.load(step_word): # type:ignore
        # 是否继续之前的任务
        if SLEEP.load("continue"):
            SLEEP.clear("continue")
            server.reply(info, RText("继续之前中断的任务。", RColor.green))
        else:
            msg = []
            msg.append(RText(f"之前有中断的任务: {world} -> {clearchunk}", RColor.red))
            msg.append("\n")
            msg.append(RText(f"如果需要断续之前中断的任务: {CMD} cfg continue", RColor.red))
            msg.append("\n")
            msg.append(RText(f"或者，删除之前中断的任务: {CMD} cfg taskclear", RColor.red))
            server.reply(info, RTextList(*msg))

    else:
        # 初始化进度阶段
        SLEEP.save("progress", "water")


    xyz = SLEEP.load("collection")
    if xyz:
        pos3 = [ xyz["x"], xyz["y"], xyz["z"] ]
    else:
        pos3 = None

    if not world:
        world = player_dimension(server, info)

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
 
    pos1, pos2 = clearchunk
    x1, y1, z1 = pos1
    x2, y2, z2 = pos2

    msg = []
    msg.append(RText(f"开始清理区域: {world} -> {clearchunk}", RColor.green))
    msg.append("\n")
    server.reply(info, RTextList(*msg))

    # 外扩后的边界
    x6, y6, z6 = x1-1, y1-1, z1-1
    x7, y7, z7 = x2+1, y2+1, z2+1

    x1f, y1f, z1f = x6, max(y6, y_world_down), z6
    x2f, y2f, z2f = x7, min(y7, y_world_up), z7

    flag_water_progress_x = False
    flag_water_progress_z = False

    progress =  SLEEP.load("progress")
    if progress == "water":
        # 继续进度清理，水和岩浆阶段
        water_progress = SLEEP.load("water")
        if water_progress:
            flag_water_progress_z = True
            flag_water_progress_x = True
            y2f = water_progress["y"]
    
        server.reply(info, RText("[水和岩浆]区域清理执行...", RColor.green))

        # 预清理整个区域的水和岩浆。清水区域，要比指定区域边界大8。
        step_r = 8
        for y in inclusive_range(y2f, y1f, -step_r):

            if y - step_r > y1f:
                y2_t = y - step_r
            else:
                y2_t = y1f

            z1f_progress = z1f
            if flag_water_progress_z:
                flag_block_progress_z = False
                z1f_progress = water_progress["z"]

            for z in inclusive_range(z1f_progress, z2f, step_r):
                if z + step_r < z2f:
                    z2_t = z + step_r
                else:
                    z2_t = z2f

                x1f_progress = x1f
                if flag_water_progress_x:
                    flag_block_progress_x = False
                    x1f_progress = water_progress["z"]

                for x in inclusive_range(x1f_progress, x2f, step_r):

                    if EXIT:
                        server.reply(info, RText("清理任务被中止。", RColor.red))
                        SLEEP.save("water", {"x": x, "y": y, "z": z})
                        return

                    if flag_water_progress_x:
                        flag_water_progress_x = False
                        x = water_progress["x"]
                        server.reply(info, RText(f"继续从当前位置清理[水和岩浆]: [{x}, {y}, {z}]", RColor.green))


                    if x + step_r < x2f:
                        x2_t = x + step_r
                    else:
                        x2_t = x2f

                    result = server.rcon_query(f"execute in {world} run fill {x} {y2_t} {z} {x2_t} {y} {z2_t} minecraft:glass replace minecraft:lava")
                    if result is None:
                        err = "清理区域 岩浆 时发生异常退出。"
                        server.reply(info, RText(err, RColor.red))
                        server.logger.error(err)
                        # 保存下进度
                        SLEEP.save("water", {"x": x, "y": y, "z": z})
                        SLEEP.task_lock.release()
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
                        # 保存下进度
                        SLEEP.save("water", {"x": x, "y": y, "z": z})
                        SLEEP.task_lock.release()
                        return
                    # msg = []
                    # msg.append(RText(f"现在清理 水 坐标范围: [{x},{y2_t},{z}] [{x2_t},{y},{z2_t}] ", RColor.yellow))
                    # msg.append(RText(result, RColor.yellow))
                    # server.reply(info, RTextList(*msg))

                    SLEEP.water_sleep_if_needed()

                    if x2_t == x2f:
                        break
                if z2_t == z2f:
                    break
            if y2_t == y1f:
                break

        server.reply(info, RText("[水和岩浆]区域清理执行完成", RColor.green))

    # ----------------------

    SLEEP.clear("water")
    SLEEP.save("progress", "block")
    progress = "block"

    y1_down = max(y1, y_world_down)
    y2_up = min(y2, y_world_up)

    flag_block_progress_x = False
    flag_block_progress_z = False

    if progress == "block":

        # 查看当前进度是否到清理，方块阶段
        block_progress = SLEEP.load("block")
        if block_progress:
            flag_block_progress_x = True
            flag_block_progress_z = True
            y2_up = block_progress["y"]

        server.reply(info, RText("[方块]区域清理执行...", RColor.green))

        # 正式清理整个区域的方块。 这里步长不能30太大。
        step_r = 8
        for y in inclusive_range(y2_up, y1_down, -step_r):

            if y - step_r > y1_down:
                y2_t = y - step_r
            else:
                y2_t = y1_down

            z1_progress = z1
            if flag_block_progress_z:
                flag_block_progress_z = False
                z1_progress = block_progress["z"]

            for z in inclusive_range(z1_progress, z2, step_r):

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

                x1_progress = x1
                if flag_block_progress_x:
                    flag_block_progress_x = False
                    x1_progress = block_progress["x"]
                    server.reply(info, RText(f"继续从当前位置清理 [方块]: [{x1_progress}, {y}, {z}]", RColor.green))

                for x in inclusive_range(x1_progress, x2, step_r):

                    # server.reply(info, RText(f"清理 [方块]: [{x}, {y}, {z}]", RColor.green))

                    if EXIT:
                        server.reply(info, RText("清理任务被中止。", RColor.red))
                        # 保存下进度
                        SLEEP.save("block", {"x": x, "y": y, "z": z})
                        SLEEP.task_lock.release()
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
                        # 保存下进度
                        SLEEP.save("block", {"x": x, "y": y, "z": z})
                        SLEEP.task_lock.release()
                        return

                    # msg = []
                    # msg.append(RText(f"现在清理 方块 坐标范围: [{x},{y2_t},{z}] [{x2_t},{y},{z2_t}] ", RColor.yellow))
                    # msg.append(RText(result, RColor.yellow))
                    # server.reply(info, RTextList(*msg))


                    if pos3 is not None:
                        server.rcon_query(f"execute in {world} as @e[type=item,x={x1},y={y1},z={z1},dx={xr},dy={yr},dz={zr}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")
                        server.rcon_query(f"execute in {world} as @e[type=minecraft:experience_orb,x={x1},y={y1},z={z1},dx={xr},dy={yr},dz={zr}] run tp @s {pos3[0]} {pos3[1]} {pos3[2]}")

                    SLEEP.sleep_if_needed()

                    if x2_t == x2:
                        break
                if z2_t == z2:
                    break
            if y2_t == y1_down:
                break
    
        server.reply(info, RText("[方块]区域清理执行完成", RColor.green))

    SLEEP.task_lock.release()
    SLEEP.clear("block")
    SLEEP.save("progress", "water")


@permission
def pos(src, ctx):
    global server, info
    server, info = __get(src)

    args = ctx["args"]
    args2 = ctx["args2"]
    # print(f"{args=}")

    pos1 = [ floor(float(i)) for i in args.split(",") ]
    pos2 = [ floor(float(i)) for i in args2.split(",") ]

    if pos1[0] > pos2[0] or pos1[1] > pos2[1] or pos1[2] > pos2[2]:
        server.reply(info, RText("起点坐标不能大于终点坐标", RColor.red))
        return
    
    if not check_progress(server):
        SLEEP.save("clearchunk", [pos1, pos2])
        start()


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

    if not check_progress(server):
        SLEEP.save("clearchunk", [[x1, y_down, z1], [x2, y_up, z2]])
        start()


def collection_point(server: ServerInterface, info: Info, xyz: dict=None):
    """
    配置参数：x1,y1,z1 做为收集掉落物的位置 
    """

    # 获取玩家所在维度
    world = player_dimension(server, info)

    if xyz is None:
        # 配置当前玩家位置为收集点
        x, y, z = player_pos(server, info)
        x, y, z = floor(float(x)), floor(float(y)), floor(float(z))
    
    else:
        x, y, z = floor(float(xyz["x"])), floor(float(xyz["y"])), floor(float(xyz["z"]))

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

        SLEEP.save("world", world)
        SLEEP.save("collection", config)

        server.reply(info, RText(f"配置回收坐标点：[{x}, {y}, {z}] ", RColor.green))

    elif rcon_result == "Test failed":
        server.reply(info, RText(f"回收位置 [{x}, {y}, {z}] 不是空气，请检查坐标是否正确。", RColor.red))

    elif rcon_result == "That position is not loaded":
        server.reply(info, RText(f"回收位置 [{x}, {y}, {z}] 未加载，请先加载该区域。", RColor.red))

    else:
        server.reply(info, RText(f"无法检测回收位置 [{x}, {y}, {z}] 是否为空气，rcon命令返回: {rcon_result}", RColor.red))


def collection_point_get(server: ServerInterface, info: Info):

    point = SLEEP.load("collection")
    if point:
        server.reply(info, RText(f"当前回收坐标点：{point}", RColor.green))
    else:
        server.reply(info, RText("未配置回收坐标点。", RColor.red))


@permission
def config(src: CommandSource, ctx: dict):
    global server, info
    server, info = __get(src)
    args = ctx["args"].split()
    server.logger.info(RText(f"当前config 参数：{args}", RColor.green))

    match args[0]:
        case "set":
            match args[1]:
                case "collection":

                    if len(args) == 5:
                        server.reply(info, RText("参数错误，使用方法：cfg set collection <x y z>", RColor.red))
                        xyz = {
                            "x": args[2],
                            "y": args[3],
                            "z": args[4],
                        }

                        collection_point(server, info, xyz)
                    else:
                        collection_point(server, info)

                case "sleep":

                    if len(args) != 3:
                        server.reply(info, RText("参数错误，使用方法：cfg set sleep <float>", RColor.red))
                        return

                    sleep_time = float(args[2])

                    SLEEP.modify_sleep(sleep_time)
                    server.reply(info, RText(f"设置每次清理后休眠时间为 {sleep_time} 秒", RColor.green))

                case "water_sleep":
                    if len(args) != 3:
                        server.reply(info, RText("参数错误，使用方法：cfg set water_sleep <float>", RColor.red))
                        return

                    sleep_time = float(args[2])

                    SLEEP.modify_water_sleep(sleep_time)
                    server.reply(info, RText(f"设置清理水和岩浆时的休眠时间为 {sleep_time} 秒", RColor.green))

                case _:
                    server.reply(info, RText("未知配置项", RColor.red))

        case "get":
            match args[1]:
                case "collection":
                    collection_point_get(server, info)

                case "sleep":
                    js = get_progress_info()
                    sleep_time = js.get("sleep_time")
                    if sleep_time is not None:
                        server.reply(info, RText(f"当前sleep时间为 {sleep_time} 秒", RColor.green))
                    else:
                        server.reply(info, RText("未设置sleep时间", RColor.red))
                
                case "water_sleep":
                    js = get_progress_info()
                    sleep_time = js.get("sleep_water")
                    if sleep_time is not None:
                        server.reply(info, RText(f"当前清理水和岩浆时的sleep时间为 {sleep_time} 秒", RColor.green))
                    else:
                        server.reply(info, RText("未设置清理水和岩浆时的sleep时间", RColor.red))

                case _:
                    server.reply(info, RText("未知配置项", RColor.red))

        case "del":
            match args[1]:
                case "collection":

                    js = get_progress_info()
                    if js.get("收集坐标点"):
                        js.pop("收集坐标点")
                        set_progress_info(js)

                    server.reply(info, RText("移除收集点", RColor.green))

                case "sleep":
                    # 清理sleep
                    js = get_progress_info()
                    if js.get("sleep_time"):
                        js.pop("sleep_time")
                        set_progress_info(js)
                        SLEEP.modify_sleep()

                    server.reply(info, RText("清除每次清理后休眠时间设置", RColor.green))
                
                case "water_sleep":
                    js = get_progress_info()
                    if js.get("sleep_water"):
                        js.pop("sleep_water")
                        set_progress_info(js)
                        SLEEP.modify_sleep()

                    server.reply(info, RText("清除清理水和岩浆时的休眠时间设置", RColor.green))

                case _:
                    server.reply(info, RText("未知配置项", RColor.red))
        
        case "continue":
            SLEEP.save("continue", True)
            start()

        case "taskclear":
            SLEEP.clear("progress")
            server.reply(info, RText("已删除之前中断的清理任务", RColor.green))

        case _:
            server.reply(info, RText("未知操作", RColor.red))
    


def help(src: CommandSource):
    global server, info
    server, info = __get(src)

    msg=[
        f"{CMD}    查看使用方法",
        f"{'='*10} center 使用方法 {'='*10}",
        f"{CMD} center R y_up y_down    以玩家当前位置为中心，清理半径R的正方形区域，y_up为上边界，y_down为下边界",
        f"{'='*10} 使用绝对坐标位置 {'='*10}",
        f"{CMD} pos x1,y1,z1 x2,y2,z2",
        "x1,y1,z1    起点位置坐标",
        "x2,y2,z2    结束位置坐标",
        f"{'='*10} 设置收集点(没配置则不收集) {'='*10}",
        f"{CMD} cfg set collection <x y z>    配置掉落物回收位置(会把掉落物收集到这个位置，一般在漏斗上方。)",
        f"{CMD} cfg get collection   查看掉落物回收位置",
        f"{CMD} cfg del collection   删除掉落物回收位置(不再产生掉落物+不收集掉落物,性能好.)",
        f"{'='*10} 设置清理方块sleep时间 {'='*10}",
        f"{CMD} cfg set sleep <float>    设置每次sleep时间，单位秒",
        f"{CMD} cfg get sleep    查看设置的sleep时间",
        f"{CMD} cfg del sleep    清理sleep",
        f"{'='*10} 设置清理水和岩浆sleep时间 {'='*10}",
        f"{CMD} cfg set water_sleep <float>    设置每次sleep时间，单位秒",
        f"{CMD} cfg get water_sleep    查看设置的sleep时间",
        f"{CMD} cfg del water_sleep    清理sleep",
        f"{'='*10} 任务管理 {'='*10}",
        f"{CMD} cfg continue    继续之前中断的清理任务",
        f"{CMD} cfg taskclear   删除之前中断的清理任务",
        f"{'='*10} 工作过程简略 {'='*10}",
        "1. 预清理指定区域外扩1格的水和岩浆",
        "2. 正式清理指定区域的方块",
        "3. 如果配置了收集点，则把掉落物和经验球传送到收集点",
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
    """
    能改为在最后使用QuotableText("args") 来接收所有参数，然后在函数内拆分参数
    这样就不需要定义很多子命令了
    c.then(
        Literal("setcfg").runs(lambda src: collection_point(src, None))
        .then(
            Number("x").then(
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
    """
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
            Text("args").then(
                Text("args2").runs(lambda src, ctx: pos(src, ctx))
            )
        )
    )
    c.then(
        Literal("cfg").then(
            GreedyText("args").runs(lambda src, ctx: config(src, ctx))
        )
    )
    return c


def on_load(server: PluginServerInterface, old_plugin: PluginServerInterface):
    """
    !!MCDR plugin reload 不会重新加载 Python 模块（.py 文件），而是重新调用 on_load，但模块本身（包括全局变量、类定义、锁对象等）仍然保留在内存中。
    """
    server.register_help_message(CMD, RText(PLUGIN_NAME, RColor.yellow), PermissionLevel.USER)
    server.register_command(build_command())

    if SLEEP.task_lock.locked():
        SLEEP.task_lock.release()
    
    server.logger.info(RText(f"{PLUGIN_NAME} on_load()成功", RColor.green))


def on_unload(server: PluginServerInterface):
    global EXIT
    EXIT = True
    # server_src.unregister_help_message(CMD)
    server.logger.info(RText(f"{PLUGIN_NAME} on_unload()成功", RColor.green))

