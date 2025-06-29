
#调用方式？
# function clearchunk:water {x: 1, y: 1, z: 1}

#水流或者水源
$execute if block $(x) $(y) $(z) minecraft:water run return run setblock $(x) $(y) $(z) minecraft:air strict

#水草，半高或者全高
$execute if block $(x) $(y) $(z) minecraft:seagrass run return run setblock $(x) $(y) $(z) minecraft:air strict
$execute if block $(x) $(y) $(z) minecraft:tall_seagrass run return setblock $(x) $(y) $(z) minecraft:air strict


#岩浆块气泡柱
$execute if block $(x) $(y) $(z) minecraft:dripstone_block run return run setblock $(x) $(y) $(z) minecraft:air destroy


