execute as @a[nbt={Health:0.0f}] at @s run me I_m_death

#item replace entity @s weapon.offhand with minecraft:totem_of_undying 1

advancement revoke @s only deaths:trigger_death player_death
