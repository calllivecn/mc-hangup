#!/bin/sh
#
# 每30分钟吃一次食物

safe_exit(){

	#xdotool mouseup 1
	xdotool mouseup 3
	exit 0
}
trap safe_exit SIGINT SIGTERM

getFocus(){
	SOURCE_WID=$(xdotool getwindowfocus)
}

reconveryFocus(){
	xdotool sleep 0.1
	xdotool key t
	xdotool sleep 0.1
	xdotool windowfocus "$SOURCE_WID"
}

getMcFocus(){
	WID=$(xdotool search --name 'Minecraft 1.12.2')
}

notify(){
	notify-send "接下来的10秒钟内，不要动键盘或鼠标。"
	xdotool sleep 5
}

send(){
	notify
	getFocus

	getMcFocus

	xdotool windowfocus $WID
	xdotool sleep 0.1
	xdotool key Escape 
	xdotool sleep 0.1

	xdotool key t
	xdotool sleep 0.1
	xdotool type --delay 150 "自动挂机中。。。"
	xdotool sleep 0.1
	xdotool key Return

	reconveryFocus

	xdotool sleep $[60 * 3]
}

eat(){
	notify
	getFocus
	getMcFocus

	xdotool windowfocus $WID
	xdotool sleep 0.1
	xdotool key Escape 
	xdotool sleep 0.1

	xdotool mousedown 3
	xdotool sleep 3
	xdotool mouseup 3

	reconveryFocus
}

while :
do

	for i in {1..10}
	do
		send
	done

	eat

done
