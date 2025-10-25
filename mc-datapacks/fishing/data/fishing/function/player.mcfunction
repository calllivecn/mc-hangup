#me 有收杆

$execute as @s if score @s uuid3 matches $(uuid3) run player $(name) use once
# $execute as @s unless score @s uuid3 matches $(uuid3) run me 不匹配

$execute as @s if score @s uuid3 matches $(uuid3) run schedule function fishing:reset 10t

# 使用 say 通知其他玩家有鱼上钩
$execute as @s unless score @s uuid3 matches $(uuid3) run me 🐠

return 0

