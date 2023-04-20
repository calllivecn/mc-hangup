# 先检测，打开了zxmc.auto_totem 的玩家
execute as @a[scores={zxmc.totem=1}] run function totem:step1_auto_totem



# 使用 schedule function <self> 1s 的方法，减少调用

# 为所有玩家启用, 并且每次玩家启用过后，者要在次 enable
#execute as @a at @s run scoreboard players enable @s zxmc.totem

# 如果玩家的 值不在 0..1 重置为0
#execute as @a unless entity @s[scores={zxmc.totem=0..1}] run scoreboard players set @s zxmc.totem 0
