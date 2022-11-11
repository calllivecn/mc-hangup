

# 给逃亡者上tag, 结束时要取消掉
#tag @r add running
tag @a[tag=!running] add killer

# 清除玩家成就
# advancement revoke @a everything

# 清空玩家物品
clear @a

# 清除玩家使用床等物品，的记录点, java 版并不行。
#clearspawnpoint @a

# 清空玩家效果
effect clear @a

# 清空玩家等级
experience set @a 0 levels
experience set @a 0 points

# 玩家生命恢复
effect give @a minecraft:instant_health 1 20 true
effect give @a minecraft:instant_health 1 4 true

# 恢复饱食度
effect give @a minecraft:saturation 1 20 true

# 设置白天
time set day

# 先要扩大边界                             29999984 , worldborder 需要小于三千万
worldborder set 29999984
# self.server.say("先扩大世界边界")

