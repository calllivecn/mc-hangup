execute as @a at @s store result score @s show_health as @e[distance=..20,sort=nearest,limit=1,nbt={DeathTime:0s},type=!armor_stand,type=!minecraft:player] run data get entity @s Health

execute as @a at @s if entity @e[distance=..20,sort=nearest,limit=1,nbt={DeathTime:0s},type=!armor_stand,type=!minecraft:player] run title @s actionbar ["",{"selector":"@e[distance=..20,sort=nearest,limit=1,nbt={DeathTime:0s},type=!armor_stand,type=!minecraft:player]}"},{"text":"血量:","bold":true,"color":"gold"},{"score":{"name":"@s","objective":"show_health"}}]

execute as @a at @s unless entity @e[distance=..20,sort=nearest,limit=1,nbt={DeathTime:0s},type=!armor_stand,type=!minecraft:player] run scoreboard players reset @s show_health
