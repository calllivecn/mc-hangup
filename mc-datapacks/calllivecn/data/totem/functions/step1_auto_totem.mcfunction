
# 选择 启动了自动图腾功能的玩家+背包有图腾，+副手为空+副手没图腾的。
execute as @a[scores={zxmc.totem=1}] at @s[nbt={Inventory:[{id:"minecraft:totem_of_undying"}]},nbt=!{Inventory:[{Slot:-106b}]},nbt=!{Inventory:[{Slot:-106b,id:"minecraft:totem_of_undying"}]}] run function totem:step2_auto_totem


# 选择 启动了自动图腾功能的玩家+背包有图腾，+副手不为空+副手不是图腾的。
execute as @a[scores={zxmc.totem=1}] at @s[nbt={Inventory:[{id:"minecraft:totem_of_undying"}]},nbt={Inventory:[{Slot:-106b}]},nbt=!{Inventory:[{Slot:-106b,id:"minecraft:totem_of_undying"}]}] run function totem:step2_swap_item


# 尝试看看能不能，拿到身上物品(-106b 是检测副手，可以检测到。哈哈), nbt={SelectedItem:{id:""}} 检测主手
#execute as @a[tag=im_death] at @s[nbt={Inventory:[{Slot:-106b}]}] run say 有物品
# 先测试下，直接给个不死图腾
#item replace entity @a[tag=im_death,tag=!i_say_death] weapon.offhand with minecraft:totem_of_undying 1

# 这样的话玩家没有死亡，这里也就检测不到了。
#execute as @a[tag=im_death] at @s[nbt={Inventory:[{Slot:-106b,id:"minecraft:totem_of_undying"}]}] run say 是不死图腾

# 检测玩家背包中有没有指定物品
#execute as @a[tag=im_death] at @s[nbt={Inventory:[{id:"minecraft:totem_of_undying"}]}] run say 是不死图腾


