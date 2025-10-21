
# 在使用前需要先配置玩家名称
# /data modify storage fishing:player name set value calllivecn

schedule function fishing:fishing 2t

#say 有执行

# 刚到水面时，需要等待浮标稳定后在打tag
execute as @e[type=minecraft:fishing_bobber,tag=!fishing] at @s if block ~ ~ ~ minecraft:water if block ~ ~1 ~ minecraft:air run function fishing:level1tagfish

# debug
#execute as @e[type=minecraft:fishing_bobber,tag=!fishing] at @s if block ~ ~ ~ minecraft:water if block ~ ~1 ~ minecraft:air run me 我在我在
#execute as @e[type=minecraft:fishing_bobber,tag=!fishing] store result storage autofish:player motion0 float 1 run data get entity @s Motion[0] 100
#execute as @e[type=minecraft:fishing_bobber,tag=!fishing] store result storage autofish:player motion1 float 1 run data get entity @s Motion[1] 100
#execute as @e[type=minecraft:fishing_bobber,tag=!fishing] store result storage autofish:player motion2 float 1 run data get entity @s Motion[2] 100
#function fishing:test with storage autofish:player

# 这个可以(1.21.10)
#execute as @e[type=minecraft:fishing_bobber,tag=fishing] at @s if block ~ ~ ~ minecraft:water if block ~ ~1 ~ minecraft:water run tell @e[type=minecraft:player,sort=nearest,limit=1] 上钩了

execute as @e[type=minecraft:fishing_bobber,tag=fishing] at @s if block ~ ~ ~ minecraft:water if block ~ ~1 ~ minecraft:air run function fishing:level1fishing

# carpet 模组命令
#execute as @e[type=minecraft:fishing_bobber,tag=fishing] at @s if block ~ ~ ~ minecraft:water if block ~ ~1 ~ minecraft:water run execute as @e[type=minecraft:player,sort=nearest,limit=1] run function fishing:player with storage autofish:player

#execute as @e[type=minecraft:fishing_bobber,tag=fishing] at @s if block ~ ~ ~ minecraft:water if block ~ ~1 ~ minecraft:water run tag @s remove fishing

