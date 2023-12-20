# 这里是level2, 处理水面平稳后的情况。

# execute as @s run me Debug: level2_fishing_ok: 检测上钩。

# 这样也ok, 这样落到水面上时还是会有多次 检测上钩。
execute as @s at @s run execute store result score @s fish run data get entity @e[type=minecraft:fishing_bobber,distance=..30,sort=nearest,limit=1] FallDistance 10


# 这里处理，鱼上钩和没上钩的情况。
# 是不是打个tag 每次上钩只说一次. 
# 配合收竿的进度，去掉 tag fish。
execute as @s[tag=fishing_delay,scores={fish=2..}] run function fishing:level3_fishing

# execute as @s[tag=fish,scores={fish=2..}] run tag @s remove fish

