#!/bin/bash
# date 2023-06-13 20:09:48
# author calllivecn <c-all@qq.com>

DEST_USER="rsync_backup"
DEST_PW="rsync.secrets"

DEST_HOST="10.1.2.1"
DEST_PORT=1873


EXCLUDE="--exclude server/dynmap"

#rsync -avHz $EXCLUDE --delete --progress -c --password-file="$DEST_PW" rsync://${DEST_USER}@${DEST_HOST}:${DEST_PORT}/mnt/data1/mc18 .

# v3.1.x 还不支持 --compress-choice=zstd
#rsync -avH --compress --compress-choice=zstd $EXCLUDE --delete --progress -c --password-file="$DEST_PW" rsync://${DEST_USER}@${DEST_HOST}:${DEST_PORT}/mc18/ .


rsync -avH --compress $EXCLUDE --delete --progress -c --password-file="$DEST_PW" rsync://${DEST_USER}@${DEST_HOST}:${DEST_PORT}/mc18 mc18/
