import cv2
import numpy as np
import pickle

dstBgColor = 255
dstSymColor = 0

def col2val(color):
    '''
    Преобразуем три компонента цвета в беззнаковое целое.
    '''
    r, g, b = color
    return (r & 0xF8) + (g << 8) + ((b & 0xF8) << 16)
    #return (r) + (g << 8) + ((b) << 16)

def val2col(value):
    '''
    Извлекаем три компонента цвета из беззнакового целого.
    '''
    r = value & 0xFF
    g = (value & 0xFF00) >> 8
    b = (value & 0xFF0000) >> 16
    return (r, g, b)

def rgb2flat(src):
    '''
    Преобразуем RGB изображение в массив того же размера,
    но цвет пикселя храним как 32-битное беззнаковое целое число.
    '''
    h, w, p = src.shape
    dst = np.zeros((h, w), np.uint32)
    for y in range(h):
        for x in range(w):
            dst[y, x] = col2val(src[y, x])
    return dst

def flat2rgb(src):
    '''
    Преобразуем массив 32-битных беззнаковых целых чисел
    в RGB изображение того же размера.
    '''
    h, w = src.shape
    dst = np.zeros((h, w, 3), np.uint8)
    for y in range(h):
        for x in range(w):
            dst[y, x] = val2col(src[y, x])
    return dst

def filterLines(ksize, src, captchaValue):
    print(f"Начинается очистка капчи, ядро: {ksize}")

    # Получаем размер исходного массива
    h, w = src.shape

    print(f"  Исходное изображение:")
    print(f"    Размер: {w}x{h}")

    # Задаём размеры ядра
    kernel_w = ksize
    kernel_h = ksize
    print(f"  Размер ядра: {kernel_w}x{kernel_h}")

    # Вычисляем крайние положения, которые может занимать
    # левый верхний пиксел ядра
    left = 0
    right = w - kernel_w - 1
    top = 0
    bottom = h - kernel_h - 1

    print(f"  Ограничение окна для вернего левого угла ядра:")
    print(f"    Слева: {left}")
    print(f"    Сверху: {top}")
    print(f"    Справа: {right}")
    print(f"    Снизу: {bottom}")

    # В этом ассоциативном массиве (карте) мы будем хранить
    # количество пикселов соответствующего цвета
    # colors = {}
    # colors = {15263991: 10178347, 10634705: 31755, 9124788: 359510, 5341968: 2565, 12411786: 22363, 9145236: 362, 6685184: 13641, 3289813: 22668, 1221761: 22666, 6500756: 19868, 11908545: 246670, 7551404: 160297, 7584280: 28336, 14447520: 54, 11283503: 1343, 4762545: 161409, 10392943: 235751, 12874545: 41302, 10092031: 98, 13157836: 40, 8290005: 925, 7821389: 6205, 8934975: 29399, 8872790: 12225, 12097415: 18, 12032136: 7423, 12032137: 968, 11966601: 1044, 11966602: 257, 11966603: 613, 11901067: 528, 11901068: 391, 11901324: 366, 11835789: 273, 11835790: 789}
    # colors = {15263991: 438847, 9124788: 12934, 11908545: 11161, 7551404: 6759, 4762545: 5450, 10392943: 8855, 7821389: 184, 8934975: 1011, 8872790: 695, 12032136: 301, 11835790: 102, 11770255: 70, 10003393: 10}
    colors = {}
    # Вычисляем массив, только если он пуст,
    # иначе пропускаем вычисления и загружаем карту
    pixelMapFilename = f'data/{captchaValue}.map'
    colorMapFilename = f'data/{captchaValue}.colors'

    map = {}
    colors = {}

    try:
        #raise "noload"
        map = np.load(f"{pixelMapFilename}.npy")
        with open(colorMapFilename, 'rb') as fd:
            colors = pickle.load(fd)
    except:
        print(f"  Не удалось загрузить предыдущие результаты вычислений")

        # Создаём массив таких-же размеров, но 8-битных целых
        map = np.zeros((h, w), np.uint8)
        colors.clear()

        print(f"  Ведётся поиск областей одинакового цвета, размером с ядро...")
        for y in range(top, bottom):
            for x in range(left, right):
                color = src[y, x]
                good = True
                for ky in range(y, y + kernel_h):
                    for kx in range(x, x + kernel_h):
                        good = good and (color == src[ky, kx])
                        if not good: break
                    if not good: break
                map[y, x] = 1 if good else 0
                if not good: continue
                count = colors.get(color, 0)
                colors[color] = count + 1
        print(f"  Сохранение результатов вычислений")
        np.save(pixelMapFilename, map)
        with open(colorMapFilename, 'wb') as fd:
            pickle.dump(colors, fd)

    # Вычисляем цвет фона, предполагая что площадь (количество пикселов)
    # цвета фона должно быть больше, чем площадь любого символа.
    bgColor = None
    maxCount = 0
    for color in colors:
        count = colors[color]
        if count > maxCount:
            bgColor = color
            maxCount = count

    dst = np.full_like(src, 128)
    for y in range(h):
        for x in range(w):
            pixelColor = src[y, x]
            if (pixelColor != bgColor) and map[y, x]:
                dst[y, x] = pixelColor

    return dst

def main():
    capId = 25753 # 99448
    ksize = 5

    image = cv2.imread(f'data/bot/{capId}.jpg')
    cv2.imshow('Src', image)
    cv2.waitKey(1)

    src = cv2.blur(image, (ksize, ksize))

    flat_src = rgb2flat(src)

    rest_src = flat2rgb(flat_src)
    cv2.imshow('Src-Rest', rest_src)
    cv2.waitKey(1)

    flat_dst = filterLines(ksize, flat_src, capId)

    dst = flat2rgb(flat_dst)
    cv2.imshow('Dst', dst)
    cv2.waitKey(1)
    
    cv2.imwrite(f'data/{capId}.png', dst)

    cv2.waitKey(0)

if __name__ == '__main__':
    main()
