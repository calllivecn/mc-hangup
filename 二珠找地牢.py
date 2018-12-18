#!/usr/bin/env py3
#coding=utf-8
# date 2018-12-11 09:06:47
# author calllivecn <c-all@qq.com>

import sys
import math

usage_pre=f"""
原理：
1. 工作原理是三角定位。
2. 需要两个点和指向角度。(至少需要扔两次末影珍珠,有两个点和两个角)
"""

usage=f"""
使用方法: 
{sys.argv[0]} x1 z1 角1 x2 z2 角2

例子: 
{sys.argv[0]} 100.3 100.4 120.5 150.6 20.7 145.8

注意点：

1. 六个参数都要是数字。

2. 第一次定位时：
   任意在一个点扔出末影珍珠后，
   第二个点最好向第一个方向的垂直方向移动100格左右，
   在丢出第二个点。(减小误差)

3. 由于用鼠标对角度时会有误差，所以一般会进行两次三角定位。
   第一次如果定位出的距离较远，在到达第一次目的点后，
   在做一次小距离的三角定位(第二个点向第一个方向的垂直方向移动30格左右)，
   一般就能准确定位到地牢了。
"""

def angle2rad(du):
    return du / 180 * math.pi

if len(sys.argv) != 7:
    print("使用方法: {} x1 z1 angle1 x2 z2 angle2".format(sys.argv[0]))
    print("例子: {} 100 100 120 150 20 145".format(sys.argv[0]))
    exit(1)

nums = []
for i in sys.argv[1:]:
    try:
        nums.append(float(i))
    except ValueError:
        print("六个参数都要是数字。")
        print("使用方法: {} x1 z1 angle1 x2 z2 angle2".format(sys.argv[0]))
        print("例子: {} 100 100 120 150 20 145".format(sys.argv[0]))
        exit(1)


x1, z1, angle1 = nums[0], nums[1], nums[2]
x2, z2, angle2 = nums[3], nums[4], nums[5]

angle0 = angle2

if angle1 > 180 and angle1 < -180 and angle2 > 180 and angle2 < -180:
    print("我的世界的角度在-180 ~ 180 之间")
    print("请重新输入。")
    exit(1)

if 0 < angle1 <= 180:
    angle1 = angle1 - 90
elif -180 <= angle1 <= 0:
    angle1 = angle1 + 90

if 0 < angle2 <= 180:
    angle2 = angle2 - 90
elif -180 <= angle2 <= 0:
    angle2 = angle2 + 90

#print("angle1, angle2:", angle1, angle2)

b1 = z1 - math.tan(angle2rad(angle1)) * x1 


# 判断 第一个点 和 第二个点是不是在同一条直线上
check_z = x2 * math.tan(angle2rad(angle2)) + b1
if z2 == round(check_z):
    print("第一个点 和 第二个点在同一条直线上！！！")
    print("这样是做不了三角定位的！")
    print("应该向第一个方向垂直的方向跟100格左右，在丢出第二个点")
    exit(1)

# 判断是否出现平行线
if math.tan(angle2rad(angle1)) == math.tan(angle2rad(angle2)):
    print("俩点的斜率相同！！！")
    print("可能是你跑在同一条线上。")
    print("还有极少可能你跑的太远，第二次指向的是另外一个地牢。")
    print("应该向第一个方向垂直的方向跑100格左右，在丢出第二个点")
    exit(1)
    
b2 = z2 - math.tan(angle2rad(angle2)) * x2

x0 = (b1 - b2) / (math.tan(angle2rad(angle2)) - math.tan(angle2rad(angle1)))

z0 = math.tan(angle2rad(angle1)) * x0 + b1


print("第一个点: x1, z1:",(x1, z1),"角度:",nums[2], "⁰")
print("第二个点: x2, z2:",(x2, z2),"角度:",nums[5], "⁰")
#print("求出的: b1, b2:", (b1, b2))
print("目的点: x0, z0:",(round(x0), round(z0)))

distance = math.sqrt( (x1 - x2) ** 2 + (z1 - z2) ** 2)

print("当前距离目标地(直线距离)：", round(distance), "格")
print("角度为：",round(angle0, 1), "⁰")

if distance >= 300:
    msg = """
你现在距离目标还有点远可以在到达以上目的点后，在次使用一次小距离的三角定位，以精准定位。
在到达上面计数出的目的点后，在进行一次定位的时候，就只要向垂直方向跑30格左右就可以了。
"""
    print(msg)


