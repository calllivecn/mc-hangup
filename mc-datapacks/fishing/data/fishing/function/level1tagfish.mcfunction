
#me 有执行tag 吗？

# 在单独的文件里初始化
#scoreboard objectives add fishing.fishX dummy
#scoreboard objectives add fishing.fishY dummy
#scoreboard objectives add fishing.fishZ dummy

# 检测钓钩是否在水面，并且已经稳定。是就打上tag
execute as @s at @s run execute store result score @s fishing.fishX run data get entity @s Motion[0] 100
execute as @s at @s run execute store result score @s fishing.fishY run data get entity @s Motion[1] 100
execute as @s at @s run execute store result score @s fishing.fishZ run data get entity @s Motion[2] 100

# 打tag
execute as @e[type=minecraft:fishing_bobber,scores={fishing.fishX=-10..10,fishing.fishY=-10..10,fishing.fishZ=-10..10}] at @s run tag @s add fishing

