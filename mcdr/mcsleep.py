#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-19 16:11:15
# author calllivecn <c-all@qq.com>

import re
import os
import time
import json
import socket
import ssl
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from pathlib import Path

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

PORT = 25665
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
            json.dump({"port": 25665, "secret": SECRET}, f, ensure_ascii=False, indent=4)



# 1: mc运行中，2：mc关闭中
STATE = 1

# 没有玩家后10分钟关闭服务器
WAITMIN = 1

#################
#
# 定义HTTP接口 begin
#
#################

def httpResponse(msg):
    response = [
            "HTTP/1.1 200 ok",
            "Server: server",
            "Content-Type: text/plain",
            "Content-Length: " + str(len(msg)),
            "\r\n",
            ]
    data = "\r\n".join(response) + msg
    return data.encode("utf8")

def send_handler(conn, selector):
    ip = conn.getpeername()[0]
    conn.send(httpResponse(ip))
    conn.close()
    selector.unregister(conn)

def recv_handler(conn, selector):
    data = conn.recv(4096)
    oneline = data.split("\r\n")
    selector.modify(conn, EVENT_WRITE, send_handler)

def handler_accept(conn, selector):
    sock , addr = conn.accept()
    sock.setblocking(False)
    selector.register(sock, EVENT_READ, recv_handler)


@new_thread
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


#################
#
# 定义HTTP接口 end
#
#################

@new_thread
def mcsleep(server):
    time.sleep(WAITMIN * 60)

    result = server.rcon_query("list")
    match = re.match("There are ([0-9]+) of a max of ([0-5]+) players online:(.*)", result)

    players = int(match.group(1))

    if players == 0:
        server.logger.info("mc sleep 关闭服务器中...")
        server.stop()
        server.wait_for_start()
        server.logger.info("mc sleep 服务器以关闭")


def permission(func):

    def warp(*args, **kwargs):
        server, info = __get(args[0])
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

    if server.is_server_startup():
        server.logger.info(f"rcon running")

def on_server_startup(server):

    if server.is_rcon_running():
        server.logger.info(f"服务器启动，rcon 运行。")


def on_player_left(server, player):
    pass
