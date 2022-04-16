# 
tag @a remove freeze

worldborder set 2000

kill @e[type=minecraft:armor_stand,tag=armor_stand_freeze_23jl]

execute at @a run spawnpoint @a

execute at @r run setworldspawn ~ ~ ~

team empty SpeedRun

gamemode survival @a

# 设置白天
time set day

title @a times 1 100 1
title @a subtitle ["",{"text":"逃亡者是：","bold":true,"color":"gold"},{"selector":"@a[tag=running]}"}] 
title @a title {"text":"游戏开始！","bold":true, "color": "yellow"}
tellraw @a ["",{"text":"逃亡者是：","bold":true,"color":"gold"},{"selector":"@a[tag=running]}"}]