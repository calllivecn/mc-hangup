# 先为所有死亡的玩家打上标签
#execute as @a run tag @s[type=player,nbt={DeathTime:0s}] add live
tag @a[nbt={Health:0.0f}] add im_death


execute as @a[tag=im_death,tag=!i_say_death] at @s run me "我死了"

# 保证只说一次，然后移除 i_say_death
tag @a[tag=im_death,tag=!i_say_death,nbt={Health:0.0f}] add i_say_death


# 然后玩家复活后，需要及时去掉 标签
tag @a[tag=im_death,tag=i_say_death,nbt=!{Health:0.0f}] remove i_say_death
tag @a[tag=im_death,nbt=!{Health:0.0f}] remove im_death

