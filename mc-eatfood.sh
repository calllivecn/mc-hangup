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
program=$(dirname ${0})
. "$program"/libmc.sh


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

	eat
	reconveryFocus

	for i in {0..29}
	do
		echo "还有$[ 30 - ${i}]分钟进食"
		xdotool sleep 60

	done
	


done
