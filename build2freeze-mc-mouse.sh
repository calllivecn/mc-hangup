#!/bin/bash
# date 2019-10-12 11:03:45
# author calllivecn <c-all@qq.com>


TMP="mc-mouse"

safe_exit(){
	echo "clear tmp directory"
	rm -rv "$TMP"
}

download(){
	pushd "$TMP"
	wget "$1"
	popd
}

mkdir "$TMP"

set -e

trap "safe_exit" SIGTERM SIGINT EXIT


cp mc-mouse.py "$TMP/mcmouse.py"

download https://github.com/calllivecn/keyboardmouse/raw/master/libkbm.py
download https://github.com/calllivecn/keyboardmouse/raw/master/logs.py

python3 -m zipapp "$TMP" -o mc-mouse.pyz -m "mcmouse:main"

