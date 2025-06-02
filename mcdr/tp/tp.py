#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-05 20:18:15
# author calllivecn <calllivecn@outlook.com>

import re
import os
import time
import json
import copy

from funcs import (
    CMDPREFIX,
    CONFIG_DIR,
    __get,
    RText,
    RColor,
    RAction,
    RStyle,
    RTextList,
    Literal,
    Integer,
    QuotableText,
    new_thread,
    permission,
    PermissionLevel,
    fmt,
    get_players,
    player_online,
    playsound,
)


ID_NAME = "tp"
PLUGIN_NAME = "玩家位置点记录和传送"

PLAYER_MAX_POINT = 20

CMD = CMDPREFIX + ID_NAME
TP_CONFIG_DIR = CONFIG_DIR / ID_NAME


USERTP = {}
INVITE = {}

# 如果插件重载，则退出。线程
PLUGIN_RELOAD = False

if not TP_CONFIG_DIR.exists():
    os.makedirs(TP_CONFIG_DIR)


def user_tp_store_init(server):

    players = get_players(server)

    if len(players) == 0:
        server.logger("当前没有玩家在线")
        return

    for p in get_players(server):
        player_json = TP_CONFIG_DIR / (p + ".json")
        if player_json.exists():
            server.logger.debug(f"加载 {p} 的收藏点")
            with open(player_json) as f:
                USERTP[p] = json.load(f)
        else:
            continue

    server.logger.debug(f".tp 插件初始化 USERTP: ------>\n{USERTP}")

def player_save(player, data):
    fullpathname = TP_CONFIG_DIR / (player + ".json")
    with open(fullpathname, "w+") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def click_invite(player1, player2):
    r = RText(f"{player1} 邀请你tp TA.", RColor.green)
    r.set_hover_text(RText(f"点击向玩家 {player1} 传送,或者输入 {CMD} accept {player1}", RColor.green))
    r.set_click_event(RAction.run_command, f"{CMD} accept {player1}")
    return r

def click_text(number, label_name, world, x, y, z):
    #r = RText(label_name, RColor.blue)
    r = RText(label_name, RColor.yellow)
    x = round(x)
    y = round(y)
    z = round(z)
    r.set_hover_text(RText(f"点击传送[{x}, {y}, {z}]", RColor.green))
    # r.set_click_event(RAction.run_command, f"/execute at {player} in {world} run teleport {player} {x} {y} {z}")
    # r.set_click_event(RAction.run_command, f"{CMD} {label_name}")
    r.set_click_event(RAction.run_command, f"{CMD} {number}")

    text = RTextList(RText("<", RColor.yellow), RText(number, RColor.green), RText(">", RColor.yellow), r)
    return text


@permission
def help(src):
    server, info = __get(src)

    msg=[f"{'='*10} 使用方法 {'='*10}",
    f"{CMD}                               查看使用方法",
    f"{CMD} <收藏点序号>                    tp 到收藏点",
    f"{CMD} list                          列出所有收藏点",
    f"{CMD} add <收藏点名字>                添加当前位置为收藏点",
    f"{CMD} update <收藏点序号>             更新收藏点为当前位置",
    f"{CMD} remove <收藏点序号>             删除收藏点",
    f"{CMD} rename <收藏点序号> <新名字>     修改收藏点名字",
    f"{CMD} invite <玩家>                  邀请玩家到你当前的位置",
    f"{CMD} accept <玩家>                  接收一个玩家对你的邀请(时效3分钟)",
    ]
    # msg = [ RText(m + "\n", RColor.white) for m in msg ]
    # server.reply(info, RTextList(*msg))
    server.reply(info, "\n".join(msg))


def check_level(server, info):
    # 查看玩家的等级够不够
    level = server.rcon_query(f"experience query {info.player} levels")

    l = re.match(f"{info.player} has ([0-9]+) experience levels", level).group(1)

    server.logger.debug(f"玩家 {info.player} 等级： {l}")
    level_threshold = 7
    if int(l) < level_threshold:
        server.reply(info, RText(f"经验不足，至少需要{level_threshold}级", RColor.red))
        return False
    else:
        # 扣掉1级
        server.rcon_query(f"experience add {info.player} -1 levels")
        return True


def number2key(server, info, u, number):
    if not 0 < number <= len(u):
        server.reply(info, RText("请输入正确的序号...", RColor.red))
        return False
    else:
        label_name = list(u.keys())[number-1]
        return label_name


@permission
def ls(src, ctx):
    server, info = __get(src)

    u = USERTP.get(info.player)

    msg = [
    f"{'='*10} 当前没有收藏点, 快使用下面命令收藏一个吧。 {'='*10}",
    f"{CMD} add <收藏点名>",
    ]

    if u is None:
        server.reply(info, "\n".join(msg))
    else:
        msg1 = [RText(f"{'='*10} 收藏点 {'='*10}\n", RColor.white)]
        msg2 = []
        seq = 1
        for label_name, data in u.items():
            msg2.append(click_text(seq, label_name, data["world"], data["x"], data["y"], data["z"]))
            seq += 1

        msg = msg1 + fmt(msg2)
        server.reply(info, RTextList(*msg))

    server.logger.debug(f"list ctx -------------->\n{ctx}")


@permission
def teleport(src, ctx):
    server, info = __get(src)
    msg = [
    f"{'='*10} 当前没有收藏点, 快使用下面命令收藏一个吧。 {'='*10}",
    f"{CMD} add <收藏点名>",
    ]

    server.logger.debug(f"tp() 执行了。src --------->\n{src} ctx ------------>\n{ctx}")

    u = USERTP.get(info.player)
    if u is None:
        server.reply(info, "\n".join(msg))
    else:
        # label_name = ctx.get("label_name")

        # 收藏点序号
        number = ctx.get("number")
        label_name = number2key(server, info, u, number)
        if label_name is False:
            return

        label = u.get(label_name)

        if label is None:
            server.reply(info, f"没有 {label_name} 收藏点")
        else:
            world = label["world"]
            x, y, z = label["x"], label["y"], label["z"]

            if check_level(server, info):
                server.rcon_query(f"execute at {info.player} in {world} run teleport {info.player} {x} {y} {z}")
                #playsound(server, info.player)
                server.rcon_query(f"execute at {info.player} run playsound minecraft:item.chorus_fruit.teleport player {info.player}")

        server.logger.debug(f"label_name: {label_name} 收藏点：  {label}")


@permission
def add(src, ctx):
    server, info = __get(src)

    # 查询世界
    rcon_result = server.rcon_query(f"data get entity {info.player} Dimension")

    if rcon_result is None:
        prompt = RText("rcon 没有开启, 请分别server.properties, MCDR/config.yml 开启。", RColor.red)
        server.logger.warning(prompt)
        server.tell(info.player, RText(f"{CMD} 插件没有配置成功，请联系服主。", RColor.red))

    world = re.match('{} has the following entity data: "(.*)"'.format(info.player), rcon_result).group(1)

    # 查询坐标
    rcon_result = server.rcon_query(f"data get entity {info.player} Pos")
    cmd = fr"{info.player} has the following entity data: \[(-?[0-9\.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]"
    position = re.search(cmd, rcon_result)
    x, y, z = position.group(1), position.group(2), position.group(3)
    x, y, z = round(float(x), 1), round(float(y), 1), round(float(z), 1)

    u = USERTP.get(info.player)
    if u is None:
        u = {}
        USERTP[info.player] = u
    elif len(u) > PLAYER_MAX_POINT:
        server.reply(info, RText(f"收藏点已到最大数： {PLAYER_MAX_POINT} 请删除后添加", RColor.red))
        return 

    # 查看玩家的等级够不够
    if check_level(server, info):
        label_name = ctx["label_name"]

        u[label_name] = {"world": world, "x": x, "y": y, "z":z}

        server.tell(info.player, RTextList("地点: ", RText(label_name, RColor.yellow), " 收藏成功"))
        playsound(server, info.player)

        player_save(info.player, u)

    server.logger.debug(f"add ctx -------------->\n{ctx}")


@permission
def update(src, ctx):
    server, info = __get(src)
    u = USERTP.get(info.player)

    # 查询世界
    rcon_result = server.rcon_query(f"data get entity {info.player} Dimension")

    if rcon_result is None:
        prompt = RText("rcon 没有开启, 请分别server.properties, MCDR/config.yml 开启。", RColor.red)
        server.logger.warning(prompt)
        server.tell(info.player, RText(f"{CMD} 插件没有配置成功，请联系服主。", RColor.red))

    world = re.match('{} has the following entity data: "(.*)"'.format(info.player), rcon_result).group(1)

    # 查询坐标
    rcon_result = server.rcon_query(f"data get entity {info.player} Pos")
    position = re.search(fr"{info.player} has the following entity data: \[(-?[0-9\.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]", rcon_result)
    x, y, z = position.group(1), position.group(2), position.group(3)
    x, y, z = round(float(x), 1), round(float(y), 1), round(float(z), 1)

    if u is None:
        server.tell(info.player, RText(f"当前没有收藏点.", RColor.red))
    else:

        number = ctx.get("number")
        label_name = number2key(server, info, u, number)
        if label_name is False:
            return

        label = u.get(label_name)

        if label is None:
            server.reply(info, RText(f"没有 {label_name} 收藏点", RColor.red))
        else:
            if check_level(server, info):
                u[label_name] = {"world": world, "x": x, "y": y, "z":z}
                player_save(info.player, u)
                playsound(server, info.player)
                server.reply(info, RText("更新新地点成功", RColor.green))


@permission
def remove(src, ctx):
    server, info = __get(src)

    u = USERTP.get(info.player)

    if u is None:
        server.tell(info.player, RText(f"当前没有收藏点.", RColor.red))
    else:
        number = ctx.get("number")
        label_name = number2key(server, info, u, number)
        if label_name is False:
            return

        label = u.get(label_name)

        if label is None:
            server.reply(info, RTextList(RText("没有 "), RText(label_name, RColor.yellow), RText(" 收藏点")))
            return

        u.pop(label_name)

        player_save(info.player, u)

        server.reply(info, RTextList("地点: ", RText(label_name, RColor.yellow, RStyle.strikethrough), " 删除成功"))
        playsound(server, info.player)

    server.logger.debug(f"remove ctx -------------->\n{ctx}")


@permission
def rename(src, ctx):
    server, info = __get(src)

    if USERTP.get(info.player) is None:
        server.tell(info.player, RText(f"当前没有收藏点.", RColor.red))
    else:
        u = USERTP.get(info.player)

        number = ctx.get("number")
        label_name = number2key(server, info, u, number)
        if label_name is False:
            return

        label = u.get(label_name)

        if label is None:
            server.reply(info, RText(f"没有 {label_name} 收藏点", RColor.red))
        else:
            v = u.pop(label_name)
            u[ctx["label_name2"]] = v
            player_save(info.player, u)
            playsound(server, info.player)
            server.reply(info, RText("修改名称成功", RColor.green))

    server.logger.debug(f"rename ctx -------------->\n{ctx}")

def pop_invite(k):
    try:
        INVITE.pop(k)
    except KeyError:
        pass

@new_thread(f"{CMD} 清理过期的邀请")
def clear_expire_invite(server):
    while True:

        if PLUGIN_RELOAD:
            break

        #server.logger.info(f"clear_expire_invite() 我有执行哦")
        time.sleep(180)
        c_t = int(time.time())
        for k, v in INVITE.items():
            if (c_t - v) > 180:
                pop_invite(k)

@permission
def invite(src, ctx):
    server, info = __get(src)

    invite_player = ctx["player"]

    if invite_player == info.player:
        server.reply(info, RText("不能向你自已发送邀请", RColor.red))
        return
    
    # 邀请的玩家是否在线
    if player_online(server, invite_player):

        if check_level(server, info):

            # 查看邀请信息
            k = info.player + "_" + invite_player
            v = int(time.time())
            INVITE[k] = v

            server.tell(invite_player, click_invite(info.player, invite_player))
            server.reply(info, RTextList("向玩家 ", RText(f"{invite_player}", RColor.yellow), " 发送tp邀请"))
            playsound(server, info.player)

    else:
        server.reply(info, RTextList("玩家 ", RText(f"{invite_player}", RColor.red), " 不在线"))

@permission
def accept(src, ctx):
    server, info = __get(src)

    accept_player = ctx["player"]
    
    # 对方是否在线
    if player_online(server, accept_player):

        # 查看邀请信息
        k = accept_player + "_" + info.player

        t = int(time.time()) - INVITE.get(k, 0)

        if t < 180:
            server.rcon_query(f"execute at {info.player} run teleport {info.player} {accept_player}")
            server.rcon_query(f"execute at {info.player} run playsound minecraft:item.chorus_fruit.teleport player {info.player}")
        else:
            server.reply(info, RText("玩家没有邀请你或邀请已超过3分钟", RColor.yellow))
            #playsound(server, info.player)

        pop_invite(k)

    else:
        server.reply(info, RTextList("玩家 ", RText(f"{accept_player}", RColor.red), " 不在线"))


def build_command():
    c = Literal(CMD).runs(lambda src: help(src))
    c = c.then(Integer("number").runs(lambda src, ctx: teleport(src, ctx)))
    c.then(Literal("list").runs(lambda src, ctx: ls(src, ctx)))
    c.then(Literal("add").then(QuotableText("label_name").runs(lambda src, ctx: add(src, ctx))))
    c.then(Literal("update").then(Integer("number").runs(lambda src, ctx: update(src, ctx))))
    c.then(Literal("remove").then(Integer("number").runs(lambda src, ctx: remove(src, ctx))))
    c.then(Literal("rename").then(Integer("number").then(QuotableText("label_name2").runs(lambda src, ctx: rename(src, ctx)))))
    c.then(Literal("invite").then(QuotableText("player").runs(lambda src, ctx: invite(src, ctx))))
    c.then(Literal("accept").then(QuotableText("player").runs(lambda src, ctx: accept(src, ctx))))
    return c


def on_unload(server):
    server.logger.info(f"{ID_NAME} 卸载.")


def on_load(server, old_plugin):
    server.logger.info(f"{CMD} 的配置目录: {TP_CONFIG_DIR}")

    #while not server.is_server_startup():
    #    server.logger.debug("等待server启动完成")
    #    time.sleep(1)

    global INVITE 
    global USERTP
    if old_plugin is None:

        server.logger.info("第一次启动")
        """
        这里是保证：禁用和启用插件时玩家数据都会被加载到内存
        服务器刚启动的时候, rcon没有准备好。
        也不会有玩家登录，不需要加载相关文件。
        之后要插件管理里卸载后，又重新加载的时候执行的。
        """
        if server.is_rcon_running():
            server.logger.info("is_rcon_running()")
            user_tp_store_init(server)

        clear_expire_invite(server)

    else:
        server.logger.info("非第一次启动")

        INVITE = copy.deepcopy(old_plugin.INVITE)
        USERTP = copy.deepcopy(old_plugin.USERTP)
        old_plugin.PLUGIN_RELOAD = True
        
    server.register_help_message(CMD, '玩家收藏点，和传玩家到收藏点.', PermissionLevel.USER)
    server.register_command(build_command())


# 有下面两种用法??
#def on_player_joined(server, player):
    #pass

def on_player_joined(server, player, info):

    player_json = TP_CONFIG_DIR / (player + ".json")

    if player_json.exists():
        server.logger.info(f"加载玩家 {player} 收藏点")
        with open(player_json) as f:
            USERTP[player] = json.load(f)


def on_player_left(server, player):

    u = USERTP.get(player)

    if u is not None:
        server.logger.info(f"卸载玩家 {player} 收藏点")
        USERTP.pop(player)
