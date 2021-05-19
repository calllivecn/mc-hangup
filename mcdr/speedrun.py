#!/usr/bin/env python3
# coding=utf-8
# date 2021-05-17 15:53:15
# author calllivecn <c-all@qq.com>


import re
import time
import random
from threading import Lock, get_ident
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer
from mcdreforged.permission.permission_level import PermissionLevel

PLUGIN_METADATA = {
    # ID（即插件ID）是您插件的身份字符串。它应该由小写字母，数字和下划线组成，长度为1到64
    'id': 'speedrun', 
    'version': '0.1.0',
    'name': '大逃杀',
    'description': '由一名玩家扮逃亡者，1~3名玩家扮追杀者的小游戏。',
    'author': [
        'calllivecn'
   ],
    'link': 'https://github.com/calllivecn/mc-hangup/mcdr',
    'dependencies': {
        'mcdreforged': '>=1.3.0',
    }
}

cmdprefix = "." + PLUGIN_METADATA["id"]

# 
global TEAM
TEAM = None

def get_pos(server, name):
        # 查询坐标
        rcon_result = server.rcon_query(f"data get entity {name} Pos")
        position = re.match(f"{name} has the following entity data: \[(-?[0-9\.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]", rcon_result)
        x, y, z = position.group(1), position.group(2), position.group(3)
        x, y, z = round(float(x)), round(float(y)), round(float(z))

        return x, y, z


players_deathcount = {}

def waitrcon(server):
    # server刚启动时，等待rcon
    while True:
        if server.is_rcon_running():
            # server.logger.info("rcon is running")
            break
        # else:
            # server.logger.info("wait rcon is running")
        time.sleep(1)


def init_player(server):
    if not server.is_rcon_running():
        return

    result = server.rcon_query("list")
    # server.logger.info(f"players() server.rcon_query() --> {result}")
    match = re.match("There are [0-9]+ of a max of [0-9]+ players online: (.*)", result)
    players_raw = match.group(1).split(",")
    for p in players_raw:
        if p == "":
            continue
        players_deathcount[p.strip()] = 0
    

    server.logger.info(f"players_deathcount{{}} --> {players_deathcount}")

    for p in players_deathcount.keys():
        result = server.rcon_query(f"scoreboard players get {p} death")
        if result:
            death = re.match(f"{p} has ([0-9]+) \[死亡记数\]", result)
            deathcount = int(death.group(1))
            players_deathcount[p] = deathcount
        else:
            server.rcon_query(f"scoreboard players set {p} death 0")
            players_deathcount[p] = 0


def haveplayer(server, content):

    # 排除玩家在线时，关服的情况。排除玩家退出的情况。
    if re.search("(.*) lost connection", content) or re.match(f"(.*) left the game", content):
        return None

    for player in players_deathcount.keys():
        result = re.search(player, content)
        if result:
            return player
    
    return None



class Team:
    teamname = "tmp"

    def __init__(self, server):
        self.server = server

        self.server.rcon_query("""scoreboard objectives add death deathCount ["死亡记数"]""")
        self.server.rcon_query("""scoreboard objectives setdisplay sidebar death""")

        self.server.rcon_query(f"""team add {self.teamname}""")
        # 关闭团队PVP
        self.server.rcon_query(f"team modify {self.teamname} friendlyFire false")

        # team 已建好
        self.team = True

        self.player_running = None

        # 玩家列表
        self.players = set()

        self.readys = set()
        self.unreadys = set()

        # 设置记分板
        self.server.rcon_query(f"""scoreboard objectives add death deathCount ["死亡记数"]""")
        self.server.rcon_query(f"""scoreboard objectives setdisplay sidebar death""")

        self.game_started = False

    def join(self, player):
        self.players.add(player)
        self.server.rcon_query(f"team join {self.teamname} {player}")
        # 死记记数设置为0
        self.server.rcon_query(f"scoreboard players set {player} death 0")

        # 设置第一个玩家的位置为第一局世界生出点
        self.x, y, self.z = get_pos(self.server, player)
        self.server.rcon_query(f"setworldspawn {self.x} {self.z}")

        welcome_title = f"{player} 欢迎来来大逃杀~！"
        self.server.rcon_query(f"""title {player} title {{"text":"{welcome_title}","bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false}}""")
        self.server.rcon_query(f"gamemode adventure {player}")

        self.unreadys.add(player)
    

    def leave(self, player):
        self.players.discard(player)
        self.unreadys.discard(player)
        self.readys.discard(player)
    

    def ready(self, player):
        self.readys.add(player)
        self.unreadys.discard(player)

        if len(self.unreadys) == 0 and len(self.readys) > 1:
            if not self.game_started:
                self.gameid = time.monotonic()
                self.game_start(self.gameid)
        else:
            # check 玩家人数，够不够开局
            self.server.say(f"还有人没有准备好，或人数不够。")
    
    def unready(self, player):
        self.unreadys.add(player)
        self.readys.discard(player)

    @new_thread("Speed run thread")
    def game_start(self, gameid):
        # 选出一个逃亡者
        ps = list(self.players)
        rand = random.randint(0, len(ps) - 1)
        self.player_running = ps[rand]

        # 10秒后游戏开始
        for i in range(10, 0, -1):
            self.server.say(RTextList(RText(f"{i}", RColor.green), " 秒钟后游戏开始, 请不要中途退出。"))
            time.sleep(1)
        
        self.server.rcon_query(f"team empty {self.teamname}")
        for player in self.players:
            self.server.rcon_query(f"gamemode survival {player}")
        
        self.game_started = True

        self.server.rcon_query("execute at @a run playsound minecraft:item.totem.use player @a")
        self.server.rcon_query("""title @a subtitle {"text":"游戏开始！", "bold": true, "color":"red"}""")
        self.server.rcon_query(f"""title @a title {{"text":"逃亡者是：{self.player_running}","bold":true, "color": "yellow"}}""")
        self.server.say(f"say 逃亡者是：{self.player_running}")

        # 如果 逃亡者存活过30分钟，逃亡者胜利。
        for i in range(1):
            time.sleep(1*60)

            if self.gameid != gameid:
                break

            # 广播逃亡者位置，并高亮1分钟。
            x, y, z = get_pos(self.server, self.player_running)
            self.server.say(RTextList("逃亡者:", RText(self.player_running, RColor.yellow), "现在的位置是:", RText(f"x:{x} y:{y} z:{z}", RColor.green)))
            self.server.rcon_query(f"effect give {self.player_running} minecraft:glowing 60")

        # 怎么结束？不好检测，玩家死亡。
        # 1. 使用 scoresbaord 记录玩家死亡数。
        # 2. 每次有玩家死亡，就拿到他的死亡记数，看看是否是逃亡者死亡。


        # 时间到，逃亡者胜利。
        if self.gameid == gameid and self.game_started:
            self.server.rcon_query(f"""title @a subtitle {{"text":"逃亡者 {self.player_running} 胜利！", "bold": true, "color":"red"}}""")
            self.server.rcon_query("""title @a title {"text":"游戏时间到！","bold":true, "color": "yellow"}""")
            self.server.rcon_query("execute at @a run playsound minecraft:item.totem.use player @a")

            self.game_end()

    def player_death(self, player):
        if self.game_started and player == self.player_running:
            self.server.rcon_query(f"""title @a subtitle {{"text":"{self.player_running} 死亡！", "bold": true, "color":"red"}}""")
            self.server.rcon_query("""title @a title {"text":"追杀者胜利！","bold":true, "color": "yellow"}""")
            self.server.rcon_query("execute at @a run playsound minecraft:item.totem.use player @a")

            self.game_end()

    def player_left(self, player):
        if self.game_started and player == self.player_running:
            self.server.rcon_query(f"""title @a subtitle {{"text":"{self.player_running} 离线！", "bold": true, "color":"red"}}""")
            self.server.rcon_query("""title @a title {"text":"追杀者胜利！","bold":true, "color": "yellow"}""")
            self.server.rcon_query("execute at @a run playsound minecraft:item.totem.use player @a")

            self.game_end()
    
    def game_end(self):
        self.game_started = False
        # 新一局，把玩家从 self.readys 移到 self.unreadys
        self.unreadys = self.readys
        self.readys = set()

        self.server.rcon_query(f"team join {self.teamname} @a")
        self.server.rcon_query(f"gamemode adventure @a")

        # spreadplayers <x> <z> <分散间距> <最大范围> [under 最大高度] <考虑队伍> <传送目标…>
        self.x += 5000
        self.server.rcon_query(f"spreadplayers {self.x} {self.z} 10 10 false @a")
        # 调换世界生出点
        self.server.rcon_query(f"setworldspawn {self.x} {self.z}")
        # 清除玩家成就
        self.server.rcon_query(f"advancement revoke @a everything")
        # 玩家生命恢复
        self.server.rcon_query(f"effect give @a minecraft:instant_health 1 20")


def on_server_startup(server):
    server.logger.info("Speed Run Server running")
    # waitrcon(server)

def on_player_joined(server, player, info):
    global TEAM
    if TEAM == None:
        TEAM = Team(server)
    TEAM.join(player)

    result = server.rcon_query(f"scoreboard players get {player} death")
    # server.logger.info(f"输出玩家字典 --> {players_deathcount}")

    deathcount = re.match(f"{player} has ([0-9]+) \[死亡记数\]", result)
    # server.logger.info(f"玩家：{player} 死亡记数 --> {deathcount.group(1)}")

    if deathcount:
        players_deathcount[player] = int(deathcount.group(1))
    else:
        players_deathcount[player] = 0
    
    # server.logger.info(f"输出玩家字典 --> {players_deathcount}")


def on_player_left(server, player):
    global TEAM
    TEAM.leave(player)
    if player == TEAM.player_running:
        TEAM.player_left(player)

def on_info(server, info):
    global TEAM
    if info.source != 0:
        return 
    
    if info.content == "ready":
        TEAM.ready(info.player)
        return

    elif info.content == "unready":
        TEAM.unready(info.player)
        return

    death_player = haveplayer(server, info.content)
    if death_player:
        server.logger.info(f"players_deathcount{{}} --> {players_deathcount}")
        result = server.rcon_query(f"scoreboard players get {death_player} death")
        count = re.match(f"{death_player} has ([0-9]+) \[死亡记数\]", result)

        if death_player and count:
            c = int(count.group(1))

            if players_deathcount[death_player] != c:
                players_deathcount[death_player] = c
                server.logger.info(f"检测到玩家：{death_player} 死亡, 次数为：{count.group(1)}")
                # 检测有到玩家死亡
                TEAM.player_death(death_player)


def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, "大逃杀", PermissionLevel.USER)
    global TEAM
    # 如果是第一次启动
    if old_plugin == None:
        init_player(server)
    else:
        players_deathcount.update(old_plugin.players_deathcount)
        # TEAM 生载无效。。。。！！！！
        TEAM = Team(server)




