#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-14 16:01:21
# author calllivecn <calllivecn@outlook.com>

"""
# 拿到离玩家p1, 最近的一个实体的UUID
execute at p1 run data get entity @e[type=!player,distance=..10,limit=1,sort=nearest] UUID


使用方法
1. 把光标(游戏的十字准星)对准需要添加的实体。
2. 使用/tp (按tab键） 看到实体的UUID(像这样的:c7168f6d-e1b2-4176-9a0a-fa94021611be) 选中到输入栏上。
3. 在把/tp 命令修改为需要执行的命令，这样就可以使用UUID的方式操作实体了。

tp c7168f6d-e1b2-4176-9a0a-fa94021611be calllivecn
# 没有找到实体
No entity was found
"""

from tpem.funcs import (
    re,
    time,
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
    new_thread,
    permission,
    PermissionLevel,
    PluginServerInterface,
    Info,
    event_player_death,
)


CMD = CMDPREFIX + "tpem"

TPEM_DIR = CONFIG_DIR / "tpem"

TPEM_DICT = {}

@permission
def help(src):
    server, info = __get(src)

    msg=[f"{'='*10} 使用方法 {'='*10}",
    f"{CMD}                               查看使用方法",
    f"{CMD} list                          列出所有实体名和UUID",
    f"{CMD} add <名字> <UUID>              添加UUID为名字的实体",
    f"{CMD} remove <名字>                  删除收藏点",
    f"{CMD} tp <名字>                      tp对应宠物到你当前的位置",
    ]
    # msg = [ RText(m + "\n", RColor.white) for m in msg ]
    # server.reply(info, RTextList(*msg))
    server.reply(info, "\n".join(msg))


def list(server: PluginServerInterface, info: Info):
    # 列出所有实体
    if not TPEM_DIR.exists():
        server.reply(info, RText("没有任何实体", RColor.red))
        return

    files = list(TPEM_DIR.glob("*.json"))
    if len(files) == 0:
        server.reply(info, RText("没有任何实体", RColor.red))
        return

    msg = [f"{'='*10} 实体列表 {'='*10}\n"]
    for f in files:
        name = f.stem
        with open(f, "r") as fp:
            uuid = fp.read().strip()
        msg.append(f"{name} : {uuid}\n")

    server.reply(info, RTextList(*[RText(m, RColor.white) for m in msg]))
    return


def add(server, info, name, uuid):
    # 添加一个实体
    player_confg = TPEM_DIR / f"{info.player}.json"
    if player_confg.exists():
        server.reply(info, RText(f"实体 {name} 已经存在，请先删除后再添加", RColor.red))
        return

    with open(player_confg, "w") as fp:
        fp.write(uuid)
    server.reply(info, RText(f"实体 {name} 添加成功", RColor.green))    

    return


def bak(server, player):
    result = server.rcon_query(f"data get entity {player} DeathTime")
    if int(deathtime.group(1)) == 0:
        server.rcon_query(f"attribute {player} minecraft:generic.max_health base set 40")
        server.rcon_query(f"effect give {player} minecraft:instant_health 1 5")
        break


# 根本拿不到死亡信息
# def on_death_message(server, death_message):
    # server.logger.info(f"什么信息--> {death_message}")

def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    server.say('Welcome {}'.format(player))

def on_player_left(server: PluginServerInterface, player: str, info: Info):
    server.say('Goodbye {}'.format(player))


def build_command():
    c = Literal(CMD).runs(lambda src: help(src))
    c = c.then(Integer("name").runs(lambda src, ctx: tp(src, ctx)))
    c = c.then(Integer("name").runs(lambda src, ctx: (src, ctx)))
    return c


def on_load(server: PluginServerInterface, old_plugin: PluginServerInterface):
    server.register_help_message(CMD, RText("使用UUID记录实体对象，方便操作", RColor.yellow), PermissionLevel.USER)
    server.register_command(build_command())