
import time

import cv2
#from matplotlib import 
import matplotlib.pyplot as plt

from funcs import (
    imgshow,
    search_picture,
    cv2plt_gray,
)

img_temp = cv2.imread('template.png')#读取原图片
img_target = cv2.imread('target.png')#读取旋转图片
img_match1 = cv2.imread('match1.png')#读取缩放图片
img_match2 = cv2.imread('match2.png')

imgs = [ img_temp, img_target, img_match1, img_match2 ]

imgshow(imgs)

rgb_imgs = []
gray_imgs = []
binary_imgs = []
binarys_retvals = []
for img in imgs:
    rgb_imgs.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    gray_imgs.append(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    retval_temp, dst_temp = cv2.threshold(img, 125, 255, cv2.THRESH_BINARY)
    binary_imgs.append(dst_temp)
    binarys_retvals.append(retval_temp)


#ORB 特征提取
a=time.time()
sift2 = cv2.ORB_create()
orbs = []
for img in binary_imgs:
    kp1, des1 = sift2.detectAndCompute(img, None)
    orbs.append((kp1, des1))
    # print(f"pk: {kp1} des: {des1}")

b=time.time()
print("ORB 特征提取 time:", b-a)

# 展示
prints = []
for i, orb in enumerate(orbs):
    img11 = cv2.drawKeypoints(rgb_imgs[i], orbs[i][0], rgb_imgs[i], color=(255, 0 , 0))
    prints.append(img11)

imgshow(prints)


# 特征匹配展示
#原图与仿射图的匹配连线效果图展示
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True) # orb的normType应该使用NORM_HAMMING

orb_matchs = []
for i, orb in enumerate(orbs[1:]):
    temp = orbs[0][1]
    target = orb[i+1][1]

    matches = bf.match(temp, target)
    matches = sorted(matches, key=lambda x: x.distance)
    knnMatches = bf.knnMatch(temp, target, k = 1) # drawMatchesKnn

    for m in matches:
        for n in matches:
            if(m != n and m.distance >= n.distance*0.75):
                matches.remove(m)
                break
    # img = cv2.drawMatches(img1, pk1, img4, kp4, matches[:50], img4, flags=2)
    img = cv2.drawMatches(imgs[0], orbs[0][0], imgs[i+1], orb[1], matches[:50], imgs[i+1], flags=2)
    orb_matchs.append(img)

imgshow(orb_matchs)

exit(0)
