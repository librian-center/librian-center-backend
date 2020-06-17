import logging

import cv2
import numpy as np


def 编码为webp(图):
    retval, buf = cv2.imencode(".webp",
                               图,
                               [cv2.IMWRITE_WEBP_QUALITY, 90])
    assert retval, '图像编码失败'
    logging.warning(type(buf))
    return buf.tobytes()


def 做头(流):
    原图 = cv2.imdecode(np.array([ord(i) for i in 流], dtype=np.uint8), cv2.IMREAD_COLOR)
    r, c = 原图.shape[:2]
    if r > c:
        r0 = int((r - c) / 2)
        切片 = 原图[r0:r0 + c, 0:c]
    else:
        c0 = int((c - r) / 2)
        print()
        切片 = 原图[0:r, c0:c0 + r]
    大头像 = cv2.resize(切片, (512, 512), interpolation=cv2.INTER_AREA)
    小头像 = cv2.resize(切片, (128, 128), interpolation=cv2.INTER_AREA)
    return 编码为webp(大头像), 编码为webp(小头像)
