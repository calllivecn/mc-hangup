#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-08 10:10:15
# author calllivecn <calllivecn@outlook.com>



from fishing.funcs import (
    time,
    CMDPREFIX,
    match,
    PluginServerInterface,
    Info,
)


ID_NAME = "fishing"
PLUGIN_NAME = "自动钓鱼收杆(和fishing数据包配合使用)"

cmdprefix = CMDPREFIX + ID_NAME


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
    pass

def on_unload(server):
    pass

def on_player_joined(server, player, info):
    pass

def on_player_left(server, player):
    pass
