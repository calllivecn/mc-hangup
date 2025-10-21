
# 在单独的文件里初始化
#scoreboard objectives add fishing.fishX dummy
#scoreboard objectives add fishing.fishY dummy
#scoreboard objectives add fishing.fishZ dummy

# 检测是否有鱼上钩
execute as @s at @s run execute store result score @s fishing.fishX run data get entity @s Motion[0] 100
execute as @s at @s run execute store result score @s fishing.fishY run data get entity @s Motion[1] 100
execute as @s at @s run execute store result score @s fishing.fishZ run data get entity @s Motion[2] 100

# 临时调试：输出分数
#execute as @s at @s run say "FishX: " + @s.fishing.fishX
#execute as @s at @s run say "FishY: " + @s.fishing.fishY
#execute as @s at @s run say "FishZ: " + @s.fishing.fishZ

# 有鱼上钩, 收杆
execute as @e[scores={fishing.fishX=-10..10,fishing.fishY=-10..10,fishing.fishZ=-10..10}] at @s run tag @s add fishing

