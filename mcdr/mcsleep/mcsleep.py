#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-19 16:11:15
# author calllivecn <c-all@qq.com>

import re
import ssl
import sys
import time
import json
import socket
import asyncio
import binascii
import ipaddress
import traceback
from threading import Lock
from pathlib import Path
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

from funcs import (
    CMDPREFIX,
    new_thread,
    PermissionLevel,
)

cmdprefix = CMDPREFIX + "mcsleep"

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


async def return_ip(writer, ip):
    writer.write(httpResponse(ip))
    await writer.drain()

    writer.close()
    await writer.wait_closed()


async def handler(reader, writer):

    addr = writer.transport.get_extra_info("peername")
    print("client: ", addr)

    try:
        data = await asyncio.wait_for(reader.read(1024), timeout=5)
    except asyncio.exceptions.TimeoutError:
        await return_ip(writer, addr[0])
        return


    if data:

        try:
            content = data.decode()

            oneline = content.split("\r\n")[0]

            method, path, protocol = oneline.split(" ")
        except UnicodeDecodeError as e:
            print(e, addr)
            await return_ip(writer, addr[0])
            return

        except Exception as e:
            print("有异常:", e)
            # traceback.print_exc()
            await return_ip(writer, addr[0])
            return

        if path == "/" + SECRET:
            # check_mc_server_is_running
            if STATE.state == STATE.NOTPLAYERS:
                writer.write(httpResponse("服务器在运行，没有玩家，倒计时关闭中..."))
                await writer.drain()
            elif STATE.state == STATE.PLAYERS:
                writer.write(httpResponse("服务器在运行，且有玩家。"))
                await writer.drain()
            elif STATE.state == STATE.SERVER_DOWN:
                writer.write(httpResponse("正在开启服务器..."))
                await writer.drain()
                STATE.state = STATE.SERVER_UP
            else:
                writer.write(httpResponse("未知状态..."))
                await writer.drain()

            writer.close()
            await writer.wait_closed()
        else:
            await return_ip(writer, addr[0])

async def recv_handler(r, w):
    try:
        await handler(r,w)
    except asyncio.exceptions.CancelledError:
        pass

async def asyncio_check_exit(server):
    """
    检查插件是否重载, 是：退出些loop
    """

    while True:
        if PLUGIN_RELOAD:
            # server.logger.info("olg_plugin 执行器退出...")
            print("old_plugin 执行器退出...")

            # close server
            server.close()
            await server.wait_closed()

            # 清理还未执行完成的 task
            tasks = asyncio.Task.all_tasks()
            tasks_len = len(tasks)
            if tasks_len:
                print("asyncio.Task.all_tasks() --> ", tasks_len)
                for task in tasks: 
                    task.cancel()
            break
        else:
            await asyncio.sleep(1)


async def httpmcsleep():
    server = await asyncio.start_server(recv_handler, "*", 35565, reuse_address=True, reuse_port=True)

    # addr, port = server.sockets[0].getsockname()
    # print("client:", addr, file=sys.stderr)

    await asyncio_check_exit(server)

    async with server:
        await server.serve_forever()


@new_thread(cmdprefix)
def start_httpmcsleep():
    try:
        asyncio.run(httpmcsleep())
    except asyncio.exceptions.CancelledError:
        pass
    print("asyncio.run() --> 安全退出")

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


def on_info(server, info):
    if info.source == 1 and info.content == cmdprefix + " wakeup":
        server.logger.info("mc sleep 启动服务器中...")
        STATE.state = STATE.SERVER_UP
    elif info.source == 1 and info.content == cmdprefix + " sleep":
        server.logger.info("mc sleep 关闭服务器...")
        STATE.state = STATE.SERVER_DOWN


def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, '没有玩家时，休眠服务器。', PermissionLevel.ADMIN)

    # 读配置
    get_set_secret()

    # 启动http开关
    if old_plugin is None:
        # start_httpmcsleep(server)
        start_httpmcsleep()
        players(server)
        execute(server)
    else:
        old_plugin.PLUGIN_RELOAD = True
        STATE.state = old_plugin.STATE.state
        time.sleep(3)

        # start_httpmcsleep(server)
        start_httpmcsleep()
        players(server)
        execute(server)

    if server.is_server_startup():
        server.logger.info(f"server is up")
        STATE.state = STATE.NOTPLAYERS

def on_unload(server):
    pass


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
