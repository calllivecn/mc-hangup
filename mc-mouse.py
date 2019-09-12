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
    kbm.mousedown("left")
    time.sleep(3)
    kbm.mouseup("left")

def fishing(kbm, args):

    # 切换物品栏，选项钓鱼竿
    fishingrod = args.number[0]
    food = args.unmber[1]

    kbm.key(fishingrod)

    try:
        input("按CTRL+C结束。")
        for _ in range(40*60): # 40 分钟吃一次食物。
            kbm.mouseclick("right")
            time.sleep(1)

        eatfood(kbm, food)

    except KeyboardInterrupt:
        print()

def mouseLeftDown(kbm, args):

    try:
        kbm.mousebtndown("left")
        input("按CTRL+C结束。")
    except KeyboardInterrupt:
        kbm.mousebtnup("left")
        print()



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

    parse_mouseleftdown.set_defaults(func=mouseLeftDown)

    parse_fishing.set_defaults(func=fishing)

    args = parse.parse_args()
    print(args);exit(0)

    kbm = libkbm.VirtualKeyboardMouse()
    args.func(kbm, args)


if __name__ == "__main__":
    main()
