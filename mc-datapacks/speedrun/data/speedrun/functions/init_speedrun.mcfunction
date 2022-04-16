# 设置记分板
scoreboard objectives add death deathCount ["死亡记数"]

# 设置得分板
scoreboard objectives add score dummy ["得分"]

team add SpeedRun

# 关闭团队PVP
team modify SpeedRun friendlyFire false

# 关闭服务器命令通知
team modify SpeedRun friendlyFire false

scoreboard objectives setdisplay list death
scoreboard objectives setdisplay sidebar score