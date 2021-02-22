#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-19 16:11:15
# author calllivecn <c-all@qq.com>

import re
import os
import ssl
import sys
import time
import json
import binascii
import socket
from threading import Lock
from pathlib import Path
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

from mcdreforged.api.decorator import new_thread
# from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer
from mcdreforged.permission.permission_level import PermissionLevel

PLUGIN_METADATA = {
    # ID（即插件ID）是您插件的身份字符串。它应该由小写字母，数字和下划线组成，长度为1到64
    'id': 'mcsleep', 
    'version': '0.1.0',
    'name': '没有玩家时，休眠服务器。',
    'description': '可以的',
    'author': [
        'calllivecn'
   ],
    'link': 'https://github.com/calllivecn/mc-hangup/mcdr',
    'dependencies': {
        'mcdreforged': '>=1.3.0',
    }
}

cmdprefix = "." + PLUGIN_METADATA["id"]

PORT = 35565
SECRET = b""

cfg = Path("config") / "mcsleep.json"

def get_set_secret():
    global SECRET
    global PORT
    if cfg.exists():
        with open(cfg) as f:
           data = json.load(f) 

        SECRET = data["secret"]
        PORT = data["port"]

    else:
        SECRET = binascii.b2a_hex(ssl.RAND_bytes(16)).decode()
        with open(cfg, "w") as f:
            json.dump({"port": PORT, "secret": SECRET}, f, ensure_ascii=False, indent=4)


##########################################
#            # server up # server down   #
##########################################
# player is  #     1     # 2(要开启服务器)#
########################################## 
# player not #     3     #       4       #
##########################################

class State:
    def __init__(self):
        self._lock = Lock()
        self._state = 0

        self.PLAYERS = 1
        self.SERVER_UP = 2
        self.NOTPLAYERS = 3
        self.SERVER_DOWN = 4

    @property    
    def state(self):
        with self._lock:
            return self._state
    
    @state.setter
    def state(self, value):
        with self._lock:
            self._state = value

STATE = State()

# 没有玩家后10分钟关闭服务器
WAITMIN = 1

#################
#
# 定义HTTP接口 begin
#
#################


def httpResponse(msg):
    msg += "\n"
    msg = msg.encode("utf8")
    response = [
            "HTTP/1.1 200 ok",
            "Server: server",
            "Content-Type: text/plain;charset=UTF-8",
            "Content-Length: " + str(len(msg)),
            "\r\n",
            ]
    data = "\r\n".join(response).encode("utf8") + msg
    return data


def return_ip(conn):
    ip = conn.getpeername()[0]
    conn.send(httpResponse(ip))
    conn.close()


def send_handler(conn, selector):
    ip = conn.getpeername()[0]
    conn.send(httpResponse(ip))
    conn.close()
    selector.unregister(conn)


def recv_handler(conn, selector):

    global STATE

    data = conn.recv(1024).decode()
    oneline = data.split("\r\n")[0]
    print("client:", conn.getpeername(), file=sys.stderr)

    try:
        method, path, protocol = oneline.split(" ")
    except Exception as e:
        return_ip(conn)
        selector.unregister(conn)
        return

    if path == "/" + SECRET:
        # check_mc_server_is_running
        if STATE.state == STATE.NOTPLAYERS:
            conn.send(httpResponse("服务器在运行，没有玩家，倒计时关闭中..."))
        elif STATE.state == STATE.PLAYERS:
            conn.send(httpResponse("服务器在运行，且有玩家。"))
        elif STATE.state == STATE.SERVER_DOWN:
            conn.send(httpResponse("正在开启服务器..."))
            STATE.state = STATE.SERVER_UP
        else:
            conn.send(httpResponse("未知状态..."))

        conn.close()
    else:
        return_ip(conn)
    
    selector.unregister(conn)
    # selector.modify(conn, EVENT_WRITE, send_handler)


def handler_accept(conn, selector):
    sock , addr = conn.accept()
    sock.setblocking(False)
    selector.register(sock, EVENT_READ, recv_handler)


@new_thread(cmdprefix)
def httpmcsleep(server):

    sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    sock4.bind(("0.0.0.0", PORT))
    sock6.bind(("::", PORT))
    
    sock4.listen(128)
    sock6.listen(128)

    sock4.setblocking(False)
    sock6.setblocking(False)

    selector = DefaultSelector()
    selector.register(sock4, EVENT_READ, handler_accept)
    selector.register(sock6, EVENT_READ, handler_accept)

    try:
        while True:
            for key, event in selector.select():
                conn = key.fileobj
                func = key.data
                func(conn, selector)
    except Exception as e:
        server.logger.warning(f"httpmcsleep() 异常： {e}")

    finally:
        selector.close()
        sock4.close()
        sock6.close()


#################
#
# 定义HTTP接口 end
#
#################

@new_thread("server stop 倒计时")
def waitsleep(server):

    for i in range(WAITMIN * 60):

        if STATE.state == STATE.PLAYERS:
            return

        time.sleep(1)

    server.logger.info("mc sleep 关闭服务器中...")
    server.stop()
    server.wait_for_start()
    server.logger.info("mc sleep 服务器以关闭")


@new_thread("检查在线玩家数")
def players(server):

    global STATE

    while True:
        if server.is_rcon_running():
            server.logger.info("rcon is running")
            break
        else:
            server.logger.info("wait rcon is running")
            time.sleep(5)

    while True:

        if server.is_server_startup():
            result = server.rcon_query("list")
            server.logger.info(f"players() server.rcon_query() --> {result}")

            match = re.match("There are ([0-9]+) of a max of ([0-9]+) players online:(.*)", result)
            players = int(match.group(1))

            if players == 0:
                STATE.state = STATE.NOTPLAYERS
                waitsleep(server)
            else:
                STATE.state = STATE.PLAYERS
        
        if STATE.state == STATE.SERVER_DOWN:
            return

        time.sleep(30)



def permission(func):

    def warp(*args, **kwargs):
        server = args[0].get_server()
        info = args[0].get_info()
        perm = server.get_permission_level(info)
        if perm >= PermissionLevel.ADMIN:
            func(*args, **kwargs)
 
    return warp


def wakeup(src):
    server = src.get_server()
    server.start()


def on_info(server, info):
    if info.source == 1 and info.content == cmdprefix + " wakeup":
        server.logger.info("mcsleep wakeup")
        server.start()


def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, PLUGIN_METADATA["name"], PermissionLevel.ADMIN)

    # 读配置
    get_set_secret()

    # 启动http开关
    if old_plugin is None:
        httpmcsleep(server)

    if server.is_server_startup():
        server.logger.info(f"server is up")
        STATE.state = STATE.SERVER_UP
    else:
        server.logger.info(f"server is down")
        STATE.state = STATE.SERVER_UP


def on_server_startup(server):
    players(server)


# def on_player_left(server, player):
#     pass
# 

def on_player_joined(server, player, info):
    global STATE
    if STATE.state == STATE.NOTPLAYERS:
        server.logger.info(f"玩家 {player} 加入游戏，中断 waitsleep()")
        STATE.state = STATE.PLAYERS
