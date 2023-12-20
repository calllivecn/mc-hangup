#execute as @a at @s if entity @e[type=

execute as @a[nbt={SelectedItem:{id:"minecraft:fishing_rod"}}] if entity @e[type=minecraft:fishing_bobber] run me 我还在
execute as @a[nbt={SelectedItem:{id:"minecraft:fishing_rod"}}] unless entity @e[type=minecraft:fishing_bobber] run me 我不在
