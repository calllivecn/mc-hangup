#!/bin/sh
#
# 每30分钟吃一次食物

safe_exit(){

	#xdotool mouseup 1
	xdotool mouseup 3
	exit 0
}
trap safe_exit SIGINT SIGTERM

	WID=$(xdotool search --name 'Minecraft 1.12.2')

	xdotool windowfocus $WID

	xdotool key Escape 
	sleep 1
#xdotool mousedown 1

send(){
xdotool key t
sleep 0.5
xdotool type --delay 150 "自动挂机中。。。"
sleep 0.5
xdotool key Return
sleep $[60 * 3]
}

while :
do
	xdotool mousedown 3
	sleep 5
	xdotool mouseup 3

	for i in {1..10}
	do
		send
	done

	#sleep $[60*30]
done
