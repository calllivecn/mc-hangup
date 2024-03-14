#!/bin/bash
# date 2023-06-13 20:09:48
# author calllivecn <c-all@qq.com>


EXCLUDE="--exclude server/dynmap/ --exclude server/world/"
EXCLUDE="--exclude server/dynmap/" 


DEST_HOST="tenw"
MC_WORLD="/mnt/data1/mc18"
check_time_file="$MC_WORLD/server/whitelist.json"

LOCAL_TIMESTAMP=".timestamp"
if [ ! -f "$LOCAL_TIMESTAMP" ];then
	echo 0 > "$LOCAL_TIMESTAMP"
fi



check_timestamp(){
	# 当前时间缀比远程旧，返回 return 0, else return 1

	local check_time_file="$1"
	local datetime timestamp local_timestamp 
	datetime=$(ssh "$DEST_HOST" stat "$check_time_file" |grep -o -P '(?<=Access: )([0-9]{4}\-[0-9]{2}\-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})')

	timestamp=$(date +%s --date="$datetime")

	read local_timestamp < "$LOCAL_TIMESTAMP"

	if [ "$local_timestamp" -lt "$timestamp" ];then
		return 0
	else
		return 1
	fi
}


# if check_timestamp;then
# 	echo "检测完，需要更新。。。"
# else
# 	echo "检测完，不需要更新。。。"
# fi

rsync -avHz $EXCLUDE --delete --progress -c ${DEST_HOST}:/mnt/data1/mc18 .
#rsync -avHz $EXCLUDE --delete --progress -c ${DEST_HOST}:/mnt/data1/mc120 .
rsync -avHz $EXCLUDE --delete --progress -c ${DEST_HOST}:/mnt/data1/mc120-极限 .

