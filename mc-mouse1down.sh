#!/bin/bash

set -e

safe_exit(){

	xdotool mouseup 1
	echo safe_exit
	exit 0

}
trap safe_exit SIGINT

# quote libmc.sh
. "$(dirname ${0})"/libmc.sh

$delay
xdotool key Escape 
$delay
xdotool mousedown 1
