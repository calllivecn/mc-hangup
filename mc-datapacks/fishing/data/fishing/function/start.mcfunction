
$data modify storage fishing:$(name) set value "$(name)"

$execute store result storage fishing:$(name) uuid3 int 1 run scoreboard players get $(name) uuid3

$function fishing:fishing with fishing:$(name)

