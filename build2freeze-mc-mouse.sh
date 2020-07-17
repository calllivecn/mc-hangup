#!/bin/bash
# date 2019-10-12 11:03:45
# author calllivecn <c-all@qq.com>


TMP="mc-mouse"

safe_exit(){
	echo "clear tmp directory $TMP"
	rm -r "$TMP"
}


mkdir "$TMP"

set -e

trap "safe_exit" SIGTERM SIGINT EXIT


cp mc-mouse.py "$TMP/mcmouse.py"

if [ -n "$1" ];then
	pip3 install --no-compile --target "$TMP" git+https://github.com/calllivecn/keyboardmouse@"${1}"
else
	pip3 install --no-compile --target "$TMP" git+https://github.com/calllivecn/keyboardmouse@master
fi

python3 -m zipapp "$TMP" -c -o mc-mouse.pyz -m "mcmouse:main"

