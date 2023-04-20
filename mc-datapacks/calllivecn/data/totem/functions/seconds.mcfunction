
# 为所有玩家启用, 并且每次玩家启用过后，者要在次 enable
execute as @a at @s run scoreboard players enable @s zxmc.totem

# 如果玩家的 值不在 0..1 重置为0
execute as @a unless entity @s[scores={zxmc.totem=0..1}] run scoreboard players set @s zxmc.totem 0

# 最后,1秒钟后再次调用自己
schedule function totem:seconds 1s
