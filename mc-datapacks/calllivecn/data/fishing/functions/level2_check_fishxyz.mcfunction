# 拿到 fishX fishY fishZ

execute as @s run execute store result score @s fishX run data get entity @e[type=minecraft:fishing_bobber,limit=1] Motion[0] 10
execute as @s run execute store result score @s fishY run data get entity @e[type=minecraft:fishing_bobber,limit=1] Motion[1] 10
execute as @s run execute store result score @s fishZ run data get entity @e[type=minecraft:fishing_bobber,limit=1] Motion[2] 10

