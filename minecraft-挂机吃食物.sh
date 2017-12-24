
safe_exit(){
	xdotool mouseup 3
	exit 0
}

trap "safe_exit" SIGINT SIGTERM


WIN=$(xdotool search --name "Minecraft 1.12.2")
WIN=$(xdotool search --name "Minecraft 1.12")

xdotool windowfocus $WIN

xdotool key Escape

while :
do
	xdotool mousedown 3
	sleep 0.1
	xdotool mouseup 3
	sleep $[60 * 60]
done
