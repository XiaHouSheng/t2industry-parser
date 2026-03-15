from PIL import Image
from ultralytics import YOLO
import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
#分类模型
model = YOLO(str(BASE_DIR / "model" / "yolov8n-cls-splitter-cell.pt"))

#多层划分模型
model_seg = YOLO("./model/yolov8n-seg-splitter-cell.pt")

#旋转分类模型
model_rotate = YOLO("./model/yolov8n-rotate-cls.pt")

#机器检测模型
model_detect = YOLO("./model/yolov8n-machine-detect.pt")

#产物分类模型 ./model/yolov8n-product-cls.pt
model_product = YOLO("./model/yolov8n-product-cls.pt")

#机器旋转分类模型  ./model/yolov8n-machine-rotate-cls.pt
model_machie_rotate = YOLO("./model/yolov8n-machine-rotate-cls.pt")

#管道 belt 旋转分类模型 yolov8n-pipe-belt-rotate-cls.pt
model_pipe_belt_rotate = YOLO("./model/yolov8n-pipe-belt-rotate-cls.pt")


def trainClassfier():
    results = model.train(
        # 基础参数
        data="./datasets/splitter_cell",  # 你的12张图数据集路径
        epochs=200,                  # 少量轮数避免过拟合
        imgsz=132,                  # 分类模型标准尺寸
        batch=4,                    # 极小批次适配小数据
        lr0=0.001,                  # 低学习率更稳定
        dropout=0.2,                # 抑制过拟合
        device=0,                   # 使用GPU训练
        # 内置增强核心配置（适配12张图）
        hsv_h=0.03,                 # 提高色调调整幅度
        hsv_s=0.9,                  # 提高饱和度调整幅度
        hsv_v=0.6,                  # 提高明度调整幅度
        degrees=0,               # 增大旋转角度
        translate=0.15,             # 增大平移范围
        scale=0.6,                  # 增大缩放范围
        shear=3.0,                  # 增大剪切角度
        flipud=0.2,                 # 开启垂直翻转（默认关闭）
        fliplr=0.5,                 # 保持水平翻转概率
        # 其他优化
        patience=3,                 # 早停机制
        val=False,                  # 不划分验证集（12张图太少）
        save=True,                   # 保存最佳模型
    )
    model.save("./model/yolov8n-cls-splitter-cell.pt")

def trainSegModel():
    results = model_seg.train(
        # 基础参数
        data="./yaml/seg_cell.yaml",  # 你的12张图数据集路径
        epochs=200,                  # 少量轮数避免过拟合
        imgsz=132,                  # 分类模型标准尺寸
        batch=16,                    # 极小批次适配小数据
        lr0=0.001,                  # 低学习率更稳定
        dropout=0.2,                # 抑制过拟合
        device=0,                   # 使用GPU训练
        # 内置增强核心配置（适配12张图）
        hsv_h=0.03,                 # 提高色调调整幅度
        hsv_s=0.9,                  # 提高饱和度调整幅度
        hsv_v=0.6,                  # 提高明度调整幅度
        degrees=0,               # 增大旋转角度
        translate=0.15,             # 增大平移范围
        scale=0.6,                  # 增大缩放范围
        shear=3.0,                  # 增大剪切角度
        flipud=0.2,                 # 开启垂直翻转（默认关闭）
        fliplr=0.5,                 # 保持水平翻转概率
        # 其他优化
        patience=3,                 # 早停机制
        val=False,                  # 不划分验证集（12张图太少）
        save=True,                   # 保存最佳模型
    )
    model_seg.save("./model/yolov8n-seg-splitter-cell.pt")
    print(results)

def trainRotateCls():
    results = model_rotate.train(
        # 基础参数
        data="./yaml/rotate_cls.yaml",  # 你的12张图数据集路径
        epochs=200,                  # 少量轮数避免过拟合
        imgsz=132,                  # 分类模型标准尺寸
        batch=4,                    # 极小批次适配小数据
        lr0=0.00001,                  # 低学习率更稳定
        dropout=0.2,                # 抑制过拟合
        device=0,                   # 使用GPU训练
        mosaic=0,
        # 内置增强核心配置（适配12张图）
        hsv_h=0.03,                 # 提高色调调整幅度
        hsv_s=0.9,                  # 提高饱和度调整幅度
        hsv_v=0.6,                  # 提高明度调整幅度
        degrees=0,               # 增大旋转角度
        translate=0.15,             # 增大平移范围
        scale=0.6,                  # 增大缩放范围
        shear=0,                  # 增大剪切角度
        patience=3,                 # 早停机制
        val=False,                  # 不划分验证集（12张图太少）
        save=True,                   # 保存最佳模型
    )
    model_rotate.save(str(BASE_DIR / "model" / "yolov8n-rotate-cls.pt"))
    print(results)

def trainMachineDetect():
    results = model_detect.train(
        # 基础参数
        data="./yaml/machine_detect.yaml",  # 你的12张图数据集路径
        epochs=200,                  # 少量轮数避免过拟合
        batch=4,                    # 极小批次适配小数据
        lr0=0.001,                  # 低学习率更稳定
        dropout=0.2,                # 抑制过拟合
        device=0,                   # 使用GPU训练
        # 内置增强核心配置（适配12张图）
        hsv_h=0.03,                 # 提高色调调整幅度
        hsv_s=0.9,                  # 提高饱和度调整幅度
        hsv_v=0.6,                  # 提高明度调整幅度
        translate=0.15,             # 增大平移范围
        scale=0.6,                  # 增大缩放范围
        save=True,                   # 保存最佳模型
    )
    model_detect.save(str(BASE_DIR / "model" / "yolov8n-machine-detect.pt"))
    print(results)

def trainProductCls():
    results = model_product.train(
        # 基础参数
        data="./datasets/output_cls",  # 你的12张图数据集路径
        epochs=300,                  # 少量轮数避免过拟合
        imgsz=128,                  # 分类模型标准尺寸
        batch=4,                    # 极小批次适配小数据
        lr0=0.001,                  # 低学习率更稳定
        dropout=0.2,                # 抑制过拟合
        device=0,                   # 使用GPU训练
        # 内置增强核心配置（适配12张图）
        mosaic=0,
        mixup=0,
        hsv_h=0.0,                 # 提高色调调整幅度
        hsv_s=0.0,                  # 提高饱和度调整幅度
        hsv_v=0.0,                  # 提高明度调整幅度
        translate=0.15,             # 增大平移范围
        scale=0.6,                  # 增大缩放范围
        save=True,                   # 保存最佳模型
        val=False,                  # 不划分验证集（12张图太少）
    )
    model_product.save(str(BASE_DIR / "model" / "yolov8n-product-cls.pt"))
    print(results)

def trainMachineRotate():
    results = model_machie_rotate.train(
        # 基础参数
        data="./datasets/machine_rotate",  # 你的12张图数据集路径
        epochs=200,                  # 少量轮数避免过拟合
        imgsz=64,                  # 分类模型标准尺寸
        batch=4,                    # 极小批次适配小数据
        lr0=0.0001,                  # 低学习率更稳定
        dropout=0.2,                # 抑制过拟合
        device=0,                   # 使用GPU训练
        # 内置增强核心配置（适配12张图）
        hsv_h=0.03,                 # 提高色调调整幅度
        hsv_s=0.9,                  # 提高饱和度调整幅度
        hsv_v=0.6,                  # 提高明度调整幅度
        translate=0.3,             # 增大平移范围
        scale=0.6,                  # 增大缩放范围
        save=True,                   # 保存最佳模型
    )
    model_machie_rotate.save(str(BASE_DIR / "model" / "yolov8n-machine-rotate-cls.pt"))
    print(results)

def trainBeltAPipeRotateCls():
    results = model_pipe_belt_rotate.train(
        # 基础参数
        data="./datasets/pipe_belt_cls",  # 你的12张图数据集路径
        epochs=200,                  # 少量轮数避免过拟合
        imgsz=132,                  # 分类模型标准尺寸
        batch=4,                    # 极小批次适配小数据
        lr0=0.001,                  # 低学习率更稳定
        dropout=0.2,                # 抑制过拟合
        device=0,                   # 使用GPU训练
        mosaic=0,
        # 内置增强核心配置（适配12张图）
        hsv_h=0.03,                 # 提高色调调整幅度
        hsv_s=0.9,                  # 提高饱和度调整幅度
        hsv_v=0.6,                  # 提高明度调整幅度
        degrees=0,               # 增大旋转角度
        translate=0.15,             # 增大平移范围
        scale=0.6,                  # 增大缩放范围
        shear=3.0,                  # 增大剪切角度
        patience=3,                 # 早停机制
        val=False,                  # 不划分验证集（12张图太少）
        save=True,                   # 保存最佳模型
    )
    model_rotate.save(str(BASE_DIR / "model" / "yolov8n-pipe-belt-rotate-cls.pt"))
    print(results)


def valRotateCls(ndarrays):
    results = model_rotate(ndarrays)
    output = []
    for result in results:
        if len(result.boxes) > 0:
            top1 = max([b for b in result.boxes], key=lambda b: b.conf[0])
            class_id = int(top1.cls[0])
            class_name = result.names[class_id]
            conf = float(top1.conf[0])
            output.append({'class_id': class_id, 'class_name': class_name, 'conf': conf})
    print(f"[RotateCls] 处理 {len(ndarrays)} 个样本，top1: {output[0]['class_name'] if output else 'None'} {output[0]['conf'] if output else 0:.2f}")
    return output

def valMachineDetect(ndarrays):
    results = model_detect(ndarrays)
    output = []
    for result in results:
        if len(result.boxes) > 0:
            top1 = max([b for b in result.boxes], key=lambda b: b.conf[0])
            class_id = int(top1.cls[0])
            class_name = result.names[class_id]
            conf = float(top1.conf[0])
            output.append({'class_id': class_id, 'class_name': class_name, 'conf': conf, 'boxes': result.boxes})
    print(f"[MachineDetect] 处理 {len(ndarrays)} 个样本，top1: {output[0]['class_name'] if output else 'None'} {output[0]['conf'] if output else 0:.2f}")
    return output

def valSegModel(ndarrays):
    results = model_seg(ndarrays)
    all_segmented = []
    for i, result in enumerate(results):
        segmented_images = []
        confs = []
        if result.masks is not None:
            for j, mask in enumerate(result.masks):
                box = result.boxes[j]
                mask_data = mask.data[0].cpu().numpy()
                img = ndarrays[i]
                mask_resized = cv2.resize(mask_data.astype(np.uint8), (img.shape[1], img.shape[0]))
                masked_img = cv2.bitwise_and(img, img, mask=mask_resized)
                x, y, w, h = map(int, box.xywh[0])
                x1 = max(0, x - w // 2)
                y1 = max(0, y - h // 2)
                x2 = min(img.shape[1], x + w // 2)
                y2 = min(img.shape[0], y + h // 2)
                cropped = masked_img[y1:y2, x1:x2]
                cropped[cropped == 0] = 255
                segmented_images.append(cropped)
                confs.append(float(box.conf[0]))
        all_segmented.append({"segmented_images": segmented_images, "confs": confs})
    print(f"[SegModel] 处理 {len(ndarrays)} 个样本，分割 {sum(len(s['segmented_images']) for s in all_segmented)} 个区域")
    return all_segmented

def valClassModel(ndarrays):
    results = model(ndarrays)
    output = []
    for result in results:
        if result.probs is not None:
            class_id = int(result.probs.top1)
            class_name = result.names[class_id]
            conf = float(result.probs.top1conf)
            output.append({'class_id': class_id, 'class_name': class_name, 'conf': conf})
    print(f"[ClassModel] 处理 {len(ndarrays)} 个样本，top1: {output[0]['class_name'] if output else 'None'} {output[0]['conf'] if output else 0:.2f}")
    return output

def valProductCls(ndarrays):
    results = model_product(ndarrays)
    output = []
    for result in results:
        if result.probs is not None:
            class_id = int(result.probs.top1)
            class_name = result.names[class_id]
            conf = float(result.probs.top1conf)
            output.append({'class_id': class_id, 'class_name': class_name, 'conf': conf})
    print(f"[ProductCls] 处理 {len(ndarrays)} 个样本，top1: {output[0]['class_name'] if output else 'None'} {output[0]['conf'] if output else 0:.2f}")
    return output

def valMachineRotateCls(ndarrays):
    results = model_machie_rotate(ndarrays)
    output = []
    for result in results:
        if result.probs is not None:
            class_id = int(result.probs.top1)
            class_name = result.names[class_id]
            conf = float(result.probs.top1conf) 
            output.append({'class_id': class_id, 'class_name': class_name, 'conf': conf})
    print(f"[MachineRotateCls] 处理 {len(ndarrays)} 个样本，top1: {output[0]['class_name'] if output else 'None'} {output[0]['conf'] if output else 0:.2f}")
    return output

def valPipeBeltRotateCls(ndarrays):
    results = model_pipe_belt_rotate(ndarrays)
    output = []
    for result in results:
        if result.probs is not None:
            class_id = int(result.probs.top1)
            class_name = result.names[class_id]
            conf = float(result.probs.top1conf)
            output.append({'class_id': class_id, 'class_name': class_name, 'conf': conf})
    print(f"[PipeBeltRotateCls] 处理 {len(ndarrays)} 个样本，top1: {output[0]['class_name'] if output else 'None'} {output[0]['conf'] if output else 0:.2f}")
    return output

if __name__ == "__main__":
    pass
    
