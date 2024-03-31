#!/usr/bin/env python3
# coding=utf-8
# date 2023-04-24 00:49:12
# author calllivecn <calllivecn@outlook.com>

template="""\
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={{Inventory:[{{Slot:{0}b, id:"minecraft:totem_of_undying"}}]}}] run tag @s add zxmc.totem_find_{0}
execute at @s if entity @s[tag=zxmc.totem_find_{0}] run item replace entity @s weapon.offhand from entity @s container.{0}
execute at @s if entity @s[tag=zxmc.totem_find_{0}] run item replace entity @s container.{0} with minecraft:air
execute at @s if entity @s[tag=zxmc.totem_find_{0}] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_{0}] run tag @s remove zxmc.totem_find_{0}
"""


for i in range(35):
	print("# ", "="*20, f"第{i}个槽位", "="*20)
	new = template.format(i)
	print(new)
