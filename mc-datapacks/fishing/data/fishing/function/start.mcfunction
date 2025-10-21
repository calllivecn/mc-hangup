
$data modify storage fishing:player name set value "$(name)"

$execute store result storage fishing:player uuid3 int 1 run scoreboard players get $(name) uuid3

