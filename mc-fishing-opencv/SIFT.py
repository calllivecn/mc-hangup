
import time
from pathlib import Path

import cv2
import matplotlib.pyplot as plt

from funcs import (
    imgshow,
    search_picture,
    cv2plt_gray,
)

images_path = Path("images")

img_temp = cv2.imread(str(images_path / 'temp-big.png'))#读取原图片
img_target = cv2.imread(str(images_path / 'target-orb.png'))#读取旋转图片
img_match1 = cv2.imread(str(images_path / 'match1.png'))#读取缩放图片
img_match2 = cv2.imread(str(images_path / 'match2.png'))

imgs = [img_temp, img_target, img_match1, img_match2 ]

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
sift = cv2.SIFT_create()
sifts = []
for img in binary_imgs:
    kp1, des1 = sift.detectAndCompute(img, None)
    sifts.append((kp1, des1))
    # print(f"pk: {kp1} des: {des1}")

b=time.time()
print("SIFT 特征提取 time:", b-a)

# 展示
prints = []
for i, orb in enumerate(sifts):
    img11 = cv2.drawKeypoints(rgb_imgs[i], sifts[i][0], rgb_imgs[i], color=(255, 0 , 0))
    prints.append(img11)

imgshow(prints)

# 特征匹配展示
# 原图与仿射图的匹配连线效果图展示

# FLANN 参数设计
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks=50)
flann = cv2.FlannBasedMatcher(index_params, search_params)

a = time.time()

sift_matchs = []
for i, sift_ in enumerate(sifts):
    temp_pk = sifts[0][0]
    temp_des = sifts[0][1]
    
    target_des = sifts[i][1]

    matches = flann.knnMatch(temp_des, target_des, k=2)
    matchesMask = [ [0, 0] for i in range(len(matches))]
    good = []
    for m, n in matches:
        if(m.distance < n.distance*0.75):
            good.append([m])

    # img = cv2.drawMatches(img1, pk1, img4, kp4, matches[:50], img4, flags=2)
    img = cv2.drawMatchesKnn(img_temp, temp_pk, imgs[i], sift_[0], good, None, flags=2)
    sift_matchs.append(img)


b=time.time()
print("SIFT 特征匹配与展示 time:", b-a)

imgshow(sift_matchs)

exit(0)
