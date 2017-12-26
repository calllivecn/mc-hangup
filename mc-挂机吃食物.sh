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
	sleep 0.1
	xdotool key t
	sleep 0.1
	xdotool windowfocus "$SOURCE_WID"
}

getMcFocus(){
	WID=$(xdotool search --name 'Minecraft 1.12.2')
}

notify(){
	notify-send "接下来的10秒钟内，不要动键盘或鼠标。"
	sleep 5
}

send(){
	notify
	getFocus

	getMcFocus

	xdotool windowfocus $WID
	sleep 0.1
	xdotool key Escape 
	sleep 0.1

	xdotool key t
	sleep 0.1
	xdotool type --delay 150 "自动挂机中。。。"
	sleep 0.1
	xdotool key Return

	reconveryFocus

	sleep $[60 * 3]
	#sleep 45
}

eat(){
	notify
	getFocus
	getMcFocus

	xdotool windowfocus $WID
	sleep 0.1
	xdotool key Escape 
	sleep 0.1

	xdotool mousedown 3
	sleep 3
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

	#sleep $[60*30]
done
