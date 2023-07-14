

import cv2
from matplotlib import pyplot as plt


temp = plt.imread("template.png")
target = plt.imread("target.png")

temp_gray = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
taret_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)



plt.imshow(img)
plt.show()
