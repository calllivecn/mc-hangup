# 目前在wayland+桌面缩放情况下 卡在不能正确获取窗口位置。

# 使用opencv 匹配图片，实现自动钓鱼。

- 目前支持X11 wayland。依赖：keyboardmouse 包，需要当前用户加入input用户组(或者 使用root用户)运行。
- pip install git+https://github.com/calllivecn/keyboardmouse@master
- 打包命令(会生成目录：dist/mc-fishing/ 复制整个目录走就可以执行了)

```shell
pyinstaller mc-fishing.spec

```


- 之后执行(进入mc-fishing/)

```shell
./mc-fishing
or
./mc-fishing --help
```
