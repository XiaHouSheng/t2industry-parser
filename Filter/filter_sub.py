import cv2
from PIL import Image
import numpy as np
import os

target_path = "./config/standard_images/"
classes = os.listdir(target_path)

standard = {}
standard_offset = {
    "battery": (5, 0),
    "powder": (-5, -5),
}

rotate_cls_classes = [
    "left_bottom",
    "left_top",
    "right_bottom",
    "right_top",
]


for class_name in classes:
    class_path = os.path.join(target_path, class_name)
    sub_images = {}
    for img_name in os.listdir(class_path):
        img_path = os.path.join(class_path, img_name)
        img = cv2.imread(img_path)
        sub_images[img_name] = img
    standard[class_name] = sub_images

def getClasses():
    return classes

def hsv_match_score(img1, img2, offset_x=0, offset_y=0):
    # 取中心 区域，支持偏移
    cx, cy = 32 + offset_x, 32 + offset_y
    half = 8
    roi1 = img1[cy - half:cy + half, cx - half:cx + half]
    roi2 = img2[cy - half:cy + half, cx - half:cx + half]

    hsv1 = cv2.cvtColor(roi1, cv2.COLOR_BGR2HSV)
    hsv2 = cv2.cvtColor(roi2, cv2.COLOR_BGR2HSV)
    hist1 = cv2.calcHist([hsv1],[0,1],None,[50,60],[0,180,0,256])
    hist2 = cv2.calcHist([hsv2],[0,1],None,[50,60],[0,180,0,256])
    cv2.normalize(hist1, hist1)
    cv2.normalize(hist2, hist2)
    score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return score

def find_best_match(img, class_):
    best_match = None
    best_score = -1
    img = cv2.resize(img, (64, 64))

    for img_name, std_img in standard[class_].items():
        if class_ in standard_offset:
            offset_x, offset_y = standard_offset[class_]
        else:
            offset_x, offset_y = 0, 0
        score = hsv_match_score(img, std_img, offset_x, offset_y)
        if score > best_score:
            best_score = score
            best_match = img_name
    return best_match, best_score

def find_rotate_match(img: np.ndarray, range_out=5, band=3):

    height, width, _ = img.shape

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    top = np.mean(gray[range_out:range_out+band, :])
    bottom = np.mean(gray[height-range_out-band:height-range_out, :])
    left = np.mean(gray[:, range_out:range_out+band])
    right = np.mean(gray[:, width-range_out-band:width-range_out])

    lines = {
        "top": top,
        "bottom": bottom,
        "left": left,
        "right": right
    }

    sorted_lines = sorted(lines.items(), key=lambda x: x[1])

    top1, top2 = sorted_lines[0][0], sorted_lines[1][0]

    if top1 in ["left", "right"]:
        return f"{top1}_{top2}"
    else:
        return f"{top2}_{top1}"



if __name__ == "__main__":
    target_path = "./ScreenShots/target_test_single.png"
    image = Image.open(target_path).convert("RGB")
    ndarray = np.array(image)
    output = find_rotate_match(ndarray)
    print(output)





