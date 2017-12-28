#!/bin/sh


safe_exit(){

	xdotool mouseup 3
	exit 0

}

trap safe_exit SIGINT

WID=$(xdotool search --name 'Minecraft 1.12.2')

fishingRod="${1:-1}"
food="${2:-2}"

echo "假设钓鱼杆在物品栏第:${fishingRod}格"
echo  "假设食物在物品栏第:${food}格"

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


xdotool windowfocus $WID
$delay
xdotool key Escape
$delay
xdotool key "$fishingRod"

while :
do
	down_up3
	eat
done

