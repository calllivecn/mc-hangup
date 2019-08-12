#!/bin/bash
# date 2019-07-02 16:14:39
# author calllivecn <c-all@qq.com>


if [ -d ~/bin ];then
	:
else
	mkdir ~/bin/
fi

if [ -f ~/bin/mc.cfg ];then
	:
else
	cp mc.cfg ~/bin/
fi

scripts="
libmc.sh
mc-chat.sh
mc-eatfood.sh
mc-fishing.sh
mc-input.sh
mc-mouse1down.sh
mc-sleep.sh
mc-Dungeon.py
"

for f in $scripts;
do
	install -m755 "$f" ~/bin/"$f"
done
