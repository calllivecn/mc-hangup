#!/bin/sh

trap safe_exit SIGINT

WID=$(xdotool search --name 'Minecraft 1.12')

safe_exit(){

	xdotool mouseup 1
	exit 0

}

xdotool windowfocus $WID

xdotool key Escape 
sleep 1
xdotool mousedown 1
