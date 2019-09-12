#!/usr/bin/env python3
# coding=utf-8
# date 2019-09-11 21:24:52
# author calllivecn <c-all@qq.com>

import time
import argparse

import libkbm



def eatfood(kbm, food):
    """
    kbm: ...
    food: 食物的位置。
    """

    kbm.key(food)
    kbm.mousedown("right")
    time.sleep(3)
    kbm.mouseup("right")

def fishing(kbm, args):

    # 切换物品栏，选项钓鱼竿
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

    except KeyboardInterrupt:
        print()

def mouseLeftDown(kbm, args):

    try:
        print("按CTRL+C结束。")
        kbm.mousebtndown("left")
    except KeyboardInterrupt:
        kbm.mousebtnup("left")
        print()


def hangup(kbm, args):
    print("功能还没完成，使用其他功能吧！")


def main():

    parse = argparse.ArgumentParser(#title="选项",
                                    description="MC 一些挂机的鼠标操作。")

    subparse = parse.add_subparsers(title="功能", description="可用功能名称")

    parse_mouseleftdown = subparse.add_parser("leftdown", help="按住鼠标左键")

    parse_fishing = subparse.add_parser("fishing", usage="%(prog)s <1> <2>",
                                        description="1： 钓鱼竿, 2：食物。(物品栏编号) 换成你对应的编号",
                                        help="钓鱼机，挂机钓鱼。")
    parse_fishing.add_argument("number", nargs=2, choices=[str(x) for x in range(10)],
                                help="物品栏编号，0~9。")

    parse_hangup = subparse.add_parser("hangup", help="长时间挂机，进食，产生活动：移动，发信息。")
    parse_hangup.add_argument("-f", "--food", type=int, required=True, help="食物编号")
    parse_hangup.add_argument("-m", "--move", action="store_true", help="是否随机按下1秒W,S,A,D模拟移动。")
    parse_hangup.add_argument("-t", "--time", type=int, default=30, help="随机移动间隔时间")
    #parse_hangup.add_argument("--message", help="是否随机发送一个挂机消息。(只能是)")
    

    parse_mouseleftdown.set_defaults(func=lambda arg: mouseLeftDown(kbm, arg))

    parse_fishing.set_defaults(func=lambda arg: fishing(kbm, arg))

    parse_hangup.set_defaults(func=lambda arg: hangup(kbm, arg))

    args = parse.parse_args()
    #print(args);exit(0)

    kbm = libkbm.VirtualKeyboardMouse()
    args.func(args)


if __name__ == "__main__":
    main()
