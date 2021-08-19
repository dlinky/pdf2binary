import os
import sys
import cv2
import numpy as np
from pdf2image import convert_from_path


def create_folder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


def empty(self):
    pass


# paths
path_dir = os.getcwd()
path_dir = path_dir.replace(os.sep, '/') + '/'
image_dir = path_dir + 'images/'
create_folder(image_dir)
original_dir = image_dir + 'original/'
create_folder(original_dir)
sharpen_dir = image_dir + 'sharpen/'
create_folder(sharpen_dir)
result_dir = image_dir + 'result/'
create_folder(result_dir)


# sharpening
sharpening = np.array([[-1, -1, -1, -1, -1],
                       [-1, 2, 2, 2, -1],
                       [-1, 2, 9, 2, -1],
                       [-1, 2, 2, 2, -1],
                       [-1, -1, -1, -1, -1]]) / 9.0


def main(pdf):
    # pdf to image
    images_from_pdf = convert_from_path(path_dir + pdf)
    print('converted pdf to image')

    # sharpening
    images = []
    for page, img in enumerate(images_from_pdf):
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(original_dir + 'page_%d.jpg' % (page+1), img)
        img = cv2.filter2D(img, -1, sharpening)
        cv2.imwrite(sharpen_dir + 'page_%d.jpg' % (page + 1), img)
        images.append(img)
    print('sharpened images')

    threshold = 0
    page = 0
    windowName = 'threshold'
    cv2.namedWindow(windowName)
    cv2.createTrackbar('threshold', windowName, threshold, 255, empty)
    cv2.createTrackbar('page', windowName, page, len(images)-1, empty)

    # threshold 수동으로 찾기
    while True:
        if cv2.waitKey(1) == 27:
            break
        threshold = cv2.getTrackbarPos('threshold', windowName)
        page = cv2.getTrackbarPos('page', windowName)

        temp = images[page].copy()
        _, temp1 = cv2.threshold(temp, threshold, 255, cv2.THRESH_TRUNC)
        _, temp2 = cv2.threshold(temp, threshold, 255, cv2.THRESH_BINARY)
        temp = cv2.add(temp1, temp2)
        temp = cv2.resize(temp, (0, 0), fx=0.4, fy=0.4)
        cv2.imshow(windowName, temp)
    cv2.destroyAllWindows()

    # threshold 적용 & 저장
    for i, img in enumerate(images):
        temp = img.copy()
        _, temp1 = cv2.threshold(temp, threshold, 255, cv2.THRESH_TRUNC)
        _, temp2 = cv2.threshold(temp, threshold, 255, cv2.THRESH_BINARY)
        temp = cv2.add(temp1, temp2)
        cv2.imwrite(result_dir + 'page_%d.jpg' % (i+1), temp)
    print('thresholded images')
    print('done!')


argv = sys.argv
if len(sys.argv) == 1:
    main('sample.pdf')
else:
    main(sys.argv[1])