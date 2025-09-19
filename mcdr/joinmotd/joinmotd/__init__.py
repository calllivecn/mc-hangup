# -*- coding: UTF-8 -*-

from re import match

from joinmotd.funcs import (
    CMDPREFIX,
    CONFIG_DIR,
    __get,
    RText,
    RColor,
    RAction,
    RTextList,
    Literal,
)

CMD = CMDPREFIX + 'joinmotd'


def welcome(server, player):
    msg = [
        RText("="*10 + "嗨～！" + "="*10 + "\n\n"),
        RText(f"欢迎！ {player} ！\n\n", RColor.yellow),
    ]

    r = RText(">>> 点击这里，查看可用命令 <<<", RColor.green)
    r.set_hover_text("!!help")
    r.set_click_event(RAction.run_command, f"!!help")

    msg.append(r)

    server.tell(player, RTextList(*msg))

def welcome_cmd(src, ctx):
    server, info = __get(src)
    welcome(server, info.player)

def on_player_joined(server, player, info):
    welcome(server, player)

def on_load(server, prev):

    server.register_help_message(CMD, "欢迎信息")
    server.register_command(
        Literal(CMD).runs(welcome_cmd)
    )
