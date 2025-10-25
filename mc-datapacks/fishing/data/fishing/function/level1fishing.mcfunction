#me 检测finshY

# 检测是否有鱼上钩
execute store result score @s fishing.fishY run data get entity @s Motion[1] 100

# 有鱼上钩, 收杆
#execute as @s[scores={fishing.fishY=..-10}] at @s run function fishing:player with storage fishing:player

# 有鱼上钩, 收杆。最近的玩家才收杆。
#execute as @s[scores={fishing.fishY=..-10}] at @s run execute as @e[type=minecraft:player,distance=..20,sort=nearest,limit=1] at @s run function fishing:player with storage fishing:player

execute as @s[scores={fishing.fishY=..-10},tag=fishing,tag=owned] at @s run execute as @a[nbt={SelectedItem:{id:"minecraft:fishing_rod"}}] if score @s uuid3 = @e[type=minecraft:fishing_bobber,tag=fishing,tag=owned,sort=nearest,limit=1] uuid3 run function fishing:player with storage fishing:player


