# 先为所有死亡的玩家打上标签
#execute as @a run tag @s[type=player,nbt={DeathTime:0s}] add live
tag @a[nbt={Health:0.0f}] add im_death


execute as @a[tag=im_death,tag=!i_say_death] at @s run me 死了

# 尝试看看能不能，拿到身上物品(-106b 是检测副手，可以检测到。哈哈), nbt={SelectedItem:{id:""}} 检测主手
#execute as @a[tag=im_death] at @s[nbt={Inventory:[{Slot:-106b}]}] run say 有物品

# 检测玩家背包中有没有指定物品
#execute as @a[tag=im_death] at @s[nbt={Inventory:[{id:"minecraft:totem_of_undying"}]}] run say 是不死图腾


# 保证只说一次，然后移除 i_say_death
tag @a[tag=im_death,tag=!i_say_death,nbt={Health:0.0f}] add i_say_death


# 然后玩家复活后，需要及时去掉 标签
tag @a[tag=im_death,tag=i_say_death,nbt=!{Health:0.0f}] remove i_say_death
tag @a[tag=im_death,nbt=!{Health:0.0f}] remove im_death

