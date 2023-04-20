# 添加数
scoreboard objectives add zxmc.totem trigger
execute as @a run scoreboard players set @s zxmc.totem 0

# 为所有玩家启用, 并且每次玩家启用过后，者要在次 enable
execute as @a run scoreboard players enable @s zxmc.totem

