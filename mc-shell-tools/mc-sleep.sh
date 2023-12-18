#!/bin/bash
#
# 每30分钟吃一次食物

set -e

safe_exit(){

	#xdotool mouseup 1
	xdotool mouseup 3
	exit 0
}

trap safe_exit SIGINT SIGTERM

# quote libmc.sh
. "$(dirname ${0})"/libmc.sh


food=${1:-4}
MINUTE=${2:-30}

echo
echo "默认使用物品栏第:4格为食物"
echo
echo "当前使用物品栏第:${food}格为食物"
echo
echo "请保证食物充足"
echo
echo "默认每过30分钟吃一次食物"
echo
echo "当前每过${MINUTE}分钟吃一次食"
echo

while :
do

	for i in {0..360}
	do
		xdotool sleep 5
		xdotool mousemove_relative 0 2000
		xdotool click 3

	done

	xdotool mousedown 3
	xdotool sleep 3
	xdotool mouseup 3

done
