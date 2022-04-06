# 先给所有活着的玩家打上标签
tag @a[tag=!Im_dealth_say] add Im_dealth
tag @a[tag=!Im_dealth] add Im_dealth_say

# 为所有活着的玩家移除，留下死亡的玩家标签。
tag @e[type=player,tag=Im_dealth] remove Im_dealth

# 选择所有死亡玩家，说 me 死了
execute as @a[tag=Im_dealth,tag=Im_death_say] at @s run me 死了 

# say 一次后，去掉标签，避免重复 say。
tag @a[tag=Im_dealth,tag=Im_death_say] remove Im_death_say

