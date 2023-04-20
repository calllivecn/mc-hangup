
# 测试ok
#me 我就是身上有图腾，但是没拿到副手的。

# 首先如果副手上有东西需要先迁移走, 不然副手上的东西就消失了。

# 把身上的图腾移动到副手上。
clear @s minecraft:totem_of_undying 1
item replace entity @s weapon.offhand with minecraft:totem_of_undying 1

# 这样的话玩家没有死亡，这里也就检测不到了。
#execute as @a[tag=im_death] at @s[nbt={Inventory:[{Slot:-106b,id:"minecraft:totem_of_undying"}]}] run say 是不死图腾

# 检测玩家背包中有没有指定物品
#execute as @a[tag=im_death] at @s[nbt={Inventory:[{id:"minecraft:totem_of_undying"}]}] run say 是不死图腾

