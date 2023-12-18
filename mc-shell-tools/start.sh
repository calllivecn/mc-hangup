#!/bin/bash
# date 2019-04-29 15:34:02
# author calllivecn <c-all@qq.com>


check(){
	if echo "$1" |grep -qE "[0-9]+" ;then
		return 0
	else
		return 1
	fi
}

PROGRAM="${0##*/}"

MANUAL="off"

if [ $# -eq 2 ];then
	if check $1 && check $2 ;then
		MIN_M=$1
		MAX_M=$2
		MANUAL="on"
	else
		echo "Usage: ${PROGRAM} [min memory] [max memory]"
		echo "${PROGRAM} 1024 2048"
		echo "Or ${PROGRAM}"
		exit 1
	fi
fi

mem_kb=$(grep -E 'MemTotal: +([0-9]+) kB' /proc/meminfo |grep -oE '[0-9]+')

mem_mb=$[mem_kb / 1024]


if [ $MANUAL = "on" ];then
	:
elif [ $mem_mb -le 1024 ];then
	echo "内存太小，尝试以1024MB启动..."
	MIN_M=1024
	MAX_M=1024
elif [ $mem_mb -gt 1024 ] && [ $mem_mb -le 2048 ];then
	MIN_M=1024
	MAX_M=$[1024 + 512]
elif [ $mem_mb -gt 2048 ] && [ $mem_mb -le 4096 ];then
	MIN_M=$[ $mem_mb / 4]
	MAX_M=2048
elif [ $mem_mb -gt 4096 ];then
	MIN_M=$[ $mem_mb / 4]
	MAX_M=$[ $mem_mb / 2]
fi


echo "java -Xms${MIN_M}m -Xmx${MAX_M}m -jar server-1.14.4.jar nogui"
