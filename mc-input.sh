#!/bin/bash


set -e
which zenity &>/dev/null || (echo '错误：zenity 程序未安装。' >&2; exit 2)
which xdotool &>/dev/null || (echo '错误：xdotool 程序未安装。' >&2; zenity --error --text '错误：xdotool 程序未安装' --title 'Minecraft 中文聊天辅助工具'; exit 2)

delay='xdotool sleep 0.1'

MC_NAME='Minecraft 1.12.2'

WIN=$(xdotool search --name "$MC_NAME")

if test -z "$WIN";then
	echo not found "$WIN_NAME"
	exit 1
else
	xdotool windowfocus $WIN
fi

ctrl_space(){
	xdotool sleep 0.5
	xdotool key Ctrl+space
}

ctrl_space &
$delay
_mcchat_input="$(zenity --entry --text '保持 Minecraft 处于暂停界面并在此输入聊天内容：' --title 'Minecraft 中文聊天辅助工具')"
test -z "$_mcchat_input" && exit 0

$delay
xdotool type --delay 50 "$_mcchat_input"
$delay
