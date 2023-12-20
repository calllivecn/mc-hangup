# 这里是检测到有玩家钓鱼，的分支处理。

# execute as @s run me Debug: level1_fishing1: 检测上钩。

# 在多添加几个数值检测。Motion的。
# 初妈化 scoreboard objectives add fishX dummy
function fishing:level2_begin
function fishing:level2_check_fishxyz



# 这样ok
#execute as @a[nbt={SelectedItem:{id:"minecraft:fishing_rod"}}] at @e[type=minecraft:fishing_bobber,limit=1] positioned ~ ~ ~ if block ~ ~ ~ minecraft:water run me 我到水面了


# 这样ok, 上面的升级版。
# 鱼钩到水面后平稳后(移动范围小于0.2), 打上平稳(fishing_ok)标签
execute as @s[tag=!fishing_ok,scores={fishX=..2,fishY=..2,fishZ=..2}] at @e[type=minecraft:fishing_bobber,distance=..30,sort=nearest,limit=1] positioned ~ ~ ~ if block ~ ~ ~ minecraft:water run function fishing:level2_fishing_ok_tag


# 鱼钩到水面平稳后，处理有没有鱼上钩。
execute as @s[tag=fishing_ok] at @s if entity @e[type=minecraft:fishing_bobber,distance=..30,sort=nearest,limit=1] run function fishing:level2_fishing_ok


function fishgin:level2_end
