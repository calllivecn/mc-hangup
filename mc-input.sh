#!/bin/bash


set -e
which zenity &>/dev/null || (echo '错误：zenity 程序未安装。' >&2; exit 2)


# quote libmc.sh
program=$(dirname ${0})
. "$program"/libmc.sh

ctrl_space &
$delay
_mcchat_input="$(zenity --entry --text '保持 Minecraft 处于暂停界面并在此输入聊天内容：' --title 'Minecraft 中文聊天辅助工具')"
test -z "$_mcchat_input" && exit 0

$delay
xdotool type --delay 150 "$_mcchat_input"
$delay
