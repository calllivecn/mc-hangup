

![工作台](mc-icon.png  "工作台") Minecraft 中文聊天、挂机、辅助工具
----



## 使用方法：

### 配置mc.cfg:

```shell
MC\_NAME='Minecraft 1.14.4'

# xinput list --name-only  OR grep Name /proc/bus/input/devices
# 显示的需要禁用的鼠标
MOUSE="Logitech USB Optical Mouse"
```


### mc-Dungeon.py :
这个工具使用三角定位法找地牢。
由于鼠标对角会有一些误差，所以一般使用两次连续定位，就能准确定位了。
python3  mc-Dungeon.py` 查看使用方法。

### mc-checkupdate.py:
检查minecraft新版本。

### Linux：

### *注意:* 只能Xorg下使用，目前还不能在wayland下使用。
依赖项：python3, zenity, xdotool

在您的桌面环境添加一组快捷键，比如 Super + shift + T，来启动`mc-chat.sh` 或`mc-input.sh`脚本。


当进行 Minecraft 游戏的时候，按 Super + shift + T，输入聊天内容并点击确定。

##*Linux 上从1.13.x 开始可以直接输入聊天内容，不在需要辅助工具。(ubuntu18.04 测试)*

本软件**不附带任何保证**，作者不承担本软件产生的任何潜在的损失。
