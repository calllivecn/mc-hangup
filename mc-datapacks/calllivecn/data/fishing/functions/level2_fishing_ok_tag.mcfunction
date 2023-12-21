
execute as @s at @s if entity @e[type=minecraft:fishing_bobber,distance=..30,sort=nearest,limit=1] run tag @s add fishing.bobber

execute as @s at @s if entity @e[type=minecraft:fishing_bobber,distance=..30,sort=nearest,limit=1] run tell @s Debug: 鱼钩在水面+水面平稳


# execute 执行主体，不能传导到 schedule 高度的函数里
schedule function fishing:level3_delay_tag 20t
