#!/usr/bin/env python3
# coding=utf-8
# date 2019-09-11 21:24:52
# author calllivecn <c-all@qq.com>



import sys
import time
import random
import string
import signal
import argparse

try:
    import libkbm
except ModuleNotFoundError:
    logger.error("需要安装keyboardmouse模块,地址：https://github.com/calllivecn/keyboardmouse")
    sys.exit(1)

from logs import logger, setLevel

def countdown(sig, frame):
    sys.exit(0)

def disableMouse():
    """
    通过 grab() 禁用鼠标。
    """
    mouses, keyboards = libkbm.getkbm()

    for name in mouses:
        logger.info("禁用鼠标: {}".format(name))
        libkbm.disableDevice(name)


def eatfood(kbm, food):
    """
    kbm: ...
    food: 食物的位置。
    """

    kbm.key(food)
    kbm.mousebtndown("right")
    time.sleep(3)
    kbm.mousebtnup("right")

def mouseLeftDown(kbm, args):

    try:
        print("按CTRL+C结束。")
        kbm.mousebtndown("left")
        input()
    except KeyboardInterrupt:
        kbm.mousebtnup("left")
        print()

def mouseRightDown(kbm, args):

    try:
        print("按CTRL+C结束。")
        kbm.mousebtndown("right")
        input()
    except KeyboardInterrupt:
        kbm.mousebtnup("right")
        print()

def fishing(kbm, args):

    # 切换物品栏，选项钓鱼竿
    if len(args.number) == 0:
        fishingrod = 1
        food = 2
    else:
        fishingrod = args.number[0]
        food = args.number[1]

    kbm.key(fishingrod)

    try:
        print("按CTRL+C结束。")
        while True:
            for _ in range(40*60): # 40 分钟吃一次食物。
                kbm.mouseclick("right")
                time.sleep(1)

            eatfood(kbm, food)
            kbm.key(fishingrod)

    except KeyboardInterrupt:
        print()


def __move(kbm):
    for _ in range(random.randint(2, 5)):
        m = random.choices(["w", "s", "a", "d"])[0]
        kbm.keydown(m)
        time.sleep(1)
        kbm.keyup(m)

def __chat(kbm, msg):
    kbm.key("t")
    for c in msg:
        kbm.key(c)

    kbm.key("enter")

def hangup(kbm, args):

    logger.info("吃食物.")
    eatfood(kbm, args.food)

    try:
        while True:
            print("按CTRL+C结束。")
            logger.info("等待...")

            # 反挂机检测机制。
            #if args.ahd != 0:
            #    for _ in range(args.ahd):
            #        time.sleep(1)

            # 间隔 waiteat分钟吃食物
            time.sleep(args.waiteat * 60)

            logger.info("吃食物.")
            eatfood(kbm, args.food)

            if args.message:
                logger.info(f"发送挂机消息: {args.message}")
                __chat(kbm, args.message)

            if args.move:
                logger.info("随机移动.")
                __move(kbm)

    except KeyboardInterrupt:
        print()

def nugong(kbm, args):
    """
    用法：把9把弩放在快捷栏，设置一个触发快捷键。
    """
    hotkey = libkbm.WatchHotKey(args.masterkey, args.key)

    #nugong_up = libkbm.WatchHotKey(args.masterkey, args.up)

    try:
        while True:
            if hotkey.watch():
                logger.debug(f"hotkey: {hotkey} masterkey: {args.masterkey} key: {args.key}")
                for i in range(args.start, args.end + 1):
                    logger.debug(f"使用快捷栏：{i}")
                    kbm.key(str(i))
                    time.sleep(args.interval)
                    kbm.mouseclick("right")
                    time.sleep(args.interval)
    except KeyboardInterrupt:
        pass


def __message(msg):
    
    for c in msg:
        if c not in string.ascii_letters and c not in string.digits:
            raise argparse.ArgumentTypeError("必须是大小写字母和数字。")

    return msg

HELP="""
参数：
-h, --help      输出帮助信息。
-d, --disable   运行期间关闭鼠标。默认：不关闭鼠标
-v, --verbose   运行过程详细。
-w, --wait WAIT 开始前的等时间。
"""

def main():

    parse = argparse.ArgumentParser(usage="%(prog)s [选项] <功能> [参数]",
                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                    #formatter_class=argparse.RawTextHelpFormatter,
                                    description="MC 一些挂机的鼠标操作。(需要root权限)\n"
                                    "例子：\n"
                                    "   %(prog)s leftdown\n"
                                    "   %(prog)s fishing 1 2\n"
                                    "   %(prog)s fishing --help\n",
                                    )

    group1 = parse.add_argument_group(title="通用选项")

    #group1.add_argument("-h", "--help", action="store_true", help="输出帮助信息。")

    group1.add_argument("-d", "--disable", action="store_true", help="运行期间关闭鼠标。默认：不关闭鼠标")

    group1.add_argument("-v", "--verbose", action="count", default=0, help="运行过程详细。例如：-v, -vv, -vvv")

    group1.add_argument("-t", "--time", action="store", type=int, default=0, help="运行T分钟后退出，默认：0, 表示一直运行。")

    group1.add_argument("-w", "--wait", type=int, default=3, help="开始前的等时间。")

    parse.add_argument("--parse", action="store_true", help="输出命令行参数解析结果。")

    subparse = parse.add_subparsers(title="功能", description="可用功能名称", metavar="")

    #group2 = subparse.add_argument_group(title="选项")

    parse_mouseleftdown = subparse.add_parser("leftdown", add_help=False, help="按住鼠标左键。")

    parse_mouserightdown = subparse.add_parser("rightdown", add_help=False, help="按住鼠标右键。")

    parse_fishing = subparse.add_parser("fishing",
                                        help="钓鱼机，挂机钓鱼。",
                                        description="fishing <1> <2>\n"
                                        "默认：1号物品栏为钓鱼竿, 2号物品栏为食物。\n",
                                        formatter_class=argparse.RawTextHelpFormatter)

    parse_fishing.add_argument("number", nargs=2, choices=[str(x) for x in range(10)], metavar="number", help="物品栏编号，0~9。")


    parse_hangup = subparse.add_parser("hangup", help="长时间挂机，进食，产生活动：移动，发信息。")
    parse_hangup.add_argument("--food", default="1", choices=[str(x) for x in range(10)], required=True, metavar="[0-9]", help="食物物品栏编号。(每30分钟吃一个食物)")
    parse_hangup.add_argument("--waiteat", type=int, default=30, help="间隔<wait eat>吃一次食物。default: 30分钟")
    #parse_hangup.add_argument("--ahd", type=int, default=0, help="反挂机检测间隔时间。default: 30s")
    parse_hangup.add_argument("--move", action="store_true", help="是否随机按下1秒W,S,A,D模拟移动。")
    parse_hangup.add_argument("--message", type=__message, help="发送一个挂机消息。(只能是大小写字母和数字)")
    

    nu3gong1 = subparse.add_parser("nugong", help="九连发弩弓!!!(default: 按下alt+g触发)")
    nu3gong1.add_argument("--masterkey", default="alt", help="触发的主键。(default: alt)")
    nu3gong1.add_argument("--key", default="g", help="触发的副键，发射键。(default: g)")
    #nu3gong1.add_argument("--up", default="v", help="触发的副键，给弩上箭。(default: v)")
    nu3gong1.add_argument("--interval",type=float, default=0.05, help="触发按键的间隔时间。(default: 0.05 秒)")
    nu3gong1.add_argument("--start", type=int, default=1, help="快捷栏弩的开始位置。(default: 1)")
    nu3gong1.add_argument("--end", type=int, default=9, help="快捷栏弩的结束位置。(default: 9)")


    parse_mouseleftdown.set_defaults(func=lambda arg: mouseLeftDown(kbm, arg))

    parse_mouserightdown.set_defaults(func=lambda arg: mouseRightDown(kbm, arg))

    parse_fishing.set_defaults(func=lambda arg: fishing(kbm, arg))

    parse_hangup.set_defaults(func=lambda arg: hangup(kbm, arg))

    nu3gong1.set_defaults(func=lambda arg: nugong(kbm, arg))

    args = parse.parse_args()
    
    if args.parse:
        print(args)
        sys.exit(0)


    if len(sys.argv) == 1:
        parse.print_help()
        sys.exit(0)

    setLevel(args.verbose)

    print(args.wait, "秒钟等待时间。。。")
    time.sleep(args.wait)

    if args.time != 0:
        signal.signal(signal.SIGALRM, countdown)
        # *60 是分钟
        signal.alarm(args.time * 60)
        #signal.alarm(args.time)
        print(f"{args.time}分钟后退出程序。")

    kbm = libkbm.VirtualKeyboardMouse()

    if args.disable:
        disableMouse()

    args.func(args)


if __name__ == "__main__":
    main()
