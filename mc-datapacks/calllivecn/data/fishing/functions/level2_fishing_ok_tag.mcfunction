
tag @s add fishing_ok

tell @s Debug: 鱼钩在水面+水面平稳


# 执行主体，不能传导到 schedule 高度的函数里
# execute as @s run schedule function fishing:level3_delay_tag 50t

schedule function fishing:level3_delay_tag 20t
