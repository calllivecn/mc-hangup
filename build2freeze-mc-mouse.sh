#!/bin/bash
# date 2019-10-12 11:03:45
# author calllivecn <calllivecn@outlook.com>


TMP="mc-mouse"

safe_exit(){
	echo "clear tmp directory $TMP"
	rm -r "$TMP"
}


mkdir "$TMP"

TMP="$(pwd)/$TMP"

set -e

trap "safe_exit" SIGTERM SIGINT EXIT


cp mc-mouse.py "$TMP/mcmouse.py"

if [ -n "$1" ];then
	pip3 install --no-compile --target "$TMP" git+https://github.com/calllivecn/keyboardmouse@"${1}"
else
	pip3 install --no-compile --target "$TMP" git+https://github.com/calllivecn/keyboardmouse@master
fi


# 这种有问题...
#SUBMODULE="keyboardmouse"
#
#cp "$SUBMODULE/logs.py" "$TMP/"
#
#pushd "$SUBMODULE"
#if [ -n "$1" ];then
#	git checkout origin/${1}
#	python3 setup.py install --no-compile --prefix "$TMP" 
#else
#	python3 setup.py install --no-compile --prefix "$TMP" 
#
#	# py3.7 py3.8
#	#python3 setup.py install --no-compile --target "$TMP" 
#fi
#popd

python3 -m zipapp "$TMP" -c -o mc-mouse.pyz -p "/usr/bin/env python3" -m "mcmouse:main"

