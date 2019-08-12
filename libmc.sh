#!/bin/bash
# date 2018-01-01 14:58:47
# author calllivecn <c-all@qq.com>


set -e

delay='xdotool sleep 0.1'


mc_cfg="$(dirname ${0})/mc.cfg"
if [ -r "$mc_cfg" ];then
	. "$mc_cfg"
else
	echo "需要配置$mc_cfg"
	exit 1
fi

# MC_NAME='Minecraft 1.13.1'
if [ -z "${MC_NAME}" ];then
	echo "需要在 ${mc_cfg} 配置minecraft游戏窗口名称，如：Minrcraft 1.12.2"
	exit 1
fi

# MOUSE="Logitech USB Optical Mouse"
if [ -z "${MOUSE}" ];then
	echo "可以用以下方法配置启动脚本时禁用鼠标。"
	echo "xinput list --name-only 查看你想要禁用的鼠标。"
	echo "然后配置${0##*/} 中的 MOUSE 变量。"
fi

which zenity &>/dev/null || { echo '警告：zenity 程序未安装。'; }
which xdotool &>/dev/null || { echo '错误：xdotool 程序未安装。' >&2;exit 2; }

WIN=$(xdotool search --name "$MC_NAME")

if test -z "$WIN";then
	echo not found "$WIN_NAME"
	exit 1
else
	xdotool windowfocus $WIN
fi

getMcFocus(){
	WIN=$(xdotool search --name "$MC_NAME")
	if test -z $WIN;then
		echo not found $MC_NAME
		exit 1
	fi
}

focusmc(){
	local win
	win=$(xdotool getwindowfocus)

	if [ $win == $WIN ];then
		return 0
	else
		return 1
	fi
}

ctrl_space(){
	xdotool sleep 0.5
	xdotool key Ctrl+space
}


disable_mouse(){
	set +e
	xinput disable $(xinput list --id-only "$MOUSE")
	set -e
}

enable_mouse(){
	set +e
	xinput enable $(xinput list --id-only "$MOUSE")
	set -e
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
