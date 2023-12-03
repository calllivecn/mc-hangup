
tag @s add im_death
me I_m_death
return

# 保证只说一次，然后移除 i_say_death
# tag @a[tag=im_death,tag=!i_say_death,nbt={Health:0.0f}] add i_say_death


# 然后玩家复活后，需要及时去掉 标签
# tag @a[tag=im_death,tag=i_say_death,nbt=!{Health:0.0f}] remove i_say_death
# tag @a[tag=im_death,nbt=!{Health:0.0f}] remove im_death

