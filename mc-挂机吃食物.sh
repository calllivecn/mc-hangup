#!/bin/bash
#
# 每30分钟吃一次食物

safe_exit(){

	#xdotool mouseup 1
	xdotool mouseup 3
	exit 0
}

trap safe_exit SIGINT SIGTERM

MC_NAME='Minecraft 1.12.2'

delay='xdotool sleep 0.1'


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
	notify-send "接下来的10秒钟内，不要动键盘或鼠标。"
	xdotool sleep 5
}

send(){
	notify
	getFocus

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
	notify
	getFocus
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

food=${1:-4}
MINUTE=${2:-30}

echo
echo "默认使用物品栏第:4格为食物"
echo
echo "当前使用物品栏第:${food}格为食物"
echo
echo "请保证食物充足"
echo
echo "默认每过30分钟吃一次食物"
echo
echo "当前每过${MINUTE}分钟吃一次食"
echo

while :
do

	#for i in {1..10}
	#do
	#	send
	#done
	
	eat

	xdotool sleep $[60 * 30]

done
