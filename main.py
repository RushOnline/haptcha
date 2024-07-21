import cv2
import numpy as np

def isPixelsEqual(first, second):
    r1, g1, b1 = first
    r2, g2, b2 = second
    return ((r1 == r2) and (g1 == g2) and (b1 == b2))

def filterLines(src):
    h, w, p = src.shape
    print(f"{w}x{h} @ {p}")
    dst = np.zeros((h, w, 1), np.uint8)
    print(f"{dst.shape}")

    # РАБОТАЕТ! НЕ ТРОГАЙ!
    # for y in range(h):
    #     for x in range(w):
    #         r, g, b = src[y, x]


    kernel_w = 20
    kernel_h = 20

    left = 0
    right = w - kernel_w - 1
    top = 0
    bottom = h - kernel_h - 1

    for y in range(top, bottom):
        for x in range(left, right):
            print(f"добрались до {x}, {y}")
            # src[x, y])
            color = src[y, x]
            good = True
            for ky in range(y, y + kernel_h):
                for kx in range(x, x + kernel_h):
                    good = good and isPixelsEqual(color, src[ky, kx])
                    if not good: break
                if not good: break
            dst[y, x] = 255 if good else 0
    return dst

def main():
    print('main()')
    image = cv2.imread('/home/rush/workspace/rush/rabot/data/nebot/37191.png')
    cv2.imshow('Main', image)
    clear = filterLines(image)
    cv2.imshow('Dest', clear)
    cv2.waitKey(0)

if __name__ == '__main__':
    main()
