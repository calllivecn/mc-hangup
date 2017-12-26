#!/bin/sh

trap safe_exit SIGINT

WID=$(xdotool search --name 'Minecraft 1.12.2')

safe_exit(){

	xdotool mouseup 1
	exit 0

}

xdotool windowfocus $WID
sleep 0.5
xdotool key Escape 
sleep 0.5
xdotool mousedown 1
