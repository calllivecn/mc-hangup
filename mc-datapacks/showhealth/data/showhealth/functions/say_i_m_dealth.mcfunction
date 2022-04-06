# 先给所有活着的玩家打上标签
tag @a add Im_dealth

# 为活着的玩家reset Im_dealth
tag @e[type=player,tag=Im_dealth] add Im_dealth_say
# 这样也可以
#execute as @e[type=player,tag=Im_dealth] at @s run scoreboard players set @s Im_death 0

# 为所有活着的玩家移除，留下死亡的玩家标签。
tag @e[type=player,tag=Im_dealth] remove Im_dealth

# 选择所有死亡玩家，说 me 死了
execute as @a[tag=Im_dealth, tag=Im_dealth_say] at @s run me 死了 
tag @a[tag=Im_dealth, tag=Im_dealth_say] remove Im_dealth_say
# 这样也可以
#execute as @a[tag=Im_dealth, scores={Im_death=0}] at @s run me 死了 
#execute as @a[tag=Im_dealth, scores={Im_death=0}] at @s run scoreboard players set @s Im_death 1

