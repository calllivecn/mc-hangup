

MC_WINDOWS=
if [ "$1"x = x ];then
	echo "需要窗口id, xdotool search <窗口名查找>"
	exit 1
else
	MC_WINDOWS="$1"
fi

echo "3秒后开始"
sleep 3


# 配合检测器+发射器自动种+自动收菜。
autotool(){
	xdotool click --window $MC_WINDOWS 3
	sleep 0.8
	xdotool click --window $MC_WINDOWS 1
	sleep 0.1
}


while :
do
	autotool
done
