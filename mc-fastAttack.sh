#!/bin/bash
# date 2019-08-12 10:57:16
# author calllivecn <c-all@qq.com>






fastattack(){

	for i in {2..9}
	do
		xdotool key "$i"
		xdotool click 1
		echo xdotool key "$i" >> /tmp/valid
	done

}


sleep 1

time {
	fastattack
}
