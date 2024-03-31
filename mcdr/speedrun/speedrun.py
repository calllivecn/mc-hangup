#!/usr/bin/env python3
# coding=utf-8
# date 2021-05-17 15:53:15
# author calllivecn <calllivecn@outlook.com>


import re
import os
import time
import math
import random
import traceback
from subprocess import run, PIPE

import psutil


from funcs import (
    RText,
    RColor,
    RAction,
    RStyle,
    RTextList,
    Literal,
    QuotableText,
    Text,
    GreedyText,
    Integer,
    new_thread,
    PermissionLevel,
    event_player_death,
)


cmdprefix = "." + "speedrun"

# 
TEAM = None


# 盔甲架名字, 要和speedrun里的一致数据包
armor_stand_name="armor_stand_freeze_23jl"

def get_pos_point(server, name):
        # 查询坐标
        rcon_result = server.rcon_query(f"data get entity {name} Pos")
        position = re.match(f"{name} has the following entity data: \[(-?[0-9\.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]", rcon_result)
        x, y, z = position.group(1), position.group(2), position.group(3)
        x, y, z = round(float(x)), round(float(y)), round(float(z))

        return x, y, z



def waitrcon(server):
    # server刚启动时，等待rcon
    while True:
        if server.is_rcon_running():
            # server.logger.info("rcon is running")
            break
        # else:
            # server.logger.info("wait rcon is running")
        time.sleep(1)
    
CPUs=os.cpu_count()

def cpu_bak():
    while True:
        call = run(["uptime"], stdout=PIPE)
        r = re.match(".* load average: (.*), (.*), (.*)", call.stdout.decode("utf8")).group(1)
        r = round(float(r)/CPUs, 2)

        if r <= 0.7:
            print("服务器负载下降成功")
            break
        else:
            time.sleep(1)
    return r

def cpu(server):
    c = 0
    i = 1
    while c < 5:
        if psutil.cpu_percent() <= 70:
            c += 1
        else:
            c = 0
        server.say(RText(f"加载地图中。。。{i}/s", RColor.yellow))
        i += 1
        print("等待服务器负载下降...")
        time.sleep(3)

    print("服务器负载下降成功")

#######################
#
# 添加 flow 的函数 begin
#
#######################


PLAYERS = {}

def get_pos(server, player):
    # 查询坐标
    rcon_result = server.rcon_query(f"data get entity {player} Pos")
    position = re.match(f"{player} has the following entity data: \[(.*)d, (.*)d, (.*)d\]", rcon_result)
    x, y, z = float(position.group(1)), float(position.group(2)), float(position.group(3))
    # 查询维度
    rcon_result = server.rcon_query(f"data get entity {player} Dimension")
    world = re.match(f'{player} has the following entity data: "(.*)"', rcon_result).group(1)
    return x, y, z, world


def get_rotation(server, player):
    result = server.rcon_query(f"data get entity {player} Rotation")
    rotation = re.match(f"{player} has the following entity data: \\[(.*)f, (.*)f\]", result)
    return float(rotation.group(1))

# 查看相对角度，返回方向字符。
def rotate(a):
    if 0 <= a < 22.5:
        return "↑"
    elif 22.5 <= a < 67.5:
        return "↗"
    elif 67.5 <= a < 112.5:
        return "→"
    elif 112.5 <= a < 157.5:
        return "↘"
    elif 157.5 <= a < 180:
        return "↓"
    elif -180 <= a < -157.5:
        return "↓"
    elif -157.5 <= a < -112.5:
        return "↙"
    elif -112.5 <= a < -67.5:
        return "←"
    elif -67.5 <= a < -22.5:
        return "↖"
    elif -22.5 <= a < 0:
        return "↑"


ANGLE = 180/math.pi

def victor(x1, y1, x2, y2):
    tmp = (x1*x2+y1*y2) / (math.sqrt((x1**2+y1**2)) * math.sqrt((x2**2+y2**2)))
    return math.acos(tmp) * ANGLE


def show(server, player, s):
    server.rcon_query(f"title {player} times 10 60 10")
    server.rcon_query(f"""title {player} subtitle {{"text":"{s}"}}""")
    server.rcon_query(f"""title {player} title {{"text":""}}""")


def flow(server, flow_time, player1, player2):
    C = 0
    interval = 1
    while C <= flow_time:
        C += interval
        # 如果玩家不在, 说明需要停止flow
        if not PLAYERS.get(player1):
            server.logger.info(f"{player1} 停止 flow {player2}")
            break

        time.sleep(interval)

        p1x, p1y, p1z, p1world = get_pos(server, player1)
        rotation = get_rotation(server, player1)
        # r = mc_to_360(rotation)
        r = round(rotation, 1)

        p2x, p2y, p2z, p2world = get_pos(server, player2)

        if p1world != p2world:
            show(server, player1, "⤬")
            continue

        X = (p2x - p1x)
        Z = (p2z - p1z)

        # 求与Z轴增大方向的夹角
        try:
            a = round(victor(0, 10, X, Z), 1)
        except ZeroDivisionError:
            continue

        if X >= 0:
            a = -a

        relative_angle = round(a - r, 1)

        if abs(relative_angle) > 180:
            relative_angle = round(360 - abs(relative_angle), 1)
            if r < 0:
                relative_angle = -relative_angle

        s = rotate(relative_angle)

        server.logger.debug(f"相对坐标系角度：{a} - flower: {r} = 相对方向：{relative_angle}  指向：{s}")
        show(server, player1, s)

    server.logger.info(f"本次 flow 结束：{player1} -> {player2}")


@new_thread("flow 任务")
def flow_thread(server, flow_time, player1, player2):
    PLAYERS[player1] = player2
    try:
        flow(server, flow_time, player1, player2)
    except Exception:
        if PLAYERS.get(player1):
            PLAYERS.pop(player1)
        server.logger.info(f"{player1} flow 任务退出。")
        traceback.print_exc()


#######################
#
# 添加 flow 的函数 begin
#
#######################


class Team:
    teamname = "SpeedRun"


    def __init__(self, server):
        self.server = server

        self.player_running = None
        self.game_started = False

        # 倒计时，中止flag
        self.countdowning = False

        # 玩家列表
        self.players = set()
        self.readys = set()

        self.x = None
        self.y = None
        self.z = None

    # 放数据包里做
    def init_speedrun(self):
        # 设置记分板
        self.server.rcon_query(f"""scoreboard objectives add death deathCount ["死亡记数"]""")

        # 设置得分板
        self.server.rcon_query(f"""scoreboard objectives add score dummy ["得分"]""")

        self.server.rcon_query(f"""team add {self.teamname}""")

        # 关闭团队PVP
        self.server.rcon_query(f"team modify {self.teamname} friendlyFire false")


    def join(self, player):

        self.players.add(player)

        # 给予玩家所有成就, 
        self.server.rcon_query(f"advancement grant @a everything")

        # 初始化玩家计分板
        # self.init_scoreboard(player)
        self.init_speedrun()

        # 开局中有新玩家进入服务器把他改在旁观者 ?
        self.server.rcon_query(f"team join {self.teamname} {player}")

        # 记录第一局的世界生出点
        if self.x == None or self.y == None or self.z == None:
            self.x, self.y, self.z = get_pos_point(self.server, player)

        welcome_title = f"欢迎来到大逃杀~！"
        self.server.rcon_query("title @a times 2 100 2")
        self.server.rcon_query(f"""title {player} subtitle {{"text":"{player}"}}""")
        self.server.rcon_query(f"""title {player} title {{"text":"{welcome_title}","bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false}}""")

        if self.game_started:
            self.server.rcon_query(f"gamemode spectator {player}")
            self.server.rcon_query(f"spectate @r[name=!{player}] {player}")
        else:
            self.server.rcon_query(f"gamemode adventure {player}")
    

    def leave(self, player):
        self.players.discard(player)
        self.readys.discard(player)

        # 如果剩下的玩家都已准备，就开局
        if not self.game_started and self.players == self.readys and len(self.players) > 1:
            self.gameid = time.monotonic()
            self.game_start(self.gameid)
    

    def ready(self, player):
        # 如果已经开始游戏，跳过
        if self.game_started:
            self.server.tell(player, RText(f"游戏已经开始，等待下一局."))
        else:
            self.readys.add(player)
            # debug
            self.server.logger.info(f"ready(self, {player}) self.players --> {self.players} --> readys: {self.readys}")

            if self.players == self.readys and len(self.players) > 1:
                if not self.game_started:
                    self.gameid = time.monotonic()
                    self.game_start(self.gameid)
                    self.server.logger.info("游戏线程启动完成。")
            else:
                # check 玩家人数，够不够开局
                self.server.say(f"还有人没有准备，或人数不够(至少需要2名玩家)。")
    
    def unready(self, player):
        if player in self.readys:
            self.readys.discard(player)

            if self.countdowning:
                self.countdowning = False

    
    def game_start_init(self):
        # 做一些，开局前的准备; # 在每次开局前做？

        #改用数据包做，方便，性能好。

        # 选出一个逃亡者
        self.player_running = random.choice(list(self.players))

        # 剩下的是killer
        p = self.players.copy()
        p.discard(self.player_running)
        self.killers = list(p)

        # 给逃亡者上tag, 结束时要取消掉
        self.server.rcon_query(f"tag {self.player_running} add running")

        self.server.rcon_query("function speedrun:game_start_init1")


        # 拿到当前位置
        self.x, self.y, self.z = get_pos_point(self.server, random.choice(list(self.players)))

        # 调换世界生出点
        self.x += 2000
        # spreadplayers <x> <z> <分散间距> <最大范围> [under 最大高度] <考虑队伍> <传送目标…>

        # 召唤一个看不见的小盔甲架，打上tag。
        self.server.rcon_query(f'''summon minecraft:armor_stand ~ ~ ~ {{Marker:1,Small:1,Invisible:1,NoGravity:1,Invulnerable:1,Tags:["{armor_stand_name}"]}}''')

        while True:
            self.server.say(RText("寻找新一局初生点...", RColor.yellow))

            # result = self.server.rcon_query(f"spreadplayers {self.x} {self.z} 15 30 false @a")
            # result = self.server.rcon_query(f"spreadplayers {self.x} {self.z} 50 60 false @a")

            result = self.server.rcon_query(f"""execute as @e[type=minecraft:armor_stand,tag={armor_stand_name}] run spreadplayers {self.x} {self.z} 50 60 false @s""")

            if re.match("Could not spread ([0-9]+) entities around (.*) \(too many entities for space - try using spread of at most ([0-9\.]+)\)", result):
                self.z += 500
            else:
                break
            time.sleep(1)

        self.server.logger.info(f"新局初生点：{result}")

        # 输送玩家过去
        self.server.rcon_query(f"spreadplayers {self.x} {self.z} 50 60 false @a")

        # 先freeze 玩家，等待地图完全加载好，
        self.server.rcon_query("tag @a add freeze")

        # 需要先等，服务负载下降。
        cpu(self.server)

        self.server.rcon_query("tag @a remove freeze")

        # 分散玩家
        while True:
            result = self.server.rcon_query(f"spreadplayers {self.x} {self.z} 50 60 false @a")
            self.server.logger.info(f"重新分散玩家: {result}")
            if re.match("Could not spread ([0-9]+) entities around (.*) \(too many entities for space - try using spread of at most ([0-9\.]+)\)", result):
                self.server.logger.info(f"需要等待重新分散玩家...")
                self.x += 50
            else:
                break

            time.sleep(1)
        

        # 设置世界中心和边界
        self.server.rcon_query(f"worldborder center {self.x} {self.z}")
        
        # 给每个玩家设置出生点，还有设置新的世界初生点。
        self.server.rcon_query("function speedrun:game_start_init2")


    @new_thread("Speed run thread")
    def game_start(self, gameid):
        # 点我unready
        unready = RText("秒钟后开始,点我unready。", RColor.yellow)
        unready.set_hover_text(RText("点我unready", RColor.green))
        unready.set_click_event(RAction.run_command, f"unready")

        # 10秒后游戏开始
        self.countdowning = True
        for i in range(5, 0, -1):

            # 如果有玩家 unready 取消开局
            if not self.countdowning:
                self.server.say(RText("取消开局，有玩家unready。", RColor.yellow))
                return

            self.server.say(RTextList(RText(f"{i} ", RColor.green), unready))
            time.sleep(1)

        # 开局前准备
        self.game_start_init()
        
        self.game_started = True

        # sleep = 30 # testing
        sleep = 5*60

        # 如果 逃亡者存活过30分钟，逃亡者胜利。
        for i in range(6):

            if self.gameid != gameid:
                self.server.logger.info(f"之前的游戏线程退出 gameid: {self.gameid}.")
                return

            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # 广播逃亡者位置，并高亮1分钟。
            self.running_x, self.running_y, self.running_z = get_pos_point(self.server, self.player_running)
            self.server.say(RTextList("逃亡者:", RText(self.player_running, RColor.yellow), "现在的位置是:", RText(f"x:{self.running_x} y:{self.running_y} z:{self.running_z} ", RColor.green), RText(f"{now}", RColor.green)))

            self.server.rcon_query(f"effect give @a[tag=running] minecraft:glowing 60 1 true")

            # 向他杀者显示, 逃亡者坐标。
            for killer in self.killers:
                flow_thread(self.server, 300, killer, self.player_running)

            time.sleep(sleep)

        # 时间到，逃亡者胜利。
        self.game_end("running")


    def game_end(self, who="running"):
        self.game_started = False
        self.gameid = time.monotonic()
        # 新一局，把玩家 self.readys 清空
        self.readys = set()

        # 结束flow 
        PLAYERS.clear()

        # 结束提示, running: 逃亡者胜。
        if who == "running":
            self.server.rcon_query("tag @a[tag=running] add win")
        else:
            self.server.rcon_query("tag @a[tag=!running] add win")
        
        self.server.rcon_query("function speedrun:game_end")

        # self.server.rcon_query("execute at @a run playsound minecraft:item.totem.use player @a")


    def player_death(self, player):
        if self.game_started and player == self.player_running:
            self.game_end("killer")

    def player_left(self, player):
        if self.game_started and player == self.player_running:
            self.game_end("killer")


@new_thread("wait rcon + 初始化")
def waitrcon_init(server):
    global TEAM
    waitrcon(server)
    server.logger.info("Speed Run 服务器启动完成")
    TEAM = Team(server)
    # TEAM.init_speedrun()


def on_server_startup(server):
    waitrcon_init(server)


def on_player_joined(server, player, info):
    global TEAM
    if TEAM == None:
        server.logger.info(f"TEAM is None 初始化.")
        TEAM = Team(server)

    TEAM.join(player)


def on_player_left(server, player):
    TEAM.leave(player)
    if player == TEAM.player_running:
        TEAM.player_left(player)

def on_info(server, info):
    if info.source != 0:
        return 
    
    if info.content == "ready":
        TEAM.ready(info.player)
        return

    elif info.content == "unready":
        TEAM.unready(info.player)
        return

    player = event_player_death(server, info.content)
    if player:
        TEAM.player_death(player)
    # else:
        # server.logger.info(f"没有检测到玩家死亡")



def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, "大逃杀", PermissionLevel.USER)
    global TEAM
    TEAM = Team(server)
    server.logger.info(f"TEAM --> {TEAM} {id(TEAM)}")

    # 如果是第一次启动
    if old_plugin == None:
        # TEAM = Team(server)
        pass
    else:
        # 修改重载前的，gameid.
        if hasattr(old_plugin.TEAM, "gameid"):
            old_plugin.TEAM.gameid = time.monotonic()
        # print("这玩意儿，才是执行了！")
        server.logger.info("这玩意儿，才是执行了！")
        TEAM.players = old_plugin.TEAM.players

def on_remove(server, info):
    print("这玩意儿，根本没执行啊！")
    # 修改重载前的gameid
    TEAM.gameid = time.monotonic()
    server.logger.info("修改重载前的gameid")


