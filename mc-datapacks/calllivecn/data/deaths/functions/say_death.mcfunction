# 新版(1.20.2) return 语句这样使用是成功的。
execute as @a[nbt={Health:0.0f},tag=!im_death] at @s run function deaths:say_death_step2

execute as @a[nbt=!{Health:0.0f},tag=im_death] at @s run function deaths:say_death_step3



# 保证只说一次，然后移除 i_say_death
# tag @a[tag=im_death,tag=!i_say_death,nbt={Health:0.0f}] add i_say_death


# 然后玩家复活后，需要及时去掉 标签
# tag @a[tag=im_death,tag=i_say_death,nbt=!{Health:0.0f}] remove i_say_death
# tag @a[tag=im_death,nbt=!{Health:0.0f}] remove im_death



# 其他测试语句

# 检测玩家背包中有没有指定物品
#execute as @a[tag=im_death] at @s[nbt={Inventory:[{id:"minecraft:totem_of_undying"}]}] run say 是不死图腾
