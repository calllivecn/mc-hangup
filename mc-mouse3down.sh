#!/bin/sh

trap safe_exit SIGINT

WID=$(xdotool search --name 'Minecraft 1.12.2')

safe_exit(){

	xdotool mouseup 3
	exit 0

}

xdotool windowfocus $WID
xdotool sleep 0.5
xdotool key Escape 
xdotool sleep 0.5
xdotool mousedown 3
