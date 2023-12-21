# 这里是检测到有玩家钓鱼，的分支处理。

# execute as @s run me Debug: level1_fishing1: 检测上钩。

# 在多添加几个数值检测。Motion的。
# 初妈化 scoreboard objectives add fishX dummy
scoreboard objectives add fishing.fish dummy
scoreboard objectives add fishing.fishX dummy
scoreboard objectives add fishing.fishY dummy
scoreboard objectives add fishing.fishZ dummy


# 拿到 fishX fishY fishZ
execute as @s at @s run execute store result score @s fishing.fishX run data get entity @e[type=minecraft:fishing_bobber,distance=..30,sort=nearest,limit=1] Motion[0] 10
execute as @s at @s run execute store result score @s fishing.fishY run data get entity @e[type=minecraft:fishing_bobber,distance=..30,sort=nearest,limit=1] Motion[1] 10
execute as @s at @s run execute store result score @s fishing.fishZ run data get entity @e[type=minecraft:fishing_bobber,distance=..30,sort=nearest,limit=1] Motion[2] 10



# 这样ok
#execute as @a[nbt={SelectedItem:{id:"minecraft:fishing_rod"}}] at @e[type=minecraft:fishing_bobber,limit=1] positioned ~ ~ ~ if block ~ ~ ~ minecraft:water run me 我到水面了


# 这样ok, 上面的升级版。
# 鱼钩到水面后平稳后(移动范围小于0.2), 打上平稳(fishing.bobber)标签
execute as @s[tag=!fishing.bobber,scores={fishing.fishX=..2,fishing.fishY=..2,fishing.fishZ=..2}] at @e[type=minecraft:fishing_bobber,distance=..30,sort=nearest,limit=1] positioned ~ ~ ~ if block ~ ~ ~ minecraft:water run function fishing:level2_fishing_ok_tag


# 鱼钩到水面平稳后，处理有没有鱼上钩。
execute as @s[tag=fishing.bobber] at @s if entity @e[type=minecraft:fishing_bobber,distance=..30,sort=nearest,limit=1] run function fishing:level2_fishing_ok


# 清理
scoreboard objectives remove fishing.fish
scoreboard objectives remove fishing.fishX
scoreboard objectives remove fishing.fishY
scoreboard objectives remove fishing.fishZ

