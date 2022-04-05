#!/usr/bin/env python3
# coding=utf-8
# date 2021-05-17 15:53:15
# author calllivecn <c-all@qq.com>


import re
import time
import random
from threading import Thread, Lock, get_ident
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE


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
)


# 我的线程装饰器
def newthread(func):
    def wrap(*args, **kwargs):
        print("我的线程开始执行。")
        th = Thread(target=func, args=args, kwargs=kwargs)
        th.start()
        return th
    
    return wrap
        

cmdprefix = "." + "speedrun"

# 
TEAM = None

def get_pos(server, name):
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



class Team:
    teamname = "SpeedRun"


    def __init__(self, server):
        self.server = server

        self.player_running = None
        self.game_started = False

        # 倒计时，中止flag
        self.countdowning = False

        # 在重载时，初始化在线玩家死亡计数
        self.players_deathcount = {}

        # 玩家列表
        self.players = set()
        self.readys = set()

        # 记录世界出生点
        self.x = None
        self.y = None
        self.z = None

        if not server.is_rcon_running():
            return

        # 设置记分板
        self.server.rcon_query(f"""scoreboard objectives add death deathCount ["死亡记数"]""")

        # 设置得分板
        self.server.rcon_query(f"""scoreboard objectives add score dummy ["得分"]""")

        self.server.rcon_query(f"""team add {self.teamname}""")
        # 关闭团队PVP
        self.server.rcon_query(f"team modify {self.teamname} friendlyFire false")

        result = self.server.rcon_query("list")
        # server.logger.info(f"players() server.rcon_query() --> {result}")
        match = re.match("There are [0-9]+ of a max of [0-9]+ players online: (.*)", result)
        players_raw = match.group(1).split(",")
        for p in players_raw:
            if p == "":
                continue
            player = p.strip()
            self.players_deathcount[player] = 0
            self.players.add(player)
        
        # 插件重载时，随机拿个玩家的，设置为世界出生点。
        if len(self.players) >= 1:
            self.setworldspawn()
        
        self.init_scoreboard()

    # 初始化玩家的计分板
    def init_scoreboard(self, p=None):

        if p == None:
            for player in self.players_deathcount.keys():
                result = self.server.rcon_query(f"scoreboard players get {player} death")

                if re.match(f"Can't get value of death for {player}; none is set", result):
                    self.server.rcon_query(f"scoreboard players set {player} death 0")
                    self.players_deathcount[player] = 0
                else:
                    deathcount = re.match(f"{player} has ([0-9]+) \[死亡记数\]", result)
                    self.players_deathcount[player] = int(deathcount.group(1))
        
            self.server.logger.info(f"players_deathcount{{}} --> {self.players_deathcount}")

            # 设置初始得分为 0
            for player in self.players_deathcount.keys():
                result = self.server.rcon_query(f"scoreboard players get {player} score")

                if re.match(f"Can't get value of score for {player}; none is set", result):
                    self.server.rcon_query(f"scoreboard players set {player} score 0")

            # self.server.logger.info(f"输出玩家字典 --> {TEMA.players_deathcount}")
        else:

            result = self.server.rcon_query(f"scoreboard players get {p} death")

            if re.match(f"Can't get value of death for {p}; none is set", result):
                self.server.rcon_query(f"scoreboard players set {p} death 0")
                self.players_deathcount[p] = 0
            else:
                deathcount = re.match(f"{p} has ([0-9]+) \[死亡记数\]", result)
                if deathcount is None:
                    self.players_deathcount[p] = 0
                else:
                    self.players_deathcount[p] = int(deathcount.group(1))

            # 设置初始得分为 0
            result = self.server.rcon_query(f"scoreboard players get {p} score")

            if re.match(f"Can't get value of score for {p}; none is set", result):
                self.server.rcon_query(f"scoreboard players set {p} score 0")

        # 至少要有玩家和，至少有一个玩家有对应记分板的值，才能显示出来。。。
        self.server.rcon_query(f"""scoreboard objectives setdisplay list death""")
        self.server.rcon_query(f"""scoreboard objectives setdisplay sidebar score""")


    # 控制台有玩家名字相关的消息, 就说明可能是有玩家死亡，在对比玩家死亡记数。
    def haveplayer(self, content):

        # 排除玩家在线时，关服的情况。排除玩家退出的情况。
        if re.search("(.*) lost connection", content) or re.match(f"(.*) left the game", content) or re.match("(.*) joined the game", content):
            return None

        for player in self.players_deathcount.keys():
            result = re.search(player, content)
            if result:
                return player

        return None


    def join(self, player):
        self.players.add(player)

        # 开局中有新玩家进入服务器把他改在旁观者 ?
        self.server.rcon_query(f"team join {self.teamname} {player}")

        # 记录第一局的世界生出点
        if self.x == None or self.y == None or self.z == None:
            self.x, self.y, self.z = get_pos(self.server, player)

        welcome_title = f"欢迎来到大逃杀~！"
        self.server.rcon_query(f"title {player} times 10 60 10")
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
    

    #@new_thread("speed run ready thread")
    def ready(self, player):
        # 如果已经开始游戏，跳过
        if not self.game_started:
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

    def setworldspawn(self):
        # 为第个玩家重新设置出生点

        # 这样一条指令就能设置所有玩家的出生点了～～～
        self.server.rcon_query("execute at @a run spawnpoint @a")

        # for player in self.players:
            # 这条会出现，玩家的床被阻挡。。。,然后用到世界出生点信息，效果也可以。
            # self.server.rcon_query(f"execute as @a run pawnpoint {player}")
            
            # 这样可以
            # self.server.rcon_query(f"execute at @a run pawnpoint {player}")
    
        p = random.choice(list(self.players))
        self.x, self.y, self.z = get_pos(self.server, p)
        self.server.rcon_query(f"setworldspawn {self.x} {self.y} {self.z}")
        self.server.logger.info(f"开局重设世界生出点：x:{self.x} {self.y} z:{self.z}")
    
    # 他追杀者，屏幕中间，显示，逃亡者，坐标。
    def show_running_location(self, time_=1800):
        # 这里的时间是1tick， 所以30分钟为 20*1800
        # 每局，结束时。要在显示，开始信息时，关闭。
        t = 20*time_
        self.server.rcon_query(f"title @a[tag=!running] times 1 {t} 1")
        self.server.rcon_query(f"""title @a[tag=!running] subtitle {{"text":"x:{self.running_x} y:{self.running_y} z:{self.running_z}"}}""")
        self.server.rcon_query(f"""title @a[tag=!running] title {{"text":""}}""")

    def game_start_init(self):
        # 做一些，开局前的准备; # 在每次开局前做？

        # 选出一个逃亡者
        self.player_running = random.choice(list(self.players))

        # 给逃亡者上tag, 结束时要取消掉
        self.server.rcon_query(f"tag {self.player_running} add running")

        # 清除玩家成就
        self.server.rcon_query(f"advancement revoke @a everything")

        # 清空玩家物品
        self.server.rcon_query(f"clear @a")

        # 清除玩家使用床等物品，的记录点, java 版并不行。
        # self.server.rcon_query(f"clearspawnpoint @a")

        # 清空玩家效果
        self.server.rcon_query(f"effect clear @a")

        # 清空玩家等级
        self.server.rcon_query(f"experience set @a 0 levels")
        self.server.rcon_query(f"experience set @a 0 points")

        # 玩家生命恢复
        self.server.rcon_query(f"effect give @a minecraft:instant_health 1 20 true")

        # 恢复饱食度
        self.server.rcon_query(f"effect give @a minecraft:saturation 1 20 true")

        # 设置白天
        self.server.rcon_query(f"time set day")

        # 先要扩大边界
        self.server.rcon_query(f"worldborder set 60000000")

        # 调换世界生出点
        self.x += 2000
        # spreadplayers <x> <z> <分散间距> <最大范围> [under 最大高度] <考虑队伍> <传送目标…>
        while True:
            result = self.server.rcon_query(f"spreadplayers {self.x} {self.z} 15 30 false @a")
            if re.match("Could not spread ([0-9]+) entities around (.*) \(too many entities for space - try using spread of at most ([0-9\.]+)\)", result):
                self.z += 100
            else:
                break
            time.sleep(0.1)

        # 设置世界中心和边界
        self.server.rcon_query(f"worldborder center {self.x} {self.z}")
        self.server.rcon_query(f"worldborder set 2000")
        
        # 随机拿一名玩家的位置, 设置新的世界出生点。
        self.setworldspawn()

        # 玩家死亡后立刻重生到新的地点
        # self.server.rcon_query(f"gamerule doImmediateRespawn true")
        # self.server.rcon_query(f"kill @a")
        # self.server.rcon_query(f"gamerule doImmediateRespawn false")
        
        # 开启玩家之间 PVP
        self.server.rcon_query(f"team empty {self.teamname}")

        # 
        self.server.rcon_query(f"gamemode survival @a")

        # 用 title 提示玩家游戏开始。
        self.server.rcon_query("title @a times 0 100 0")
        self.server.rcon_query("execute at @a run playsound minecraft:item.totem.use player @a")
        self.server.rcon_query("""title @a subtitle {"text":"游戏开始！", "bold": true, "color":"red"}""")
        self.server.rcon_query(f"""title @a title {{"text":"逃亡者是：{self.player_running}","bold":true, "color": "yellow"}}""")
        self.server.say(f"逃亡者是：{self.player_running}")


    #@new_thread("Speed run thread")
    @newthread
    def game_start(self, gameid):
        # 点我unready
        unready = RText("秒钟后游戏开始, 请不要中途退出。", RColor.yellow)
        unready.set_hover_text(RText("点我unready", RColor.green))
        unready.set_click_event(RAction.run_command, f"unready")

        # 10秒后游戏开始
        self.countdowning = True
        for i in range(10, 0, -1):

            # 如果有玩家 unready 取消开局
            if not self.countdowning:
                self.server.say(RText("取消开局，有玩家unready。", RColor.yellow))
                return

            self.server.say(RTextList(RText(f"{i} ", RColor.green), unready))
            time.sleep(1)

        # 开局前准备
        self.game_start_init()
        
        self.game_started = True

        # 每局开始时，第一次提示.
        first_show = True
        # testing
        sleep = 5*60
        # sleep = 30

        # 如果 逃亡者存活过30分钟，逃亡者胜利。
        for i in range(6):

            if self.gameid != gameid:
                self.server.logger.info(f"之前的游戏线程退出 gameid: {self.gameid}.")
                return

            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # 广播逃亡者位置，并高亮1分钟。
            self.running_x, self.running_y, self.running_z = get_pos(self.server, self.player_running)
            self.server.say(RTextList("逃亡者:", RText(self.player_running, RColor.yellow), "现在的位置是:", RText(f"x:{self.running_x} y:{self.running_y} z:{self.running_z} ", RColor.green), RText(f"{now}", RColor.green)))
            self.server.rcon_query(f"effect give {self.player_running} minecraft:glowing 60")

            # 向他杀者显示, 逃亡者坐标。
            if first_show:
                first_show = False
                time.sleep(5)
                self.show_running_location()
                time.sleep(sleep - 5)
            else:
                self.show_running_location()
                time.sleep(sleep)

        # 怎么结束？不好检测，玩家死亡。
        # 1. 使用 scoresbaord 记录玩家死亡数。
        # 2. 每次有玩家死亡，就拿到他的死亡记数，看看是否是逃亡者死亡。


        # 时间到，逃亡者胜利。
        self.game_end("running")


    def game_end(self, who="running"):
        self.game_started = False
        self.gameid = time.monotonic()
        # 新一局，把玩家 self.readys 清空
        self.readys = set()

        self.server.rcon_query(f"team join {self.teamname} @a")
        self.server.rcon_query(f"gamemode adventure @a")

        self.server.rcon_query("title @a times 1 100 1")
        # self.server.rcon_query("""title @a subtitle {"text":"游戏时间到！","bold":true, "color": "yellow"}""")

        # 结束提示, running: 逃亡者胜。
        if who == "running":
            # self.server.rcon_query(f"""title @a[tag=running] subtitle {{"text":"胜利！", "bold": true, "color":"red"}}""")
            self.server.rcon_query("""title @a[tag=running] title {"text":"胜利！","bold":true, "color": "yellow"}""")
            self.server.rcon_query("""title @a[tag=!running] title {"text":"失败！","bold":true, "color": "yellow"}""")
            # self.server.say(RText(f"逃亡者：{self.player_running} 胜利！", RColor.red))

            # 计算得分
            self.server.rcon_query(f"scoreboard players add @a[tag=running] score 1")

        else:
            self.server.rcon_query("""title @a[tag=!running] title {"text":"胜利！","bold":true, "color": "yellow"}""")
            self.server.rcon_query("""title @a[tag=running] title {"text":"失败！","bold":true, "color": "yellow"}""")
            # self.server.say(RText(f"逃亡者：{self.player_running} 胜利！", RColor.red))

            # 计算得分
            self.server.rcon_query(f"scoreboard players add @a[tag=!running] score 1")

        # 给逃亡者上tag, 结束时，取消掉
        self.server.rcon_query(f"tag {self.player_running} remove running")

        self.server.rcon_query("execute at @a run playsound minecraft:item.totem.use player @a")


    def player_death(self, player):
        if self.game_started and player == self.player_running:
            self.game_end("killer")

    def player_left(self, player):
        if self.game_started and player == self.player_running:
            self.game_end("killer")


def on_server_startup(server):
    server.logger.info("Speed Run Server running")
    # waitrcon(server)


def on_player_joined(server, player, info):
    global TEAM
    if TEAM == None:
        server.logger.info(f"TEAM is None 初始化.")
        TEAM = Team(server)

    TEAM.join(player)
    TEAM.init_scoreboard(player)


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

    if len(TEAM.players) >= 1 and TEAM.haveplayer(info.content):
        for death_player in TEAM.players_deathcount.keys():
            result = server.rcon_query(f"scoreboard players get {death_player} death")
            count = re.match(f"{death_player} has ([0-9]+) \[死亡记数\]", result)

            # server.logger.info(f"TEAM.players_deathcount{{}} --> {TEAM.players_deathcount}, count:{count}")

            if death_player and count:
                c = int(count.group(1))
                if TEAM.players_deathcount[death_player] != c:
                    TEAM.players_deathcount[death_player] = c
                    server.logger.info(f"检测到玩家 {death_player} 死亡, 次数为：{count.group(1)}")
                    # 检测有到玩家死亡
                    TEAM.player_death(death_player)


def on_load(server, old_plugin):
    server.register_help_message(cmdprefix, "大逃杀", PermissionLevel.USER)
    global TEAM
    TEAM = Team(server)
    server.logger.info(f"TEAM --> {TEAM} {id(TEAM)}")

    # 如果是第一次启动
    if old_plugin == None:
        pass
    else:
        # 修改重载前的，gameid.
        if hasattr(old_plugin.TEAM, "gameid"):
            old_plugin.TEAM.gameid = time.monotonic()
        # print("这玩意儿，才是执行了！")
        server.logger.info("这玩意儿，才是执行了！")

def on_remove(server, info):
    print("这玩意儿，根本没执行啊！")
    # 修改重载前的gameid
    TEAM.gameid = time.monotonic()
    server.logger.info("修改重载前的gameid")


