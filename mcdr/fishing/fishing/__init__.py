#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-08 10:10:15
# author calllivecn <calllivecn@outlook.com>



from fishing.funcs import (
    time,
    __get,
    CMDPREFIX,
    match,
    player_online,
    PluginServerInterface,
    Info,
    CommandSource,
    PermissionLevel,
    Literal,
    QuotableText,
    RColor,
    RText,
    RTextList,
)


ID_NAME = "fishing"
PLUGIN_NAME = "自动钓鱼收杆(和fishing数据包配合使用)"

cmdprefix = CMDPREFIX + ID_NAME


def fishing_help(src):
    server, info = __get(src)
    msg = RTextList()
    msg.append(RText("自动钓鱼收杆插件帮助:\n", RColor.gold))
    msg.append(RText(f"{cmdprefix} [player]", RColor.yellow))
    msg.append(RText("        # 指定或者切换使用数据包收杆的玩家或者机器人\n", RColor.yellow))
    msg.append(RText("只能有一个玩家是数据包收杆(数据包收杆意味着，可以/tick无限加速。)\n", RColor.white))
    server.reply(info, msg)


def fishing(src: CommandSource, ctx: dict):
    server, info = __get(src)
    player = ctx.get("player")

    if not player_online(server, player):
        server.reply(info, RText(f"玩家 {player} 不在线!", RColor.red))
        return

    server.execute(f'''function fishing:start {{"name": "{player}"}}''')
    time.sleep(0.1)
    server.execute(f'''player {player} use once''')


def on_info(server: PluginServerInterface, info: Info):
    # server.logger.info(f"[fishing] 收到信息: {info=} {info.content=}")
    if info.source == 0:
        # * calllivecn 🐠 
        # [Not Secure] * calllivecn 🐠
        player = match(r"\[(.*)\] \* (.*) 🐠", info.content, groups=(1,2))
        if player:
            p = player[1]
            server.execute(f"player {p} use once")
            time.sleep(0.5)
            server.execute(f"player {p} use once")


def on_load(server: PluginServerInterface, old_plugin: PluginServerInterface):

    c = Literal(cmdprefix).runs(fishing_help)
    c.then(QuotableText("player").runs(fishing))

    server.register_help_message(cmdprefix, PLUGIN_NAME, PermissionLevel.USER)
    server.register_command(c)


def on_unload(server):
    pass

def on_player_joined(server, player, info):
    pass

def on_player_left(server, player):
    pass
