#!/bin/bash
# date 2018-12-11 10:27:33
# author calllivecn <c-all@qq.com>

set -e

# quote libmc.sh
. "$(dirname $0)"/libmc.sh

ctrl_space &
$delay
_mcchat_input="$(zenity --entry --text '保持 Minecraft 处于暂停界面并在此输入聊天内容：' --title 'Minecraft 中文聊天辅助工具')"
test -z "$_mcchat_input" && exit 0


$delay
xdotool key Escape
$delay
xdotool key t

#xdotool key --clearmodifiers Escape
#sleep 0.5 && xdotools key Control+space 

$delay
xdotool type --delay 150 "$_mcchat_input"
$delay
xdotool key Return
$delay


