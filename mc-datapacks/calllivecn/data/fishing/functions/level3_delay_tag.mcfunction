
execute as @a[tag=fishing.bobber] at @s if entity @e[type=minecraft:fishing_bobber,distance=..30,sort=nearest,limit=1] run tag @s add fishing.delay

execute as @a[tag=fishing.bobber] at @s if entity @e[type=minecraft:fishing_bobber,distance=..30,sort=nearest,limit=1] run tell @s Debug: 打上延迟标签
