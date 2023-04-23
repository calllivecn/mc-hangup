# 这里功能是在前面，玩家背包里有不死图腾，副手上其他物品的情况下执行。（另外副手没有物品的情况在另外的文件实现）
# 试着实现 在玩家背包里交换物品位置
# 思路
# 0. 生成一个盔甲架，用来临时放玩家副手上有的东西（如果有的话）
# 1. 然后一个个背包位置测试，试到不死图腾。
# 2. 然后用item 把这个位置不死图腾换到副手 + 然后把临时盔甲架的东西换到这个位置，清理临时盔甲架。
#   1. 这里需要在细的实现。在这个位置找到图腾后，需要打上对就位置名的标签？
#   2. 并打上已经找到的标签（zxmc.totem_find_X）X 是槽位号

# execute at @s run say “execute as @s 可以？测试是可以的”

execute at @s run summon minecraft:armor_stand ~ ~ ~ {Tags:["zxmc.totem"],Invisible:1b,NoGravity:1b,Invulnerable:1b,Small:1b,DisabledSlots:256}

# 把玩家副手的物品，换到盔甲上
execute at @s if entity @s run item replace entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand from entity @s weapon.offhand

# 先只测试下0号位置: 先把图腾从玩家背包换到副手，然后把盔甲里临时保存的物品换到这个位置。(测试成功)
#execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:0b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_0
#execute at @s if entity @s[tag=zxmc.totem_find_0] run item replace entity @s weapon.offhand from entity @s container.0
#execute at @s if entity @s[tag=zxmc.totem_find_0] run item replace entity @s container.0 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
#execute at @s if entity @s[tag=zxmc.totem_find_0] run tag @s add zxmc.totem_find
#execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_0] run tag @s remove zxmc.totem_find_0
#


#  ==================== 第0个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:0b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_0
execute at @s if entity @s[tag=zxmc.totem_find_0] run item replace entity @s weapon.offhand from entity @s container.0
execute at @s if entity @s[tag=zxmc.totem_find_0] run item replace entity @s container.0 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_0] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_0] run tag @s remove zxmc.totem_find_0

#  ==================== 第1个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:1b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_1
execute at @s if entity @s[tag=zxmc.totem_find_1] run item replace entity @s weapon.offhand from entity @s container.1
execute at @s if entity @s[tag=zxmc.totem_find_1] run item replace entity @s container.1 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_1] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_1] run tag @s remove zxmc.totem_find_1

#  ==================== 第2个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:2b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_2
execute at @s if entity @s[tag=zxmc.totem_find_2] run item replace entity @s weapon.offhand from entity @s container.2
execute at @s if entity @s[tag=zxmc.totem_find_2] run item replace entity @s container.2 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_2] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_2] run tag @s remove zxmc.totem_find_2

#  ==================== 第3个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:3b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_3
execute at @s if entity @s[tag=zxmc.totem_find_3] run item replace entity @s weapon.offhand from entity @s container.3
execute at @s if entity @s[tag=zxmc.totem_find_3] run item replace entity @s container.3 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_3] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_3] run tag @s remove zxmc.totem_find_3

#  ==================== 第4个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:4b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_4
execute at @s if entity @s[tag=zxmc.totem_find_4] run item replace entity @s weapon.offhand from entity @s container.4
execute at @s if entity @s[tag=zxmc.totem_find_4] run item replace entity @s container.4 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_4] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_4] run tag @s remove zxmc.totem_find_4

#  ==================== 第5个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:5b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_5
execute at @s if entity @s[tag=zxmc.totem_find_5] run item replace entity @s weapon.offhand from entity @s container.5
execute at @s if entity @s[tag=zxmc.totem_find_5] run item replace entity @s container.5 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_5] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_5] run tag @s remove zxmc.totem_find_5

#  ==================== 第6个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:6b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_6
execute at @s if entity @s[tag=zxmc.totem_find_6] run item replace entity @s weapon.offhand from entity @s container.6
execute at @s if entity @s[tag=zxmc.totem_find_6] run item replace entity @s container.6 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_6] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_6] run tag @s remove zxmc.totem_find_6

#  ==================== 第7个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:7b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_7
execute at @s if entity @s[tag=zxmc.totem_find_7] run item replace entity @s weapon.offhand from entity @s container.7
execute at @s if entity @s[tag=zxmc.totem_find_7] run item replace entity @s container.7 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_7] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_7] run tag @s remove zxmc.totem_find_7

#  ==================== 第8个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:8b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_8
execute at @s if entity @s[tag=zxmc.totem_find_8] run item replace entity @s weapon.offhand from entity @s container.8
execute at @s if entity @s[tag=zxmc.totem_find_8] run item replace entity @s container.8 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_8] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_8] run tag @s remove zxmc.totem_find_8

#  ==================== 第9个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:9b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_9
execute at @s if entity @s[tag=zxmc.totem_find_9] run item replace entity @s weapon.offhand from entity @s container.9
execute at @s if entity @s[tag=zxmc.totem_find_9] run item replace entity @s container.9 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_9] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_9] run tag @s remove zxmc.totem_find_9

#  ==================== 第10个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:10b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_10
execute at @s if entity @s[tag=zxmc.totem_find_10] run item replace entity @s weapon.offhand from entity @s container.10
execute at @s if entity @s[tag=zxmc.totem_find_10] run item replace entity @s container.10 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_10] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_10] run tag @s remove zxmc.totem_find_10

#  ==================== 第11个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:11b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_11
execute at @s if entity @s[tag=zxmc.totem_find_11] run item replace entity @s weapon.offhand from entity @s container.11
execute at @s if entity @s[tag=zxmc.totem_find_11] run item replace entity @s container.11 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_11] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_11] run tag @s remove zxmc.totem_find_11

#  ==================== 第12个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:12b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_12
execute at @s if entity @s[tag=zxmc.totem_find_12] run item replace entity @s weapon.offhand from entity @s container.12
execute at @s if entity @s[tag=zxmc.totem_find_12] run item replace entity @s container.12 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_12] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_12] run tag @s remove zxmc.totem_find_12

#  ==================== 第13个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:13b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_13
execute at @s if entity @s[tag=zxmc.totem_find_13] run item replace entity @s weapon.offhand from entity @s container.13
execute at @s if entity @s[tag=zxmc.totem_find_13] run item replace entity @s container.13 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_13] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_13] run tag @s remove zxmc.totem_find_13

#  ==================== 第14个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:14b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_14
execute at @s if entity @s[tag=zxmc.totem_find_14] run item replace entity @s weapon.offhand from entity @s container.14
execute at @s if entity @s[tag=zxmc.totem_find_14] run item replace entity @s container.14 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_14] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_14] run tag @s remove zxmc.totem_find_14

#  ==================== 第15个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:15b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_15
execute at @s if entity @s[tag=zxmc.totem_find_15] run item replace entity @s weapon.offhand from entity @s container.15
execute at @s if entity @s[tag=zxmc.totem_find_15] run item replace entity @s container.15 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_15] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_15] run tag @s remove zxmc.totem_find_15

#  ==================== 第16个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:16b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_16
execute at @s if entity @s[tag=zxmc.totem_find_16] run item replace entity @s weapon.offhand from entity @s container.16
execute at @s if entity @s[tag=zxmc.totem_find_16] run item replace entity @s container.16 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_16] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_16] run tag @s remove zxmc.totem_find_16

#  ==================== 第17个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:17b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_17
execute at @s if entity @s[tag=zxmc.totem_find_17] run item replace entity @s weapon.offhand from entity @s container.17
execute at @s if entity @s[tag=zxmc.totem_find_17] run item replace entity @s container.17 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_17] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_17] run tag @s remove zxmc.totem_find_17

#  ==================== 第18个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:18b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_18
execute at @s if entity @s[tag=zxmc.totem_find_18] run item replace entity @s weapon.offhand from entity @s container.18
execute at @s if entity @s[tag=zxmc.totem_find_18] run item replace entity @s container.18 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_18] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_18] run tag @s remove zxmc.totem_find_18

#  ==================== 第19个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:19b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_19
execute at @s if entity @s[tag=zxmc.totem_find_19] run item replace entity @s weapon.offhand from entity @s container.19
execute at @s if entity @s[tag=zxmc.totem_find_19] run item replace entity @s container.19 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_19] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_19] run tag @s remove zxmc.totem_find_19

#  ==================== 第20个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:20b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_20
execute at @s if entity @s[tag=zxmc.totem_find_20] run item replace entity @s weapon.offhand from entity @s container.20
execute at @s if entity @s[tag=zxmc.totem_find_20] run item replace entity @s container.20 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_20] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_20] run tag @s remove zxmc.totem_find_20

#  ==================== 第21个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:21b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_21
execute at @s if entity @s[tag=zxmc.totem_find_21] run item replace entity @s weapon.offhand from entity @s container.21
execute at @s if entity @s[tag=zxmc.totem_find_21] run item replace entity @s container.21 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_21] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_21] run tag @s remove zxmc.totem_find_21

#  ==================== 第22个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:22b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_22
execute at @s if entity @s[tag=zxmc.totem_find_22] run item replace entity @s weapon.offhand from entity @s container.22
execute at @s if entity @s[tag=zxmc.totem_find_22] run item replace entity @s container.22 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_22] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_22] run tag @s remove zxmc.totem_find_22

#  ==================== 第23个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:23b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_23
execute at @s if entity @s[tag=zxmc.totem_find_23] run item replace entity @s weapon.offhand from entity @s container.23
execute at @s if entity @s[tag=zxmc.totem_find_23] run item replace entity @s container.23 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_23] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_23] run tag @s remove zxmc.totem_find_23

#  ==================== 第24个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:24b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_24
execute at @s if entity @s[tag=zxmc.totem_find_24] run item replace entity @s weapon.offhand from entity @s container.24
execute at @s if entity @s[tag=zxmc.totem_find_24] run item replace entity @s container.24 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_24] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_24] run tag @s remove zxmc.totem_find_24

#  ==================== 第25个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:25b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_25
execute at @s if entity @s[tag=zxmc.totem_find_25] run item replace entity @s weapon.offhand from entity @s container.25
execute at @s if entity @s[tag=zxmc.totem_find_25] run item replace entity @s container.25 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_25] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_25] run tag @s remove zxmc.totem_find_25

#  ==================== 第26个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:26b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_26
execute at @s if entity @s[tag=zxmc.totem_find_26] run item replace entity @s weapon.offhand from entity @s container.26
execute at @s if entity @s[tag=zxmc.totem_find_26] run item replace entity @s container.26 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_26] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_26] run tag @s remove zxmc.totem_find_26

#  ==================== 第27个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:27b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_27
execute at @s if entity @s[tag=zxmc.totem_find_27] run item replace entity @s weapon.offhand from entity @s container.27
execute at @s if entity @s[tag=zxmc.totem_find_27] run item replace entity @s container.27 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_27] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_27] run tag @s remove zxmc.totem_find_27

#  ==================== 第28个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:28b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_28
execute at @s if entity @s[tag=zxmc.totem_find_28] run item replace entity @s weapon.offhand from entity @s container.28
execute at @s if entity @s[tag=zxmc.totem_find_28] run item replace entity @s container.28 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_28] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_28] run tag @s remove zxmc.totem_find_28

#  ==================== 第29个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:29b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_29
execute at @s if entity @s[tag=zxmc.totem_find_29] run item replace entity @s weapon.offhand from entity @s container.29
execute at @s if entity @s[tag=zxmc.totem_find_29] run item replace entity @s container.29 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_29] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_29] run tag @s remove zxmc.totem_find_29

#  ==================== 第30个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:30b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_30
execute at @s if entity @s[tag=zxmc.totem_find_30] run item replace entity @s weapon.offhand from entity @s container.30
execute at @s if entity @s[tag=zxmc.totem_find_30] run item replace entity @s container.30 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_30] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_30] run tag @s remove zxmc.totem_find_30

#  ==================== 第31个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:31b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_31
execute at @s if entity @s[tag=zxmc.totem_find_31] run item replace entity @s weapon.offhand from entity @s container.31
execute at @s if entity @s[tag=zxmc.totem_find_31] run item replace entity @s container.31 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_31] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_31] run tag @s remove zxmc.totem_find_31

#  ==================== 第32个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:32b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_32
execute at @s if entity @s[tag=zxmc.totem_find_32] run item replace entity @s weapon.offhand from entity @s container.32
execute at @s if entity @s[tag=zxmc.totem_find_32] run item replace entity @s container.32 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_32] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_32] run tag @s remove zxmc.totem_find_32

#  ==================== 第33个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:33b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_33
execute at @s if entity @s[tag=zxmc.totem_find_33] run item replace entity @s weapon.offhand from entity @s container.33
execute at @s if entity @s[tag=zxmc.totem_find_33] run item replace entity @s container.33 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_33] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_33] run tag @s remove zxmc.totem_find_33

#  ==================== 第34个槽位 ====================
execute at @s if entity @s[tag=!zxmc.totem_find,nbt={Inventory:[{Slot:34b, id:"minecraft:totem_of_undying"}]}] run tag @s add zxmc.totem_find_34
execute at @s if entity @s[tag=zxmc.totem_find_34] run item replace entity @s weapon.offhand from entity @s container.34
execute at @s if entity @s[tag=zxmc.totem_find_34] run item replace entity @s container.34 from entity @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1] weapon.offhand
execute at @s if entity @s[tag=zxmc.totem_find_34] run tag @s add zxmc.totem_find
execute at @s if entity @s[tag=zxmc.totem_find,tag=zxmc.totem_find_34] run tag @s remove zxmc.totem_find_34




# 最后清理


execute at @s if entity @s[tag=zxmc.totem_find] run tag @s remove zxmc.totem_find
execute at @s run kill @e[type=minecraft:armor_stand,tag=zxmc.totem,sort=nearest,limit=1]