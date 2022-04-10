# coding=utf-8

import re
import math
import time
import traceback

from funcs import (
    CMDPREFIX,
    CONFIG_DIR,
    __get,
    RText,
    RColor,
    RAction,
    RTextList,
    Literal,
    QuotableText,
    new_thread,
)

CMD = CMDPREFIX + 'flow'

PLAYERS = {}

def get_pos(server, player):
    # 查询坐标
    rcon_result = server.rcon_query(f"data get entity {player} Pos")
    position = re.match(f"{player} has the following entity data: \[(.*)d, (.*)d, (.*)d\]", rcon_result)
    x, y, z = float(position.group(1)), float(position.group(2)), float(position.group(3))
    # 查询维度
    rcon_result = server.rcon_query(f"data get entity {player} Dimension")
    world = re.match(f'{player} has the following entity data: "(.*)"', rcon_result).group(1)
    return x, y, z, world


def get_rotation(server, player):
    result = server.rcon_query(f"data get entity {player} Rotation")
    rotation = re.match(f"{player} has the following entity data: \\[(.*)f, (.*)f\]", result)
    return float(rotation.group(1))


# 查看相对角度，返回方向字符。
def rotate(a):
    if 0 <= a < 22.5:
        return "↑"
    elif 22.5 <= a < 67.5:
        return "↗"
    elif 67.5 <= a < 112.5:
        return "→"
    elif 112.5 <= a < 157.5:
        return "↘"
    elif 157.5 <= a < 180:
        return "↓"
    elif -180 <= a < -157.5:
        return "↓"
    elif -157.5 <= a < -112.5:
        return "↙"
    elif -112.5 <= a < -67.5:
        return "←"
    elif -67.5 <= a < -22.5:
        return "↖"
    elif -22.5 <= a < 0:
        return "↑"


ANGLE = 180/math.pi

def victor(x1, y1, x2, y2):
    tmp = (x1*x2+y1*y2) / (math.sqrt((x1**2+y1**2)) * math.sqrt((x2**2+y2**2)))
    return math.acos(tmp) * ANGLE


def show(server, player, s):
    # server.rcon_query(f"title {player} times 10 60 10")
    server.rcon_query(f"""title {player} subtitle {{"text":"{s}"}}""")
    server.rcon_query(f"""title {player} title {{"text":""}}""")


def flow(server, player1, player2):
    while True:
        # 如果玩家不在, 说明需要停止flow
        if not PLAYERS.get(player1):
            server.logger.info(f"{player1} 停止 flow {player2}")
            break

        time.sleep(3)

        p1x, p1y, p1z, p1world = get_pos(server, player1)
        rotation = get_rotation(server, player1)
        # r = mc_to_360(rotation)
        r = round(rotation, 1)

        p2x, p2y, p2z, p2world = get_pos(server, player2)

        if p1world != p2world:
            show(server, player1, "⤬")
            continue

        X = (p2x - p1x)
        Z = (p2z - p1z)

        # 求与Z轴增大方向的夹角
        a = round(victor(0, 10, X, Z), 1)

        if X >= 0:
            a = -a

        relative_angle = round(a - r, 1)

        if abs(relative_angle) > 180:
            relative_angle = round(360 - abs(relative_angle), 1)
            if r < 0:
                relative_angle = -relative_angle

        s = rotate(relative_angle)

        server.logger.debug(f"相对坐标系角度：{a} - flower: {r} = 相对方向：{relative_angle} 指向：{s}")
        server.logger.debug(f"值计数：{a} - {r} = {relative_angle} 指向：{s}")
        show(server, player1, s)


@new_thread("flow 任务")
def flow_thread(server, player1, player2):
    try:
        flow(server, player1, player2)
    except Exception:
        if PLAYERS.get(player1):
            PLAYERS.pop(player1)
        server.logger.info(f"{player1} flow 任务退出。")
        traceback.print_exc()

def flow_cmd(src, ctx):
    server, info = __get(src)
    player2 = ctx.get("player")
    if info.player == player2:
        server.reply(info, RText(f"你不需要flow你自己", RColor.red))
    else:
        if PLAYERS.get(info.player):
            server.reply(info, RText(f"不用重复开flow功能", RColor.red))
        else:
            PLAYERS[info.player] = player2
            server.reply(info, RText(f"开始flow {player2}", RColor.yellow))
            flow_thread(server, info.player, player2)

def flow_stop(src, ctx):
    server, info = __get(src)
    if PLAYERS.get(info.player):
        server.reply(info, RText(f"停止flow", RColor.yellow))
        PLAYERS.pop(info.player)
    else:
        server.reply(info, RText(f"没有使用flow", RColor.yellow))


def on_player_joined(server, player, info):
    server.rcon_query(f"title {player} times 10 60 10")

def help_and_run(src):
    server, info = __get(src)

    line = [
        f"{'='*10} 说明 {'='*10}",
        f"1. ←↑→↓↖↗↘↙: 目标相对你的方向",
        f"2. ⤬: 目标你和不在同一维度",
        f"{'='*10} 使用方法 {'='*10}",
        f"{CMD}                    查看帮忙信息",
        f"{CMD} <玩家>              你想要跟随的玩家",
        f"{CMD}stop               停止flow",
    ]

    server.reply(info, "\n".join(line))


def build_command():
    c = Literal(CMD).runs(lambda src: help_and_run(src))
    c.then(QuotableText("player").runs(lambda src, ctx: flow_cmd(src, ctx)))
    return c

def on_load(server, prev):
    server.register_help_message(CMD, "跟随玩家位置")

    server.register_command(build_command())
    server.register_command(Literal(f"{CMD}stop").runs(lambda src, ctx: flow_stop(src, ctx)))

