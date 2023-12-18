#!/bin/bash

set -e

safe_exit(){

	xdotool mouseup 1
	enable_mouse
	echo safe_exit
	exit 0

}

trap safe_exit SIGINT SIGTERM ERR

# quote libmc.sh
. "$(dirname ${0})"/libmc.sh

disable_mouse

$delay
xdotool key Escape 
$delay
xdotool mousedown 1

while :
do
	xdotool sleep 3
done
