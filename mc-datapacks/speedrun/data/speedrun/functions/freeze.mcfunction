# 初始化时，地图加载很慢，需要 把玩家固定在原地一段时间。

#say "有执行"

# 需要先拿到玩家坐标
teleport @a[tag=freeze] @e[type=minecraft:armor_stand,tag=armor_stand_freeze_23jl,limit=1]

# 固定玩家头向下
execute as @a[tag=freeze] at @s run teleport @s ~ ~ ~ -90 90

#execute as @a[tag=freeze] at @s run teleport @s ~ 250 ~ -90 90
#execute as @a[tag=freeze] at @s run teleport @s @e[type=minecraft:armor_stand,nbt={CustomName:'{"text":"{"armor_name"}'}] -90 90

#execute at @a run teleport @s @s
#execute at @a run teleport @s @s facing ~ ~ ~