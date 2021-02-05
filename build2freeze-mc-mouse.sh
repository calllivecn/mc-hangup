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

#if [ -n "$1" ];then
#	pip3 install --no-compile --target "$TMP" git+https://github.com.cnpmjs.org/calllivecn/keyboardmouse@"${1}"
#else
#	pip3 install --no-compile --target "$TMP" git+https://github.com.cnpmjs.org/calllivecn/keyboardmouse@master
#fi
SUBMODULE="keyboardmouse"
pushd "$SUBMODULE"
if [ -n "$1" ];then
	git checkout origin/${1}
	python3 "setup.py" install --no-compile --target "$TMP" 
else
	python3 "setup.py" install --no-compile --target "$TMP" 
fi
popd

python3 -m zipapp "$TMP" -c -o mc-mouse.pyz -p "/usr/bin/env python3" -m "mcmouse:main"

