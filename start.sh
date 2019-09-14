#!/bin/bash
# date 2019-04-29 15:34:02
# author calllivecn <c-all@qq.com>


min_m=${1:-1024}
max_m=${2:-2048}

java -Xms${min_m}m -Xmx${max_m}m -jar server-1.14.4.jar nogui
