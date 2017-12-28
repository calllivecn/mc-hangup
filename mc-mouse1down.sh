#!/bin/sh



safe_exit(){

	xdotool mouseup 1
	echo safe_exit
	exit 0

}
trap safe_exit SIGINT

delay='xdotool sleep 0.1'

MC_NAME='Minecraft 1.12.2'

WIN=$(xdotool search --name "$MC_NAME")
if test -z $WIN;then
	echo not found $MC_NAME
	exit 1
fi

$delay
xdotool windowfocus $WIN
$delay
xdotool key Escape 
$delay
xdotool mousedown 1
