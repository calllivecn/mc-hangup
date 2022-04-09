# coding=utf-8

import re
import math
import time

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

PLAYERS_DICT = {}


def welcome(server, player):
    msg = [
        RText("="*10 + "嗨～！" + "="*10 + "\n\n"),
        RText(f"欢迎！ {player} ！\n\n", RColor.yellow),
    ]

    r = RText(">>> 点击这里，查看可用命令 <<<", RColor.green)
    r.set_hover_text("!!help")
    r.set_click_event(RAction.run_command, f"!!help")

    msg.append(r)

    server.tell(player, RTextList(*msg))

def get_pos(server, player):
    # 查询坐标
    rcon_result = server.rcon_query(f"data get entity {player} Pos")
    position = re.search(f"{player} has the following entity data: \[(-?[0-9\.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]", rcon_result)
    x, y, z = float(position.group(1)), float(position.group(2)), float(position.group(3))
    return x, y, z


def get_rotation(server, player):
    result = server.rcon_query(f"data get entity {player} Rotation")
    rotation = re.match(f"{player} has the following entity data: \\[(.*)f, (.*)f\]", result)
    return float(rotation.group(1))


# 查看相对角度，返回方向字符。
def angle(a):
    if 337.5 <= a < 360 or 0 <= a < 22.5:
        return "↓"
    elif 22.5 <= a < 67.5:
        return "↘"
    elif 67.5 <= a < 112.5:
        return "→"
    elif 112.5 <= a < 157.5:
        return "↗"
    elif 157.5 <= a < 202.5:
        return "↑"
    elif 202.5 <= a < 247.5:
        return "↖"
    elif 247.5 <= a < 292.5:
        return "←"
    elif 292.5 <= a < 337.5:
        return "↙"

# 查看相对角度，返回方向字符。
def rotate(a):
    if abs(a) > 180:
        a = 360 - abs(a)

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
    server.rcon_query(f"title {player} times 10 60 10")
    server.rcon_query(f"""title {player} subtitle {{"text":"{s}"}}""")
    server.rcon_query(f"""title {player} title {{"text":""}}""")


@new_thread
def flow(server, player1, player2):
    while True:
        p1x, p1y, p1z = get_pos(server, player1)
        rotation = get_rotation(server, player1)
        # r = mc_to_360(rotation)
        r = round(rotation, 1)

        p2x, p2y, p2z = get_pos(server, player2)

        """
        try:
            # a = math.atan((p2x - p1x) / (p2z - p1z)) * (180/math.pi)
            X = (p2x - p1x)
            Z = (p2z - p1z)
            a = math.atan(X / Z) * (180/math.pi)
        except ZeroDivisionError:
            # Z == 0, 说明 a 为 90 or -90
            if p2x > p1x:
                a = -90
            else:
                a = 90
            
        if X >= 0:
            if Z > 0:
                a = a
            elif Z == 0:
                # 说明坐标相同, 在一起。
                show(server, player1, "↺")
            else:
                a -= -90
        elif X < 0:
            if Z >= 0:
                a = -a
            else:
                a += 90
            # 说明坐标相同, 在一起。
            # show(server, player1, "↺")
        """

        # relative_angle = r - a
        # s = angle(relative_angle)

        X = (p2x - p1x)
        Z = (p2z - p1z)

        # 求与Z轴增大方向的夹角
        a = round(victor(0, 10, X, Z), 1)

        if X >= 0:
            a = -a

        relative_angle = round(a - r, 1)

        if abs(relative_angle) > 180:
            relative_angle = 360 - abs(relative_angle)

        s = rotate(relative_angle)

        server.logger.debug(f"相对坐标系角度：{a} 指向：{s}")
        server.logger.info(f"相对坐标系角度：{a} - {r} = {relative_angle}  指向：{s}")

        show(server, player1, s)
        time.sleep(1)


def flow_cmd(src, ctx):
    server, info = __get(src)
    # welcome(server, info.player)
    player2 = ctx.get("player")
    if info.player == player2:
        server.reply(info, RText(f"你不需要flow你自己", RColor.red))
    else:
        flow(server, info.player, player2)

# def on_player_joined(server, player, info):
    # welcome(server, player)

def help_and_run(src):
    server, info = __get(src)

    line = [
        f"{'='*10} 使用方法 {'='*10}",
        f"{CMD}                      查看帮忙信息",
        f"{CMD} <玩家>              你想要跟随的玩家",
    ]

    server.reply(info, "\n".join(line))


def build_command():
    c = Literal(CMD).runs(lambda src: help_and_run(src))
    c.then(QuotableText("player").runs(lambda src, ctx: flow_cmd(src, ctx)))
    return c

def on_load(server, prev):
    server.register_help_message(CMD, "跟随玩家位置")

    server.register_command(build_command())

