![工作台](mc-icon.png  "工作台") Minecraft 中文聊天、挂机、自动钓鱼、等辅助工具
----


## mc-Dungeon.py:

```
这个工具使用三角定位法找地牢。
由于鼠标对角会有一些误差，所以一般使用两次连续定位，就能准确定位了。
python3  mc-Dungeon.py` 查看使用方法。
```

## mc-checkupdate.py:

```
检查minecraft新版本。
```

## 以下工具目前只支持Linux：

### mc-mouse.py: 模拟鼠标键盘的工具

- 能在Xorg和wayland下使用。依赖：keyboardmouse 包，需要root(or 当前用户加入input用户组)运行。
- pip install git+https://github.com/calllivecn/keyboardmouse@master
- 或者打包成pyz文件：bash build2freeze-mc-mouse.sh

- 执行下面命令查看使用方法：

```
mc-mouse.pyz --help
```

## mc-fishing 这是自动钓鱼工具

[自动钓鱼工具](mc-fishing-opencv/)

## 这是 mcdreforged 的插件：

[mcdreforged](mcdr)


## 这是之前的脚本工具，只在X11桌面环境下工作

[mc-shell-tools](mc-shell-tools/)

