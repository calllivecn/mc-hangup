
execute as @a at @s store result score @s show_health as @e[distance=..10,sort=nearest,limit=1,nbt={DeathTime:0s},type=!armor_stand,type=!minecraft:player] run data get entity @s Health

execute as @a at @s store result score @s total_health as @e[distance=..10,sort=nearest,limit=1,nbt={DeathTime:0s},type=!armor_stand,type=!minecraft:player] run attribute @s minecraft:generic.max_health base get

execute as @a at @s if entity @e[distance=..10,sort=nearest,limit=1,nbt={DeathTime:0s},type=!armor_stand,type=!minecraft:player] run title @s actionbar [{"selector":"@e[distance=..10,sort=nearest,limit=1,nbt={DeathTime:0s},type=!armor_stand,type=!minecraft:player]}"},{"text":"血量:","bold":true,"color":"gold"},{"score":{"name":"@s","objective":"show_health"}},{"text": "/"},{"score":{"name":"@s","objective":"total_health"}}]

execute as @a at @s unless entity @e[distance=..10,sort=nearest,limit=1,nbt={DeathTime:0s},type=!armor_stand,type=!minecraft:player] run scoreboard players reset @s show_health
execute as @a at @s unless entity @e[distance=..10,sort=nearest,limit=1,nbt={DeathTime:0s},type=!armor_stand,type=!minecraft:player] run scoreboard players reset @s total_health

schedule function showhealth:showhealth 1s
