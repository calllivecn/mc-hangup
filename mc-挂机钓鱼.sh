#!/bin/bash


safe_exit(){

	xdotool mouseup 3
	exit 0

}

trap safe_exit SIGINT

MC_NAME='Minecraft 1.12.2'

WIN=$(xdotool search --name "$MC_NAME")
if test -z "$WIN";then
	echo not found $MC_NAME
	exit 1
fi

fishingRod=${1:-1}
food=${2:-2}

if echo "$fishingRod" | grep -qE '[1-9]' && echo "$food" |grep -qE '[1-9]';then
	:
else
	echo "钓鱼杆的食物必须是物品栏上的一个位置：1~9 之间。"
	echo "例子：${0##*/} 6 4"
	exit 1
fi

echo "默认使用物品栏第:${fishingRod}格为钓鱼杆"
echo "默认使用物品栏第:${food}格为食物"
echo
echo "当前使用物品栏第:${fishingRod}格为钓鱼杆"
echo "当前使用物品栏第:${food}格为食物"


delay='xdotool sleep 0.1'

eat(){

	$delay
	xdotool key "$food"

	$delay
	xdotool mousedown 3
	xdotool sleep 3
	xdotool mouseup 3

	$delay
	xdotool key "$fishingRod"
}


down_up3(){
	$delay
	xdotool key "$fishingRod"
	$delay
	xdotool mousedown 3
	xdotool sleep $[60 * 40]
	xdotool mouseup 3
}


xdotool windowfocus $WIN
$delay
xdotool key Escape
$delay
xdotool key "$fishingRod"

while :
do
	down_up3
	eat
done

