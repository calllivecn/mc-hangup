

# 多个玩家钓鱼会乱。。。 2023-12-21

#############
#
# 这里是检测有没有玩家在钓鱼的分支。
#
###############

# 如果有玩家在钓鱼，
execute as @a[nbt={SelectedItem:{id:"minecraft:fishing_rod"}}] at @s if entity @e[type=minecraft:fishing_bobber,distance=..30,sort=nearest,limit=1] run function fishing:level1_fishing1

# 如果没有玩家在钓鱼，清理状态
# execute as @a[nbt={SelectedItem:{id:"minecraft:fishing_rod"}}] unless entity @e[type=minecraft:fishing_bobber,limit=1] run function fishing:level1_clear

#function fishing:print with storage fishing:falldistance






