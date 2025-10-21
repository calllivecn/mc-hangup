
# 检测是否有鱼上钩

execute store result score @s fishing.fishY run data get entity @s Motion[1] 100

# 有鱼上钩, 收杆
execute as @s[scores={fishing.fishY=..-10}] at @s run function fishing:player with storage fishing:player


