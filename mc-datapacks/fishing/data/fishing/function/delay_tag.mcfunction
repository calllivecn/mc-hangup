# 这样不行，知道为什么。
me 已打tag
execute as @e[type=minecraft:fishing_bobber,tag=!fishing] at @s if block ~ ~ ~ minecraft:water if block ~ ~1 ~ minecraft:air run tag @s add fishing
