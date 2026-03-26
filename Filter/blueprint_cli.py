import argparse
import json
import numpy as np
import cv2
from PIL import Image
from filter import *
from filter_sub import *
from filter_rotate_converter import *
from filter_process import convert_blueprint
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent

machine_detect_classes = [
    "machine",
    "power_pole",
    "power_station",
    "res_in_port",
    "res_out_port",
    "storage_box"
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Blueprint image parser"
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Blueprint image path"
    )

    parser.add_argument(
        "-c",
        "--config",
        default=str(BASE_DIR / "config" / "machine_config" / "product_to_factory.json"),
        help="Product to factory config json"
    )

    parser.add_argument(
        "--grid-x",
        type=int,
        default=16
    )

    parser.add_argument(
        "--grid-y",
        type=int,
        default=17
    )

    parser.add_argument(
        "--save",
        action="store_true",
        default=True
    )

    return parser.parse_args()

def main():

    args = parse_args()

    # 读取蓝图
    target_img = Image.open(args.input).convert("RGB")
    target_ndarray = np.array(target_img)

    # 读取配置
    recipe_config = json.load(open(args.config, "r"))

    w_index = args.grid_x
    h_index = args.grid_y

    height, width, _ = target_ndarray.shape

    grid_width = width // w_index
    grid_height = height // h_index
    final_cell_size = (grid_height + grid_width) // 2

    target_batch = [target_ndarray]

    # -----------------------------
    # 机器检测
    # -----------------------------
    result_machine_detect = valMachineDetect(target_batch)

    machine_detect_boxes = result_machine_detect[0]['boxes']
    machine_detect_boxes = [
        box for box in machine_detect_boxes
        if box.conf[0] >= 0.7
    ]

    skip_range = []
    data = []

    for box in machine_detect_boxes:

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        class_name = machine_detect_classes[int(box.cls[0])]

        box_width = x2 - x1
        box_height = y2 - y1

        grid_w = int(np.around(box_width / final_cell_size))
        grid_h = int(np.around(box_height / final_cell_size))

        start_x = round(x1 / final_cell_size)
        start_y = round(y1 / final_cell_size)

        for i in range(grid_w):
            for j in range(grid_h):
                skip_range.append((start_x + i, start_y + j))

        # power_pole / power_station
        if box.cls[0] == 1 or box.cls[0] == 2:

            data.append({
                "class_name": None,
                "machine_detect_type": class_name,
                "producer": None,
                "rotate": 0,
                "x": start_x,
                "y": start_y,
                "w": grid_w,
                "h": grid_h,
            })

            continue

        # -----------------------------
        # 中心 icon 分类
        # -----------------------------
        average_x = (x1 + x2) / 2
        average_y = (y1 + y2) / 2

        start_crop_x = int(average_x - (final_cell_size / 2))
        start_crop_y = int(average_y - (final_cell_size / 2))

        end_crop_x = start_crop_x + final_cell_size
        end_crop_y = start_crop_y + final_cell_size

        ndarray_product_icon = target_ndarray[
            start_crop_y:end_crop_y,
            start_crop_x:end_crop_x
        ]

        result_product_cls = valProductCls([ndarray_product_icon])[0]

        pre_class_name = result_product_cls['class_name']
        pre_conf = result_product_cls['conf']

        # -----------------------------
        # rotate 判断
        # -----------------------------
        rotate_id = 0

        if box.cls[0] == 0 or box.cls[0] == 5:

            start_crop_x_top = int(x1 + final_cell_size)
            start_crop_y_top = int(y1)

            end_crop_x_top = start_crop_x_top + final_cell_size
            end_crop_y_top = start_crop_y_top + final_cell_size

            start_crop_x_side = int(x1)
            start_crop_y_side = int(y1 + final_cell_size)

            end_crop_x_side = start_crop_x_side + final_cell_size
            end_crop_y_side = start_crop_y_side + final_cell_size

            ndarray_side_port = target_ndarray[
                start_crop_y_side:end_crop_y_side,
                start_crop_x_side:end_crop_x_side
            ]

            ndarray_top_port = target_ndarray[
                start_crop_y_top:end_crop_y_top,
                start_crop_x_top:end_crop_x_top
            ]

            machine_rotate_detect_batch = [
                ndarray_top_port,
                ndarray_side_port
            ]

            result_machine_rotate = valMachineRotateCls(
                machine_rotate_detect_batch
            )

            top_id, top_class_name, top_conf = result_machine_rotate[0].values()
            side_id, side_class_name, side_conf = result_machine_rotate[1].values()

            if float(top_conf) > float(side_conf):

                if top_class_name == "top_in":
                    rotate_id = 0
                else:
                    rotate_id = 2

            else:

                if side_class_name == "side_in":
                    rotate_id = 3
                else:
                    rotate_id = 1

        if box.cls[0] == 3 or box.cls[0] == 4:

            if grid_w > grid_h:
                rotate_id = 0
            else:
                rotate_id = 1

        # icon 匹配
        if pre_class_name in getClasses():

            convert_bgr = cv2.cvtColor(
                ndarray_product_icon,
                cv2.COLOR_RGB2BGR
            )

            best_match, best_score = find_best_match(
                convert_bgr,
                pre_class_name
            )

            pre_class_name = best_match.split(".")[0]
            pre_conf = best_score

        data.append({

            "class_name": pre_class_name,
            "machine_detect_type": machine_detect_classes[int(box.cls[0])],
            "producer": recipe_config[pre_class_name],
            "rotate": rotate_id,
            "x": start_x,
            "y": start_y,
            "w": grid_w,
            "h": grid_h,
        })

    # -----------------------------
    # belt / pipe 解析
    # -----------------------------
    data_belts = []

    for xindex in range(w_index):
        for yindex in range(h_index):

            if (xindex, yindex) in skip_range:
                continue

            start_crop_x = xindex * final_cell_size
            start_crop_y = yindex * final_cell_size

            end_crop_x = start_crop_x + final_cell_size
            end_crop_y = start_crop_y + final_cell_size

            grid_ndarray = target_ndarray[
                start_crop_y:end_crop_y,
                start_crop_x:end_crop_x
            ]

            if np.std(grid_ndarray) < 15:
                continue

            seg_outputs = valSegModel([grid_ndarray])[0]

            confs = seg_outputs['confs']
            seg_images = seg_outputs['segmented_images']

            seg_images = [
                img for img, conf in zip(seg_images, confs)
                if conf >= 0.5
            ]

            if len(seg_images) == 0:
                continue

            grid_class_outputs = valClassModel(seg_images)

            muti_layer = []

            for i in range(len(grid_class_outputs)):

                class_id, class_name, conf = grid_class_outputs[i].values()

                class_name_split = class_name.split("_")

                seg_image = seg_images[i]
                seg_image = cv2.cvtColor(seg_image, cv2.COLOR_BGR2RGB)

                if len(class_name_split) == 1:

                    rotate_cls_output = valRotateCls([seg_image])

                    rotate_cls_output.sort(
                        key=lambda x: x['conf'],
                        reverse=True
                    )

                    rotate_id = convertForStraight(
                        rotate_cls_output[0]["class_name"]
                    )

                    muti_layer.append({
                        "class_name": class_name,
                        "conf": conf,
                        "rotate_id": rotate_id,
                    })

                elif class_name_split[1] in ["corner1", "corner2"]:

                    class_name_rotate = find_rotate_match(
                        seg_image,
                        range_out=1
                    )

                    rotate_id = convertForCorner(
                        class_name_rotate
                    )

                    muti_layer.append({
                        "class_name": class_name,
                        "conf": conf,
                        "rotate_id": rotate_id,
                    })

                elif class_name_split[1] in [
                    "connector",
                    "converger",
                    "splitter"
                ]:

                    rotate_cls_output = valPipeBeltRotateCls([seg_image])

                    rotate_id = convertForModel(
                        rotate_cls_output[0]["class_name"]
                    )

                    muti_layer.append({
                        "class_name": class_name,
                        "conf": conf,
                        "rotate_id": rotate_id,
                    })

            data_belts.append({
                "x": xindex,
                "y": yindex,
                "muti_layer": muti_layer,
            })

    # -----------------------------
    # 输出蓝图
    # -----------------------------
    blueprint = convert_blueprint(data, data_belts, save = args.save)
    return blueprint

def run():
    try:
        blueprint = main()
        print(json.dumps({
            "status": "success",
            "blueprint": blueprint,
            "error": ""
        }, indent=2), flush=True)
        exit(0)
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "blueprint": "",
            "error": str(e)
        }, indent=2), flush=True)
        exit(1)

if __name__ == "__main__":
    #最后一次更新时间：2026-3-15
    #这个cli工具是喂给gpt之后的重构版本
    #没有debug功能，若要使用debug功能可以使用blueprint_debug.py
    run()