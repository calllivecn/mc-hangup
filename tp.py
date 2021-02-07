#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-05 20:18:15
# author calllivecn <c-all@qq.com>

import re
import os
import json
from pathlib import Path

from mcdreforged.api.rtext import RText, RColor, RAction, RStyle, RTextList
from mcdreforged.command.builder.command_node import Literal, QuotableText, Text, GreedyText, Integer

PLUGIN_METADATA = {
	# ID（即插件ID）是您插件的身份字符串。它应该由小写字母，数字和下划线组成，长度为1到64
	'id': 'tp', 
	'version': '0.1.0',
	'name': '玩家位置点记录和传送',
	'author': [
		'calllivecn'
   ],
	'link': 'https://github.com/calllivecn/mcdr/tp.py',
	'dependencies': {
    	'mcdreforged': '>=1.0.0',
	}
}

PLAYER_MAX_POINT = 20

# set it to 0 to disable hightlight
plugin_id = PLUGIN_METADATA["id"]
cmdprefix = "." + plugin_id
config_dir = Path(os.path.dirname(os.path.dirname(__file__)), "config", plugin_id)

"""
def display(server, name, position, dimension):
	x, y, z = position
	dimension_convert = {
		'minecraft:overworld': '0',
		'minecraft:the_nether': '-1',
		'minecraft:the_end': '1',
	}
"""


USERTP = {}

def user_tp_store_init(server):

	if not config_dir.exists():
		os.makedirs(config_dir)

	for usertp in config_dir.glob("*.json"):
		server.logger.debug(f"加载 －－－》 {usertp.stem}")
		with open(usertp) as f:
			USERTP[usertp.stem] = json.load(f)

	server.logger.debug(f".tp 插件初始化 USERTP: ------>\n{USERTP}")

def player_save(player, data):
	fullpathname = config_dir / (player + ".json")
	with open(fullpathname, "w+") as f:
			json.dump(data, f, ensure_ascii=False, indent=4)

def click_text(player, label_name, world, x, y, z):
	r = RText(label_name, RColor.blue)
	r.set_hover_text(RText(f"点击传送[{x}, {y}, {z}]", RColor.green))
	# r.set_click_event(RAction.run_command, f"/execute at {player} in {world} run teleport {player} {x} {y} {z}")
	r.set_click_event(RAction.run_command, f"{cmdprefix} {label_name}")
	# r.set_click_event(RAction.run_command, f"/tell {player} {cmdprefix} {label_name}") # 等回去测试这种能不能，隐藏交互。
	return r

def click_invite(player1, player2, world):
    r = RText(f"{player1} 邀请你tp TA.", RColor.green)
    r.set_click_event(RAction.run_command, f"/execute at {player2} in {world} run teleport @s {player1}")
    return r

def __get(src):
	return src.get_server(), src.get_info()


def help(src):
	server, info = __get(src)

	msg=[f"{'='*10} 使用方法 {'='*10}",
	f"{cmdprefix}                               查看使用方法",
	f"{cmdprefix} <收藏点>                      tp 到收藏点",
	f"{cmdprefix} list                          列出所有收藏点",
	f"{cmdprefix} add <收藏点名字>              添加或修改当前位置为收藏点",
	f"{cmdprefix} remove <收藏点名字>           删除收藏点",
	f"{cmdprefix} rename <收藏点名字> <新名字>  修改收藏点名字",
	#f"{cmdprefix} invite <玩家>                 邀请玩家到你当前的位置",
	]
	server.reply(info, "\n".join(msg))

	server.logger.debug(f"{USERTP}")


def check_level(server, info):
	# 查看玩家的等级够不够
	level = server.rcon_query(f"experience query {info.player} levels")

	l = re.match(f"{info.player} has ([0-9]+) experience levels", level).group(1)

	server.logger.debug(f"玩家 {info.player} 等级： {l}")

	if int(l) < 1:
		server.reply(info, RText("经验不足，至少需要1级", RColor.red))
		return False
	else:
		# 扣掉1级
		server.rcon_query(f"experience add {info.player} -1 levels")
		return True

def ls(src, ctx):
	server, info = __get(src)

	u = USERTP.get(info.player)

	msg = [
	f"{'='*10} 当前没有收藏点, 快使用下面命令收藏一个吧。 {'='*10}",
	f"{cmdprefix} add <收藏点名>",
	]

	if u is None:
		server.reply(info, "\n".join(msg))
	else:
		msg = [RText(f"{'='*10} 收藏点 {'='*10}\n", RColor.white)]

		for label_name, data in u.items():
			msg.append(click_text(info.player, label_name, data["world"], data["x"], data["y"], data["z"]))
			msg.append("\n")

		server.reply(info, RTextList(*msg))

	server.logger.debug(f"list ctx -------------->\n{ctx}")

def teleport(src, ctx):
	server, info = __get(src)
	msg = [
	f"{'='*10} 当前没有收藏点, 快使用下面命令收藏一个吧。 {'='*10}",
	f"{cmdprefix} add <收藏点名>",
	]

	server.logger.debug(f"tp() 执行了。src --------->\n{src} ctx ------------>\n{ctx}")

	u = USERTP.get(info.player)
	if u is None:
		server.reply(info, "\n".join(msg))
	else:
		label_name = ctx.get("label_name")
		label = u.get(label_name)

		if label is None:
			server.reply(info, f"没有 {label_name} 收藏点")
		else:
			world = label["world"]
			x, y, z = label["x"], label["y"], label["z"]

			if check_level(server, info):
				server.execute(f"execute at {info.player} in {world} run teleport {info.player} {x} {y} {z}")

		server.logger.debug(f"label_name: {label_name} 收藏点：  {label}")


def add(src, ctx):
	server, info = __get(src)

	# 查询世界
	rcon_result = server.rcon_query(f"data get entity {info.player} Dimension")

	if rcon_result is None:
		prompt = RText("rcon 没有开启, 请分别server.properties, MCDR/config.yml 开启。", RColor.red)
		server.logger.warning(prompt)
		server.tell(info.player, Rtext(f"{cmdprefix} 插件没有配置成功，请联系服主。", RColor.red))

	world = re.match('{} has the following entity data: "(.*)"'.format(info.player), rcon_result).group(1)

	# 查询坐标
	rcon_result = server.rcon_query(f"data get entity {info.player} Pos")
	position = re.search(r"\[.*\]", rcon_result).group()
	x, y, z = position.strip("[]").split(",")
	x, y, z = round(float(x.strip(" d")), 1), round(float(y.strip(" d")), 1), round(float(z.strip(" d")), 1)

	u = USERTP.get(info.player)
	if u is None:
		u = {}
		USERTP[info.player] = u
	elif len(u) > PLAYER_MAX_POINT:
		server.reply(info, RText(f"收藏点已到最大数： {PLAYER_MAX_POINT} 请删除后添加", RColor.red))
		return 

	# 查看玩家的等级够不够
	if check_level(server, info):
		label_name = ctx["label_name"]

		u[label_name] = {"world": world, "x": x, "y": y, "z":z}

		server.tell(info.player, RTextList("地点: ", RText(label_name, RColor.blue), " 收藏成功"))

		player_save(info.player, u)

	server.logger.debug(f"add ctx -------------->\n{ctx}")


def remove(src, ctx):
	server, info = __get(src)

	u = USERTP.get(info.player)

	if u is None:
	    server.tell(info.player, RText(f"当前没有收藏点.", RColor.red))
	else:
		label_name = ctx.get("label_name")

		label = u.get(label_name)

		if label is None:
			server.reply(info, RTextList(RText("没有 "), RText(label_name, RColor.blue), RText(" 收藏点")))
			return

		u.pop(label_name)

		player_save(info.player, u)

		server.reply(info, RTextList("地点: ", RText(label_name, RColor.blue, RStyle.strike_through), " 删除成功"))

	server.logger.debug(f"remove ctx -------------->\n{ctx}")

def rename(src, ctx):
	server, info = __get(src)

	if USERTP.get(info.player) is None:
		server.tell(info.player, RText(f"当前没有收藏点.", RColor.red))
	else:
		u = USERTP.get(info.player)

		label_name = ctx["label_name"]
		label = u.get(label_name)

		if label is None:
			server.reply(info, RText(f"没有 {label_name} 收藏点", RColor.red))
		else:
			if check_level(server, info):
				v = u.pop(label_name)
				u[ctx["label_name2"]] = v
				player_save(info.player, u)
				server.reply(info, RText("修改名称成功"))

	server.logger.debug(f"rename ctx -------------->\n{ctx}")


def invite(src, ctx):
    server, info = __get(src)
    
    if check_level(server, info):
        pass


def build_command():
	c = Literal(cmdprefix).runs(help)
	c = c.then(QuotableText("label_name").runs(teleport))
	c.then(Literal("list").runs(ls))
	c.then(Literal("add").then(QuotableText("label_name").runs(add)))
	c.then(Literal("remove").then(QuotableText("label_name").runs(remove)))
	c.then(Literal("rename").then(QuotableText("label_name").then(QuotableText("label_name2").runs(rename))))
    #c.then(Literal("invite").then(QuotableText("player").tuns(invite)))
	return c


def on_load(server, old_plugin):
	server.logger.debug(f"{plugin_id}: 的配置目录： {config_dir}")

	#user_tp_store_init(server)

	server.register_help_message(cmdprefix, '玩家收藏点，和传玩家到收藏点.')
	server.register_command(build_command())

def on_player_joind(server, player, info):
    server.logger.info(f"加载玩家 {player} 收藏点")
    player_json = config_dir / player + ".json"
    if player_json.exists():
        with open(player_json) as f:
            USERTP[player] = json.load(f)


def on_player_left(server, player):
    server.logger.info(f"卸载玩家 {player} 收藏点"
    u = USERTP.get(player)
    if u is not None:
        USERTP.pop(player)
