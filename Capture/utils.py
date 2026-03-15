import numpy as np
import cv2
import os
from PIL import Image
from pathlib import Path

def isMove(arrayfirst, arraynext):
    img1_float = np.float32(arrayfirst)
    img2_float = np.float32(arraynext)
    gray1 = cv2.cvtColor(img1_float, cv2.COLOR_RGB2GRAY)
    gray2 = cv2.cvtColor(img2_float, cv2.COLOR_RGB2GRAY)
    shift, response = cv2.phaseCorrelate(gray1, gray2)
    return shift, response

def pieceTogetherVertical(arrayroot, arraynext, bias):
    height, width, channels = arraynext.shape
    start_height = height - abs(np.floor(int(bias)))
    arraynext_crop = arraynext[start_height:height, :, :]
    output = np.concatenate((arrayroot, arraynext_crop), axis=0)
    return output
    
def pieceTogetherHorizontal(arrayroot, arraynext, bias):
    height, width, channels = arraynext.shape
    start_width = width - abs(np.floor(int(bias)))
    arraynext_crop = arraynext[:, start_width:width, :]
    output = np.concatenate((arrayroot, arraynext_crop), axis=1)
    return output

def cropVerticalScroll(ndarray):
    height, width, channels = ndarray.shape
    array_crop = ndarray[30:height-24, :, :]
    return array_crop

def cropHorizontalScroll(ndarray):
    height, width, channels = ndarray.shape
    array_crop = ndarray[:, 28:width-15, :]
    return array_crop

def cropImageScroll2(ndarray):
    array_crop = cropHorizontalScroll(ndarray)
    array_crop = cropVerticalScroll(array_crop)
    return array_crop

def divideToPieces(ndarray, w_index, h_index, path="./pieces/"):
    img_height, img_width, channels = ndarray.shape
    piece_width, piece_height = img_width / w_index, img_height / h_index
    for i in range(w_index):
        for j in range(h_index):
            piece = ndarray[int(j * piece_height):int((j + 1) * piece_height), int(i * piece_width):int((i + 1) * piece_width), :]
            filepath = path + f"piece_{i}_{j}.png"
            file = open(filepath, "wb")
            img = Image.fromarray(piece)
            img.save(file)
            file.close()

def rotateImageASave():
    #capture = Capture("Endfield", 100)
    path = "./datasets/splitter_cell/"
    #遍历path下所有文件夹的子文件并，使用pillow打开rotate三个方向分别保存
    for class_path in os.listdir(path):
        class_path = os.path.join(path, class_path)
        for file in os.listdir(class_path):
            file_path = os.path.join(class_path, file)
            img = Image.open(file_path)
            for i in range(3):
                img_rotate = img.rotate((i+1) * 90)
                img_rotate.save(os.path.join(class_path, f"{file.split('.')[0]}_{i}.png"))

def pasteImageGenerate():
    path_image_bg = "./ScreenShots/bg_132.png"
    path_dir_pipe = "./splices/pipe/"
    path_dir_belt = "./splices/belt/"
    path_dir_belt_model = "./splices/belt_model/"
    path_file_save = "./splices/together_result/"
    image_bg = Image.open(path_image_bg).convert("RGBA")
    #pipe and belt
    for pipe_name in os.listdir(path_dir_pipe):
        for belt_name in os.listdir(path_dir_belt):
            pipe_path = path_dir_pipe + pipe_name
            belt_path = path_dir_belt + belt_name
            pipe_img = Image.open(pipe_path).convert("RGBA")
            belt_img = Image.open(belt_path).convert("RGBA")
            #paste pipe and belt
            image_bg_copy = image_bg.copy()
            image_bg_copy.paste(belt_img, (2, 0), belt_img)
            image_bg_copy.paste(pipe_img, (0, 0), pipe_img)
            pipe_img.close()
            belt_img.close()
            #save
            file = open(os.path.join(path_file_save, f"{pipe_name.split('.')[0]}_{belt_name.split('.')[0]}.png"), "wb")
            image_bg_copy.save(file)
            file.close()
    # pipe and model
    for pipe_name in os.listdir(path_dir_pipe):
        for belt_model_name in os.listdir(path_dir_belt_model):
            pipe_path = path_dir_pipe + pipe_name
            belt_model_path = path_dir_belt_model + belt_model_name
            pipe_img = Image.open(pipe_path).convert("RGBA")
            belt_model_img = Image.open(belt_model_path).convert("RGBA")
            #paste pipe and belt_model
            image_bg_copy = image_bg.copy()
            image_bg_copy.paste(belt_model_img, (2, 0), belt_model_img)
            image_bg_copy.paste(pipe_img, (0, 0), pipe_img)
            pipe_img.close()
            belt_model_img.close()
            #save
            file = open(os.path.join(path_file_save, f"{pipe_name.split('.')[0]}_{belt_model_name.split('.')[0]}.png"), "wb")
            image_bg_copy.save(file)
            file.close()

def testMatchIcon():
    target_path = "./ScreenShots/test_target_icon.png"
    target_img = cv2.imread(target_path)
    if target_img is None:
        print(f"无法读取目标图片: {target_path}")
        return
    
    base_dir = Path("./datasets/output_cls/train")
    if not base_dir.exists():
        print(f"目录不存在: {base_dir}")
        return
    
    orb = cv2.ORB_create()
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    kp1, des1 = orb.detectAndCompute(target_img, None)
    if des1 is None:
        print("目标图片未检测到特征点")
        return
    
    results = []
    for folder in base_dir.iterdir():
        if folder.is_dir():
            filename = folder.name
            icon_path = folder / f"{filename}.png"
            if icon_path.exists():
                icon_img = cv2.imread(str(icon_path))
                if icon_img is not None:
                    kp2, des2 = orb.detectAndCompute(icon_img, None)
                    if des2 is not None:
                        matches = bf.match(des1, des2)
                        score = len([m for m in matches if m.distance < 50])
                        results.append({
                            'filename': filename,
                            'score': score,
                            'matches': len(matches)
                        })
    
    if results:
        best_match = max(results, key=lambda x: x['score'])
        print(f"top1: {best_match['filename']}, score = {best_match['score']}")
    else:
        print("未找到任何匹配的图标")

if __name__ == "__main__":
    testMatchIcon()


    

    
            



