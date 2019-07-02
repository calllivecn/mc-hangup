#!/bin/bash
# date 2019-07-02 16:14:39
# author calllivecn <c-all@qq.com>


if [ -d ~/bin ];then
	:
else
	mkdir ~/bin/
fi


for f in *.sh *.py mc.cfg;
do
	install -m755 "$f" ~/bin/"$f"
done
