#!/bin/sh
#
# 每30分钟吃一次食物

safe_exit(){

	#xdotool mouseup 1
	xdotool mouseup 3
	exit 0
}
trap safe_exit SIGINT

WID=$(xdotool search --name 'Minecraft 1.12.2')

xdotool windowfocus $WID

xdotool key Escape 
sleep 1
#xdotool mousedown 1

while :
do
	sleep $[60*30]
	xdotool mousedown 3
	sleep 5
	xdotool mouseup 3
done
