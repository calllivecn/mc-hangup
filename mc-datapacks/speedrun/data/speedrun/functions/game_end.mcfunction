

team join SpeedRun @a

gamemode adventure @a

title @a times 2 100 2

title @a[tag=win] title {"text":"胜利！","bold":true, "color": "yellow"}

title @a[tag=!win] title {"text":"失败！","bold":true, "color": "yellow"}

scoreboard players add @a[tag=win] score 1

tag @a remove running
tag @a remove killer
tag @a remove win