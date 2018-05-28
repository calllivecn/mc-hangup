#!/bin/bash
# date 2018-01-01 14:58:47
# author calllivecn <c-all@qq.com>


set -e

delay='xdotool sleep 0.1'

MC_NAME='Minecraft 1.12.2'

which zenity &>/dev/null || { echo '错误：zenity 程序未安装。' >&2;exit 2; }
which xdotool &>/dev/null || { echo '错误：xdotool 程序未安装。' >&2;exit 2; }

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


getFocus(){
	SOURCE_WIN=$(xdotool getwindowfocus)
	eval $(xdotool getmouselocation --shell)
}

reconveryFocus(){
	$delay
	xdotool key t
	$delay
	xdotool windowfocus "$SOURCE_WIN"
	$delay
	xdotool mousemove --screen $SCREEN $X $Y
}

getMcFocus(){
	WIN=$(xdotool search --name "$MC_NAME")
	if test -z $WIN;then
		echo not found $MC_NAME
		exit 1
	fi
}

notify(){
	#zenity --notification --text "接下来的10秒钟内，不要动键盘或鼠标。"
	notify-send "接下来的10秒钟内，不要动键盘或鼠标。"
	xdotool sleep 5
}

send(){
	getFocus

	notify

	getMcFocus

	xdotool windowfocus $WIN
	$delay
	xdotool key Escape 
	$delay

	xdotool key t
	$delay
	xdotool type --delay 150 "自动挂机中。。。"
	$delay
	xdotool key Return

	reconveryFocus

	xdotool sleep $[60 * "$MINTUE"]
}

eat(){
	getFocus
	notify
	getMcFocus

	xdotool windowfocus $WIN
	$delay
	xdotool key Escape 
	$delay
	xdotool key ${food}
	$delay
	xdotool mousedown 3
	xdotool sleep 3
	xdotool mouseup 3

	reconveryFocus
}
