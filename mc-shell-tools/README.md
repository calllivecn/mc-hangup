![工作台](../mc-icon.png  "工作台") Minecraft 中文聊天、挂机、辅助工具
----

- 使用方法

### 配置mc.cfg:

```shell
MC\_NAME='Minecraft 1.14.4'

# xinput list --name-only  OR grep Name /proc/bus/input/devices
# 显示的需要禁用的鼠标
MOUSE="Logitech USB Optical Mouse"
```

### 使用方法：

### *注意:*  以下工具只能Xorg下使用
- mc-chat.sh
- mc-eatfood.sh
- mc-fishing.sh
- mc-input.sh
- mc-mouse1down.sh
- mc-sleep.sh


依赖项：python3, zenity, xdotool

在您的桌面环境添加一组快捷键，比如 Super + shift + T，来启动`mc-chat.sh` 或`mc-input.sh`脚本。


当进行 Minecraft 游戏的时候，按 Super + shift + T，输入聊天内容并点击确定。

## *Linux 上从1.13.x 开始可以直接输入聊天内容，不在需要辅助工具。(ubuntu18.04 测试)*

本软件**不附带任何保证**，作者不承担本软件产生的任何潜在的损失。
