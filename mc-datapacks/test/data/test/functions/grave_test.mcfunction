
summon minecraft:armor_stand ~ ~ ~ {Tags:["graves.marker","graves.hitbox","graves.new"],Invisible:1b,NoGravity:1b,Invulnerable:1b,Small:1b,DisabledSlots:256,HandItems:[{id:"minecraft:stone_button",Count:1b,tag:{gravesData:{items:[]}}},{id:"minecraft:stone_button",Coun    t:2b,tag:{gravesData:{}}}],Pose:{RightArm:[0.0f,-90.0f,0.0f],LeftArm:[0.0f,90.0f,0.0f],Head:[180.0f,0.0f,0.0f]},Silent:1b}
# 生成坟墓:
summon minecraft:armor_stand ~ ~ ~ {Tags:["graves.items","graves.new","graves.marker"],Invisible:1b,Small:1b,DisabledSlots:256,HandItems:[{id:"minecraft:stone_button",Count:1b,tag:{gravesitems:[]}}]}

# 保存全身物品到坟墓
data modify entity @e[type=minecraft:armor_stand,sort=nearest,limit=1] HandItems[0].tag.zxmcitems append from entity @s Inventory