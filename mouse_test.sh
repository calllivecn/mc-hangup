
OLD_WIN=$(xdotool getwindowfocus)

WIN_NAME='Minecraft 1.12.2'

WIN=$(xdotool search --name "$WIN_NAME")

WW="--window $WIN"

xdotool windowfocus $WIN
sleep 0.1
xdotool key $WW Escape
sleep 0.1
xdotool click $WW --delay 100 3
sleep 0.1
xdotool key $WW t

xdotool windowfocus $OLD_WIN
exit 0



export WIN_NAME WIN WW

SCRIPT='windowfocus $WIN
key  Escape

click --delay 100  3 

key t'

TMP=$(mktemp)

echo "$SCRIPT" > $TMP

xdotool "$TMP"

rm $TMP
