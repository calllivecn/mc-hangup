
# 在使用前需要先配置玩家名称, 使用/function fishing:start
# /data modify storage fishing:player name set value calllivecn
# /execute store result storage fishing:player uuid3 int 1 run scoreboard players get @s uuid3

schedule function fishing:fishing 2t

#say tick有执行

execute as @a[nbt={SelectedItem:{id:"minecraft:fishing_rod"}}] run execute store result score @s uuid3 run data get entity @s UUID[3]

# 把玩家附近最近且未绑定的 bobber（距离 3 区块内）当作它的 bobber
# 把玩家的 uuid3 复制到那个 bobber 的 uuid3 上，并给 bobber 加个标记防止重复
execute as @a[nbt={SelectedItem:{id:"minecraft:fishing_rod"}}] at @s run scoreboard players operation @e[type=minecraft:fishing_bobber,limit=1,sort=nearest,tag=!owned,distance=..3] uuid3 = @s uuid3
execute as @a[nbt={SelectedItem:{id:"minecraft:fishing_rod"}}] at @s run tag @e[type=minecraft:fishing_bobber,limit=1,sort=nearest,tag=!owned,distance=..3] add owned

# 运行在 bobber 上下文：对于每个已绑定的 bobber，寻找拥有相同 uuid3 的玩家并以该玩家执行命令(在我这里已经移动到level1fishing)
#execute as @e[type=minecraft:fishing_bobber,tag=owned] at @s run execute as @a if score @s uuid3 = @e[type=minecraft:fishing_bobber,limit=1,sort=nearest,tag=owned] uuid3 run function fishlink:owner_action


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

# 浮标离开水面时，不需要移除 tag fishing。每次丢出的鱼钩都一个新的实体。
#execute as @e[type=minecraft:fishing_bobber,tag=fishing] at @s if block ~ ~ ~ minecraft:water if block ~ ~1 ~ minecraft:water run tag @s remove fishing

