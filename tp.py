#!/usr/bin/env python3
# coding=utf-8
# date 2021-02-05 20:18:15
# author calllivecn <c-all@qq.com>

import re
import os
import json
from pathlib import Path

from mcdreforged.api.rtext import RText, RColor, RAction
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
# 将其设为0以禁用高亮
plugin_id = PLUGIN_METADATA["id"]
cmdprefix = "." + plugin_id
config_dir = Path(os.path.dirname(os.path.dirname(__file__)), "config", plugin_id)


def process_coordinate(text):
	data = text[1:-1].replace('d', '').split(', ')
	data = [(x + 'E0').split('E') for x in data]
	return tuple([float(e[0]) * 10 ** int(e[1]) for e in data])


def process_dimension(text):
	return text.replace(re.match(r'[\w ]+: ', text).group(), '', 1)


def display(server, name, position, dimension):
	x, y, z = position
	dimension_convert = {
		'minecraft:overworld': '0',
		'minecraft:the_nether': '-1',
		'minecraft:the_end': '1',
	}
	dimension_color = {
		'0': '§2',
		'-1': '§4',
		'1': '§5'
	}
	dimension_display = {
		'0': {'translate': 'createWorld.customize.preset.overworld'},
		'-1': {'translate': 'advancements.nether.root.title'},
		'1': {'translate': 'advancements.end.root.title'}
	}
	if dimension in dimension_convert:  # convert from 1.16 format to pre 1.16 format
		dimension = dimension_convert[dimension]
	texts = [
		'',
		{
			'text': '§e{}'.format(name),
			'clickEvent':
			{
				'action': 'run_command',
				'value': '/execute at {0} run tp {0}'.format(name)
			}
		},
		'§r @ ',
		dimension_color[dimension],  # hacky fix for voxelmap yeeting text color in translated text 
		dimension_display[dimension],
		' §b[x:{}, y:{}, z:{}]§r'.format(int(x), int(y), int(z))
	]
	if dimension in ['0', '-1']:  # coordinate convertion between overworld and nether
		dimension_opposite = '-1' if dimension == '0' else '0'
		x, z = (x / 8, z / 8) if dimension == '0' else (x * 8, z * 8)
		texts.extend([
			' §7->§r ',
			dimension_color[dimension_opposite],
			dimension_display[dimension_opposite],
			' ({}, {}, {})'.format(int(x), int(y), int(z))
		])

	t = json.dumps(texts)
	serverlogger.info(f"texts ------------------>\n{t}")
	server.execute('tellraw @a {}'.format(t))

	#if HIGHLIGHT_TIME > 0:
		#server.execute('effect give {} minecraft:glowing {} 0 true'.format(name, HIGHLIGHT_TIME))


USERTP = {}

def user_tp_store_init(server):


	if not config_dir.exists():
		os.makedirs(config_dir)

	for usertp in config_dir.glob("*.json"):
		server.logger.debug(f"加载 －－－》 {usertp.stem}")
		with open(usertp) as f:
			USERTP[usertp.stem] = json.load(f)

	server.logger.info(f".tp 插件初始化 USERTP: ------>\n{USERTP}")

def player_save(player, data):
	fullpathname = config_dir / (player + ".json")
	with open(fullpathname, "w+") as f:
			json.dump(data, f, ensure_ascii=False, indent=4)

def click_text(player, label_name, x, y, z):
	r = RText(label_name, RColor.blue)
	r.set_click_event(RAction.run_command, f"/execute at {player} run tp {x} {y} {z}")
	return r


def __get(src):
	return src.get_server(), src.get_info()


def help(src):
	server, info = __get(src)

	server.tell(info.player, f"{'='*10} 使用方法 {'='*10}")
	server.logger.info(f"{USERTP}")

def ls(src, ctx):
	server, info = __get(src)

	u = USERTP.get(info.player)

	if u is None:
		server.reply(info, f"{'='*10} 当前没有收藏点, 快使用下面命令收藏一个吧。 {'='*10}")
		server.reply(info, f"{cmdprefix} add <收藏点名>")
	else:
		server.reply(info, f"{'='*10} 收藏点 {'='*10}")
		for label_name, data in u.items():
			server.reply(info, click_text(info.player, label_name, data["x"], data["y"], data["z"]))

	server.logger.debug(f"list ctx -------------->\n{ctx}")

def add(src, ctx):
	server, info = __get(src)

	# 查询世界
	rcon_result = server.rcon_query(f"data get entity {info.player} Dimension")

	if rcon_result is None:
		prompt = "rcon 没有开启, 请分别server.properties, MCDR/config.yml 开启。"
		server.logger.warning(prompt)
		server.tell(info.player, f"{cmdprefix} 插件没有配置成功，请联系服主。")

	world = re.match('{} has the following entity data: "(.*)"'.format(info.player), rcon_result).group(1)

	# 查询坐标
	rcon_result = server.rcon_query(f"data get entity {info.player} Pos")
	position = re.search(r"\[.*\]", rcon_result).group()
	x, y, z = position.strip("[]").split(",")
	x, y, z = int(x.split(".")[0]), int(y.split(".")[0]), int(z.split(".")[0])

	u = USERTP.get(info.player)
	if u is None:
		u = {}
		USERTP[info.player] = u
	elif len(u) > PLAYER_MAX_POINT:
		server.reply(info, f"收藏起点已到最大数： {PLAYER_MAX_POINT} 请删除后添加")
		return 

	label_name = ctx["label_name"]

	u[label_name] = {"world": world, "x": x, "y": y, "z":z}

	server.tell(info.player, f"地点: {label_name} 收藏成功")

	player_save(info.player, u)

	server.logger.debug(f"add ctx -------------->\n{ctx}")


def remove(src, ctx):
	server, info = __get(src)

	if USERTP.get(info.player) is None:
		server.tell(info.player, f"当前没有收藏点.")
	else:
		u = USERTP.get(info.player)
		label_name = ctx.get("label_name")

		if label_name is None:
			server.reply(info, f"没有 {label_name} 收藏点")
			return

		u.pop(label_name)

		player_save(info.player, u)

		server.reply(info, f"地点: {label_name} 删除成功")

	server.logger.debug(f"remove ctx -------------->\n{ctx}")

def rename(src, ctx):
	server, info = __get(src)

	if USERTP.get(info.player) is None:
		server.tell(info.player, f"当前没有收藏点.")
	else:
		u = USERTP.get(info.player)

		label_name = ctx["label_name"]
		label = u.get(label_name)

		if label is None:
			server.reply(info, f"没有 {label_name} 收藏点")
		else:
			v = u.pop(label_name)
			u[ctx["label_name2"]] = v

			player_save(info.player, u)


	server.logger.debug(f"rename ctx -------------->\n{ctx}")

def build_command():
	c = Literal(cmdprefix).runs(help)
	c.then(Literal("list").runs(ls))
	c.then(Literal("add").then(QuotableText("label_name").runs(add)))
	c.then(Literal("remove").then(Text("label_name").runs(remove)))
	c.then(Literal("rename").then(Text("label_name").then(Text("label_name2").runs(rename))))
	return c


def on_load(server, old_plugin):
	server.logger.debug(f"{plugin_id}: 的配置目录： {config_dir}")

	user_tp_store_init(server)

	server.register_help_message(cmdprefix, '玩家收藏点，和传玩家到收藏点.')
	server.register_command(build_command())

