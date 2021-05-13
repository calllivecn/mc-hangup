#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-19 16:11:15
# author calllivecn <c-all@qq.com>

import re
import ssl
import sys
import time
import json
import ipaddress
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

# 没有玩家后10分钟关闭服务器
WAITTIME = 10

cfg = Path("config") / "mcsleep.json"


# 插件重载时，退出线程
PLUGIN_RELOAD = False

def get_set_secret():
    global WAITTIME
    global PORT
    global SECRET
    if cfg.exists():
        with open(cfg) as f:
           data = json.load(f) 

        SECRET = data["secret"]
        PORT = data["port"]
        WAITTIME = data["waittime"]

    else:
        SECRET = binascii.b2a_hex(ssl.RAND_bytes(16)).decode()
        with open(cfg, "w") as f:
            json.dump({"waittime": WAITTIME, "port": PORT, "secret": SECRET}, f, ensure_ascii=False, indent=4)


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

        self.PLAYERS = 1
        self.IDLE = self.PLAYERS
        self.SERVER_UP = 2
        self.NOTPLAYERS = 3
        self.SERVER_DOWN = 4

        self._state = self.SERVER_UP

    @property    
    def state(self):
        with self._lock:
            return self._state
    
    @state.setter
    def state(self, value):
        with self._lock:
            self._state = value

STATE = State()

#################
#
# 定义HTTP接口 begin
#
#################


def httpResponse(msg):
    msg = "<h1>" + msg + "</h1>\n"
    msg = msg.encode("utf8")
    response = [
            "HTTP/1.1 200 ok",
            "Server: server",
            "Content-Type: text/html;charset=UTF-8",
            "Content-Length: " + str(len(msg)),
            "\r\n",
            ]
    data = "\r\n".join(response).encode("utf8") + msg
    return data


def return_ip(conn):
    ip46, port, _, _ = conn.getpeername()

    ip46 = ipaddress.IPv6Address(ip46)
    if ip46.ipv4_mapped:
        ip = ip46.ipv4_mapped
    else:
        ip = ip46.compressed

    conn.send(httpResponse(ip))
    conn.close()


def send_handler(conn, selector):
    ip = conn.getpeername()[0]
    conn.send(httpResponse(ip))

def conn_exit(conn, selector):
    conn.close()
    selector.unregister(conn)


def recv_handler(conn, selector):

    addr = conn.getpeername()
    print("client:", addr, file=sys.stderr)

    data = conn.recv(1024)

    if data:

        try:
            content = data.decode()

            oneline = content.split("\r\n")[0]

            method, path, protocol = oneline.split(" ")
        except UnicodeDecodeError as e:
            print(e, addr)
            conn_exit(conn, selector)
            return
        except Exception as e:
            print("有异常:", e)
            return_ip(conn)
            conn_exit(conn, selector)
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

        else:
            return_ip(conn)
    
    conn_exit(conn, selector)
    # selector.modify(conn, EVENT_WRITE, send_handler)


def handler_accept(conn, selector):
    sock , addr = conn.accept()
    sock.setblocking(False)
    selector.register(sock, EVENT_READ, recv_handler)


@new_thread(cmdprefix)
def httpmcsleep(server):

    #sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    #sock4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    sock6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

    #sock4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)
    sock6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)

    #sock4.bind(("0.0.0.0", PORT))
    sock6.bind(("::", PORT))
    
    #sock4.listen(128)
    sock6.listen(128)

    #sock4.setblocking(False)
    sock6.setblocking(False)

    selector = DefaultSelector()
    #selector.register(sock4, EVENT_READ, handler_accept)
    selector.register(sock6, EVENT_READ, handler_accept)

    try:
        while True:
            for key, event in selector.select(0.1):
                conn = key.fileobj
                func = key.data
                func(conn, selector)

            # selector.select(0.1) 超时处理。
            if PLUGIN_RELOAD == True:
                return

    except Exception as e:
        server.logger.warning(f"httpmcsleep() 异常： {e}")

    finally:
        selector.close()
        #sock4.close()
        sock6.close()


#################
#
# 定义HTTP接口 end
#
#################

@new_thread("mc sleep 执行器")
def execute(server):

    waittime = WAITTIME * 60
    print_count = 60
    while True:

        time.sleep(1)

        if PLUGIN_RELOAD:
            server.logger.info("olg_plugin 执行器退出...")
            return
        

        if STATE.state != STATE.NOTPLAYERS:
            waittime = WAITTIME * 60

        
        if STATE.state == STATE.SERVER_UP:
            server.logger.info("启动服务器中...")

            if not server.is_server_running():
                server.start()

            STATE.state = STATE.NOTPLAYERS

        elif STATE.state == STATE.SERVER_DOWN:

            if server.is_server_running():
                server.logger.info("关闭服务器中...")
                server.stop()
                server.wait_for_start()
                server.logger.info("服务器已关闭")

        elif STATE.state == STATE.PLAYERS:
            pass

        elif STATE.state == STATE.NOTPLAYERS:
            waittime -= 1

            if (waittime % print_count) == 0:
                server.logger.info(f"等待玩家加入... {waittime}秒后关闭服务器")

            if waittime < 0:
                STATE.state = STATE.SERVER_DOWN
            else:
                continue
        

def waitrcon(server):
    # server刚启动时，等待rcon
    while True:

        if server.is_rcon_running():
            # server.logger.info("rcon is running")
            break
        # else:
            # server.logger.info("wait rcon is running")
        
        time.sleep(5)


@new_thread("检查在线玩家数")
def players(server):

    while True:

        if server.is_server_startup():

            waitrcon(server)

            result = server.rcon_query("list")
            # server.logger.info(f"players() server.rcon_query() --> {result}")

            match = re.match("There are ([0-9]+) of a max of ([0-9]+) players online:(.*)", result)
            players = int(match.group(1))

            if players == 0:
                STATE.state = STATE.NOTPLAYERS
            else:
                STATE.state = STATE.PLAYERS

        # 每秒check退出标志
        for _ in range(30):
            if PLUGIN_RELOAD:
                return
            else:
                time.sleep(1)



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
    server.logger.info("mc sleep 启动服务器中...")
    STATE.state = STATE.SERVER_UP


def on_info(server, info):
    if info.source == 1 and info.content == cmdprefix + " wakeup":
        STATE.state = STATE.SERVER_UP


def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, PLUGIN_METADATA["name"], PermissionLevel.ADMIN)

    # 读配置
    get_set_secret()

    # 启动http开关
    if old_plugin is None:
        httpmcsleep(server)
        players(server)
        execute(server)
    else:
        old_plugin.PLUGIN_RELOAD = True
        STATE.state = old_plugin.STATE.state
        time.sleep(3)

        httpmcsleep(server)
        players(server)
        execute(server)

    if server.is_server_startup():
        server.logger.info(f"server is up")
        STATE.state = STATE.NOTPLAYERS


#def on_server_startup(server):
#    server.logger.info("on_server_startup()")
#    STATE.state = STATE.NOTPLAYERS
#
#def on_server_stop(server):
#    server.logger.info("on_server_stop()")
#    STATE.state = STATE.SERVER_DOWN


# def on_player_left(server, player):
#     pass
# 

def on_player_joined(server, player, info):
    if STATE.state == STATE.NOTPLAYERS:
        server.logger.info(f"玩家 {player} 加入游戏，中断 waitsleep")
        STATE.state = STATE.PLAYERS
