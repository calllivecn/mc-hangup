

#execute as @a at @s run data get entity @e[type=!player,sort=nearest,limit=1]

execute as @a at @s run data get entity @e[type=minecraft:fishing_bobber,sort=nearest,limit=1]


schedule function test:autofishing 10t