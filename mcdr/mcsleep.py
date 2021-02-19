#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-19 16:11:15
# author calllivecn <c-all@qq.com>

import re
import os
import sys
import time
import json
import base64
import socket

from struct import pack

from mcdreforged.api.decorator import new_thread
# from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
# from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer
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
    'link': 'https://github.com/calllivecn/mc-hangup',
    'dependencies': {
        'mcdreforged': '>=1.3.0',
    }
}


# 没有玩家后10分钟关闭服务器
WAITMIN = 1

server_property = {"Version": "", "Protocol": 0, "MaxPlayers": 0}


@new_thread
def stop_server_before(server, waitmin):
    time.sleep(WAITMIN * 60)

    result = server.rcon_query("list")
    match = re.match("There are ([0-9]+) of a max of ([0-5]+) players online: (.*)", result)

    players = int(match.group(1))

    if players == 0:
        server.logger.info("mc sleep 关闭服务器")
        server.stop()

        while server.is_server_running():
            time.sleep(0.1)

        FakeServer(server)


@new_thread
def query_playernum_old(server):
    time.sleep(1)  # in case of server is not ready yet
    playerCount = Client().getResultNew()["OnlinePlayers"]
    if playerCount == 0:
        stop_server_before(server, WAITMIN)


@new_thread
def query_playernum(server):
        result = server.rcon_query("list")
        match = re.match("There are ([0-9]+) of a max of ([0-9]+) players online:", result)

        players = int(match.group(1))

        if players == 0:
            stop_server_before(server, WAITMIN)


def pic2base() -> bytes:
    '''encode the server-icon.png to base64'''
    image_path = "server/server-icon.png"
    with open(image_path, "rb") as f:
        image = f.read()
        image_base64 = base64.b64encode(image)
        return image_base64


def genStatus() -> bytes:
    # the favicon is https://minecraft-zh.gamepedia.com/File:White_Bed_JE3_BE2.png
    with open("config/mcsleep.png", "rb") as f:
        faviconBytes = base64.b64encode(f.read()).decode("ascii")

    msg = {
        "description":
            {"text":"服务器已休眠，点击登录唤醒。"},
        "players":{"max": server_property["MaxPlayers"],"online":0},
        "version":{"name": server_property["Version"] ,"protocol": server_property["Protocol"]},
        "favicon": f"data:image/png;base64,{faviconBytes}"
    }
    print(msg, file=sys.stderr)

    statusBytes = json.dumps(msg, ensure_ascii=False).encode("utf-8")
    statusBytes = bytes(encode_varint(len(statusBytes)), "latin-1") + statusBytes
    statusBytes = b'\x00' + statusBytes
    statusBytes = bytes(encode_varint(len(statusBytes)), "latin-1") + statusBytes
    return statusBytes


# def genLoginReturn() -> bytes:
#     msg = 'Server is starting... Please wait for a minute and try again!!\
#         For more information, check website https://mc.sciroccogti.top/!'
#     ret = msg.encode("utf-8")
#     ret = bytes(encode_varint(len(ret)), "latin-1") + ret
#     return ret

@new_thread
def FakeServer(server):
    '''
    Act as a server when the Java server is shut down
    ping request1: L1 \x00\xc2\x04 HOST c \xdd\x01\x01\x00
        L1: length from \x00 to \x01 (included)
        e.g. \x16\x00\xc2\x04\x12tis.union.worldc\xdd\x01\x01\x00
    ping request2: \xfe\x01\xfa\x00\x0b MC|PingHost+HOST \x00\x00 c \xdd
        e.g. \xfe\x01\xfa\x00\x0bMC|PingHost+tis.union.world\x00\x00c\xdd
    login request: L1 \x00\xc2\x04 HOST c \xdd\x02\r\x00 L2 USER
        L1: length from \x00 to \x02 (included)
        L2: length of USER
        e.g. \x16\x00\xc2\x04\x12tis.union.worldc\xdd\x02\r\x00\x0bSciroccogti
    '''

    server.logger.info("MC Sleep start!")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # TODO: read port from server.properties
    # waiting for port exiting TIME_WAIT
    while True:  
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            server_socket.bind(("0.0.0.0", 25565))
        except Exception as err:
            server.logger.warning("port 已经使用 1s 后重试...", err)
            server_socket.close()
            time.sleep(1)
        else:
            server.logger.info("MC Sleep 服务启动。")
            break

    server_socket.listen(128)

    try:
        while True:
            client_socket, client_addr = server_socket.accept()  # wait for client
            recv_data = client_socket.recv(50)
            print(recv_data, file=sys.stderr)
            print(recv_data.decode("unicode-escape"), file=sys.stderr)

            dataLength = decode_varint(recv_data[:2].decode("latin-1")) + 2

            # Judge if is "MC|PingHost+`ip`" or ping request 1
            # frame head
            if ((recv_data[0:2] == b"\xfe\x01" and recv_data[5:27].decode("utf-16-be") == "MC|PingHost") or len(recv_data) < dataLength + 2):
                server.logger.info("FakeServer get a ping")
                client_socket.send(genStatus())
                client_socket.close()
            else:
                # login request
                # start server here
                server.logger.info("FakeServer get a login request")
                client_socket.close()
                server_socket.close()
                server.start()
                break
                # client_socket.send(genLoginReturn())

    except Exception as e:
        server.logger.warning(f"listen Exception: {e}")
        server_socket.close()


class Client:

    # def __init__(self, host=socket.gethostname(), port=25565, timeout=5):
    def __init__(self, host="127.0.0.1", port=25565, timeout=5):
        self.host = host
        self.port = port  # 0 to use any available port
        self.timeout = timeout

    def __getDataNew(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        s.settimeout(self.timeout)
        s.connect((self.host, self.port))

        handShake = b"\x00"
        handShake += b"\x04"
        handShake += bytes(encode_varint(len(self.host)), "UTF-8")
        handShake += bytes(self.host, "UTF-8")
        handShake += pack("H", self.port)
        handShake += b"\x01"
        handShake = bytes(encode_varint(len(handShake)), "UTF-8") + handShake
        s.sendall(handShake)
        s.sendall(b'\x01\x00')

        data = s.recv(1024)
        dataLength = decode_varint(data[:2].decode("latin-1")) + 2
        while True:
            recv = s.recv(1024)
            data += recv
            if len(data) == dataLength:
                break
        s.close()
        assert data[2:3] == b"\x00"
        assert decode_varint(data[3:5].decode("latin-1")) == len(data[5:])
        return data[5:].decode("UTF-8")

    def getResultNew(self):
        global server_property

        status = {"Version": "", "MOTD": "",
                  "OnlinePlayers": 0, "MaxPlayers": 0}

        try:
            jsonData = json.loads(self.__getDataNew())
            status["Version"] = re.findall("(\d.\d+.\d)", jsonData["version"]["name"])[0]
            status["Protocol"] = jsonData["version"]["protocol"]
            status["MOTD"] = jsonData["description"]
            status["OnlinePlayers"] = int(jsonData["players"]["online"])
            status["MaxPlayers"] = int(jsonData["players"]["max"])
            status["ServerIcon"] = re.sub("\n", "", jsonData["favicon"])
        except Exception as e:
            print(f"Error in getResultNew: {e}", file=sys.stderr)
            print(f"status: {status}", file=sys.stderr)
        finally:
            print(f"finally status: {status}", file=sys.stderr)

            server_property["Version"] = status["Version"]
            server_property["MaxPlayers"] = status["MaxPlayers"]
            # server_property["Protocol"] = status["Protocol"]
            return status


def encode_varint(value):
    return "".join(encode_varint_stream([value]))


def decode_varint(value):
    return decode_varint_stream(value).__next__()


def encode_varint_stream(values):
    for value in values:
        while True:
            if value > 127:
                yield chr((1 << 7) | (value & 0x7f))
                value >>= 7
            else:
                yield chr(value)
                break


def decode_varint_stream(stream):
    value = 0
    base = 1
    for raw_byte in stream:
        val_byte = ord(raw_byte)
        value += (val_byte & 0x7f) * base
        if (val_byte & 0x80):
            base *= 128
        else:
            yield value
            value = 0
            base = 1



def on_load(server, old_plugin):
    server.register_help_message(PLUGIN_METADATA["id"], PLUGIN_METADATA["name"], PermissionLevel.ADMIN)
    # server.register_help_message("!!hibernate", "Hibernate server at %dmin after no one's online" % waitmin)

    if server.is_server_startup():

        while not server.is_rcon_running():
            time.sleep(0.1)
        
        server.logger.info(f"rcon running")
        query_playernum(server)


def on_server_startup(server):

    while not server.is_rcon_running():
            time.sleep(0.1)
        
    server.logger.info(f"服务器启动，rcon 运行。")
    query_playernum(server)


def on_player_left(server, player):
    query_playernum(server)
