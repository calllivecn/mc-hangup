# 在每个实体头上2格生成 area_effect_cloud 
#execute as @e[type=!minecraft:player,type=!minecraft:armor_stand] run summon minecraft:area_effect_cloud ~ ~1 ~2 {Tags:["zxmc.showhealth"],CustomNameVisible:1b,Duration:2}


#execute as @s run summon minecraft:area_effect_cloud ~ ~1 ~10 {Tags:["zxmc.showhealth"], CustomName:'{"text":"成功了"}', CustomNameVisible:1b, Duration:20, Age:5, Radius:0}
execute as @s at @s run summon minecraft:area_effect_cloud ^ ^1 ^5 {Tags:["zxmc.showhealth"], CustomName:'{"text":"成功了","color":"white"}', CustomNameVisible:1b, Duration:20, Age:5, Radius:0}
#execute as @s at @s run summon minecraft:area_effect_cloud ^ ^1 ^5 {Tags:["zxmc.showhealth"], CustomName:'{"text":"成功了","color":"white"}', CustomNameVisible:1b, Duration:20, Radius:0}


#data modify entity @e[type=minecraft:area_effect_cloud,tag=zxmc.showhealth,sort=nearest, limit=1] CustomName set value "{"text":"这是成功了"}"
#这种不行
#data modify entity @e[type=minecraft:area_effect_cloud,tag=zxmc.showhealth,sort=nearest, limit=1] CustomName set value "[{"selector":"@e[distance=..10,sort=nearest,limit=1,nbt={DeathTime:0s},type=!armor_stand,type=!minecraft:player]}"},{"text":"血量:","bold":true,"color":"gold"},{"score":{"name":"@s","objective":"show_health"}},{"text": "/"},{"score":{"name":"@s","objective":"total_health"}}]

data modify storage zxmc:test show set from entity @e[type=minecraft:area_effect_cloud,tag=zxmc.showhealth,limit=1]
