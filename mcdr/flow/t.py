#!/usr/bin/env python3
# coding=utf-8
# date 2022-04-09 02:57:25
# author calllivecn <calllivecn@outlook.com>




import math

angle = (180/math.pi)


# 求两点之间的距离
def L(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)



print("="*10, "知道坐标求角", "="*10)
print(math.asin(1/L(0, 0, 1, 1)) * angle)

print(math.atan(3/2) * angle)
print(math.atan(2/-3) * angle)
print(math.atan(-3/-2) * angle)

print(math.atan(-1) * angle)

print("="*10, "知道角求坐标之比", "="*10)
print(math.tan(-33.69/angle))
print(math.sin(100/angle))
print(math.sin(-80/angle))