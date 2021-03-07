#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-05 20:18:15
# author calllivecn <c-all@qq.com>

import re
import os
import time
import json
import copy
from pathlib import Path

from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer
from mcdreforged.permission.permission_level import PermissionLevel

PLUGIN_METADATA = {
    # ID（即插件ID）是您插件的身份字符串。它应该由小写字母，数字和下划线组成，长度为1到64
    'id': 'tp', 
    'version': '1.0.0',
    'name': '玩家位置点记录和传送',
    'author': [
        'calllivecn'
   ],
    'link': 'https://github.com/calllivecn/mc-hangup/',
    'dependencies': {
        'mcdreforged': '>=1.3.0',
    }
}

PLAYER_MAX_POINT = 20

# set it to 0 to disable hightlight
plugin_id = PLUGIN_METADATA["id"]
cmdprefix = "." + plugin_id
config_dir = Path(os.path.dirname(os.path.dirname(__file__)), "config", plugin_id)


USERTP = {}
INVITE = {}

# 如果插件重载，则退出。线程
PLUGIN_RELOAD = False

def permission(func):

    def warp(*args, **kwargs):
        # print(f"*args {args}  **kwargs {kwargs}", file=sys.stdout)
        server, info = __get(args[0])
        perm = server.get_permission_level(info)

        # print(f"warp(): {args} {kwargs}", file=sys.stdout)
        if perm >= PermissionLevel.USER:
            func(*args, **kwargs)
 
    return warp

def get_players(server):
    # 获取在线玩家
    result = server.rcon_query("list")
    server.logger.debug(f"result = server.rcon_query('list') -->\n{result}")
    match = re.match("There are ([0-9]+) of a max of ([0-9]+) players online:(.*)", result)

    if match.group(1) == "0":
        return []

    ls = match.group(3) 

    players = []
    for s in ls.split(","):
        players.append(s.strip())
    
    return players

def player_online(server, player):

    #result = server.rcon_query(f"data get entity {player} Name")
    result = server.rcon_query(f"experience query {player} points")


    #if re.search("No entity was found", result).group():
    if re.search(f"{player} has ([0-9]+) experience points", result).group():
        return True
    else:
        return False

def user_tp_store_init(server):

    players = get_players(server)

    if len(players) == 0:
        server.logger("当前没有玩家在线")
        return

    if not config_dir.exists():
        os.makedirs(config_dir)

    for p in get_players(server):
        player_json = config_dir / (p + ".json")
        if player_json.exists():
            server.logger.debug(f"加载 {p} 的收藏点")
            with open(player_json) as f:
                USERTP[p] = json.load(f)
        else:
            continue

    server.logger.debug(f".tp 插件初始化 USERTP: ------>\n{USERTP}")

def player_save(player, data):
    fullpathname = config_dir / (player + ".json")
    with open(fullpathname, "w+") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def playsound(server, player):
    server.rcon_query(f"execute at {player} run playsound minecraft:entity.player.levelup player {player}")

def click_text(player, label_name, world, x, y, z):
    r = RText(label_name, RColor.blue)
    r.set_hover_text(RText(f"点击传送[{x}, {y}, {z}]", RColor.green))
    # r.set_click_event(RAction.run_command, f"/execute at {player} in {world} run teleport {player} {x} {y} {z}")
    r.set_click_event(RAction.run_command, f"{cmdprefix} {label_name}")
    return r

def click_invite(player1, player2):
    r = RText(f"{player1} 邀请你tp TA.", RColor.green)
    r.set_hover_text(RText(f"点击向玩家 {player1} 传送", RColor.green))
    r.set_click_event(RAction.run_command, f"{cmdprefix} accept {player1}")
    return r

def __get(src):
    return src.get_server(), src.get_info()

@permission
def help(src):
    server, info = __get(src)

    msg=[f"{'='*10} 使用方法 {'='*10}",
    f"{cmdprefix}                               查看使用方法",
    f"{cmdprefix} <收藏点>                      tp 到收藏点",
    f"{cmdprefix} list                          列出所有收藏点",
    f"{cmdprefix} add <收藏点名字>              添加或修改当前位置为收藏点",
    f"{cmdprefix} remove <收藏点名字>           删除收藏点",
    f"{cmdprefix} rename <收藏点名字> <新名字>  修改收藏点名字",
    f"{cmdprefix} invite <玩家>                 邀请玩家到你当前的位置",
    f"{cmdprefix} accept <玩家>                 接收一个玩家对你的邀请(时效3分钟)",
    ]
    server.reply(info, "\n".join(msg))

    server.logger.debug(f"{USERTP}")


def check_level(server, info):
    # 查看玩家的等级够不够
    level = server.rcon_query(f"experience query {info.player} levels")

    l = re.match(f"{info.player} has ([0-9]+) experience levels", level).group(1)

    server.logger.debug(f"玩家 {info.player} 等级： {l}")

    if int(l) < 1:
        server.reply(info, RText("经验不足，至少需要1级", RColor.red))
        return False
    else:
        # 扣掉1级
        server.rcon_query(f"experience add {info.player} -1 levels")
        return True


@permission
def ls(src, ctx):
    server, info = __get(src)

    u = USERTP.get(info.player)

    msg = [
    f"{'='*10} 当前没有收藏点, 快使用下面命令收藏一个吧。 {'='*10}",
    f"{cmdprefix} add <收藏点名>",
    ]

    if u is None:
        server.reply(info, "\n".join(msg))
    else:
        msg = [RText(f"{'='*10} 收藏点 {'='*10}\n", RColor.white)]

        for label_name, data in u.items():
            msg.append(click_text(info.player, label_name, data["world"], data["x"], data["y"], data["z"]))
            msg.append("\n")

        server.reply(info, RTextList(*msg))

    server.logger.debug(f"list ctx -------------->\n{ctx}")


@permission
def teleport(src, ctx):
    server, info = __get(src)
    msg = [
    f"{'='*10} 当前没有收藏点, 快使用下面命令收藏一个吧。 {'='*10}",
    f"{cmdprefix} add <收藏点名>",
    ]

    server.logger.debug(f"tp() 执行了。src --------->\n{src} ctx ------------>\n{ctx}")

    u = USERTP.get(info.player)
    if u is None:
        server.reply(info, "\n".join(msg))
    else:
        label_name = ctx.get("label_name")
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
        server.tell(info.player, RText(f"{cmdprefix} 插件没有配置成功，请联系服主。", RColor.red))

    world = re.match('{} has the following entity data: "(.*)"'.format(info.player), rcon_result).group(1)

    # 查询坐标
    rcon_result = server.rcon_query(f"data get entity {info.player} Pos")
    position = re.search(f"{info.player} has the following entity data: \[(-?[0-9\.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]", rcon_result)
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

        server.tell(info.player, RTextList("地点: ", RText(label_name, RColor.blue), " 收藏成功"))
        playsound(server, info.player)

        player_save(info.player, u)

    server.logger.debug(f"add ctx -------------->\n{ctx}")

@permission
def remove(src, ctx):
    server, info = __get(src)

    u = USERTP.get(info.player)

    if u is None:
        server.tell(info.player, RText(f"当前没有收藏点.", RColor.red))
    else:
        label_name = ctx.get("label_name")

        label = u.get(label_name)

        if label is None:
            server.reply(info, RTextList(RText("没有 "), RText(label_name, RColor.blue), RText(" 收藏点")))
            return

        u.pop(label_name)

        player_save(info.player, u)

        server.reply(info, RTextList("地点: ", RText(label_name, RColor.blue, RStyle.strikethrough), " 删除成功"))
        playsound(server, info.player)

    server.logger.debug(f"remove ctx -------------->\n{ctx}")


@permission
def rename(src, ctx):
    server, info = __get(src)

    if USERTP.get(info.player) is None:
        server.tell(info.player, RText(f"当前没有收藏点.", RColor.red))
    else:
        u = USERTP.get(info.player)

        label_name = ctx["label_name"]
        label = u.get(label_name)

        if label is None:
            server.reply(info, RText(f"没有 {label_name} 收藏点", RColor.red))
        else:
            if check_level(server, info):
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

@new_thread(f"{cmdprefix} 清理过期的邀请")
def clear_expire_invite(server):
    while True:

        if PLUGIN_RELOAD:
            break

        server.logger.info(f"clear_expire_invite() 我有执行哦")
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
        server.reply(info, RText("不能向你自发送邀请", RColor.red))
        return
    
    # 邀请的玩家是否在线
    if player_online(server, invite_player):

        if check_level(server, info):

            # 查看邀请信息
            k = info.player + "_" + invite_player
            v = int(time.time())
            INVITE[k] = v

            server.tell(invite_player, click_invite(info.player, invite_player))
            server.reply(info, RTextList("向玩家 ", RText(f"{invite_player}", RColor.blue), " 发送tp邀请"))
            playsound(server, info.player)

    else:
        server.reply(info, RTextList("玩家 ", RText(f"{invite_player}", RColor.yellow), " 不在线"))

@permission
def accept(src, ctx):
    server, info = __get(src)

    accept_player = ctx["player"]
    
    # 对方是否在线
    if player_online(server, accept_player):

        if check_level(server, info):

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
    c = Literal(cmdprefix).runs(lambda src: help(src))
    c = c.then(QuotableText("label_name").runs(lambda src, ctx: teleport(src, ctx)))
    c.then(Literal("list").runs(lambda src, ctx: ls(src, ctx)))
    c.then(Literal("add").then(QuotableText("label_name").runs(lambda src, ctx: add(src, ctx))))
    c.then(Literal("remove").then(QuotableText("label_name").runs(lambda src, ctx: remove(src, ctx))))
    c.then(Literal("rename").then(QuotableText("label_name").then(QuotableText("label_name2").runs(lambda src, ctx: rename(src, ctx)))))
    c.then(Literal("invite").then(QuotableText("player").runs(lambda src, ctx: invite(src, ctx))))
    c.then(Literal("accept").then(QuotableText("player").runs(lambda src, ctx: accept(src, ctx))))
    return c


def on_unload(server):
    server.logger.info(f"{plugin_id} 卸载.")


def on_load(server, old_plugin):
    server.logger.info(f"{plugin_id} 的配置目录： {config_dir}")

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
        
    server.register_help_message(cmdprefix, '玩家收藏点，和传玩家到收藏点.', PermissionLevel.USER)
    server.register_command(build_command())


# 有下面两种用法??
#def on_player_joined(server, player):
    #pass

def on_player_joined(server, player, info):

    player_json = config_dir / (player + ".json")

    if player_json.exists():
        server.logger.info(f"加载玩家 {player} 收藏点")
        with open(player_json) as f:
            USERTP[player] = json.load(f)


def on_player_left(server, player):

    u = USERTP.get(player)

    if u is not None:
        server.logger.info(f"卸载玩家 {player} 收藏点")
        USERTP.pop(player)
