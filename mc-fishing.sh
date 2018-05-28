#!/bin/bash


safe_exit(){

	xdotool mouseup 3
	exit 0

}

trap safe_exit SIGINT

# quote libmc.sh
program=$(dirname ${0})
. "$program"/libmc.sh

fishingRod=${1:-1}
food=${2:-2}

usage(){
	echo "钓鱼杆的食物必须是物品栏上的一个位置：1~9 之间。"
	echo "例子：${0##*/} 6 4"
	exit 1
}

if echo "$fishingRod" | grep -qE '[1-9]' && echo "$food" |grep -qE '[1-9]';then
	:
else
	usage
fi

echo "默认使用物品栏第:1格为钓鱼杆"
echo "默认使用物品栏第:2格为食物"
echo
echo "当前使用物品栏第:${fishingRod}格为钓鱼杆"
echo "当前使用物品栏第:${food}格为食物"

down_up3(){
	$delay
	xdotool key "$fishingRod"
	$delay
	xdotool mousedown 3
	xdotool sleep $[60 * 40]
	xdotool mouseup 3
}

if [ "$1"x = "-h" ] || [ "$1"x = "--help"x ];then
	usage
fi


xdotool windowfocus $WIN
$delay
xdotool key Escape
$delay
xdotool key "$fishingRod"

while :
do
	down_up3
    $delay
    xdotool key ${food}
    $delay
    xdotool mousedown 3
    xdotool sleep 3
	xdotool mouseup 3
done

