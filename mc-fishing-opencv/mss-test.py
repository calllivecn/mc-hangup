
import time
import threading

import numpy as np
from mss import mss


# 这是截全屏
# sct.shot()

monitor = {"top": 40, "left": 0, "width": 800, "height": 640}
monitor = (40, 0, 800, 640)

def test():
    sct = mss(display=":1.0")

    t1 = time.time()
    for i in range(10):
        img = np.array(sct.grab(monitor))
    t2 = time.time()
    #print(img)
    t = (t2 - t1) / 10
    print(f"每次截图平均耗时：{round(t, 3)}/s")

    sct.close()


th = threading.Thread(target=test, name="截图线程", daemon=True)
th.start()

th.join()
