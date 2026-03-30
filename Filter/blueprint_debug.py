import json
import os
from filter import *
from filter_sub import *
from filter_rotate_converter import *
from filter_process import convert_blueprint
from PIL import ImageDraw
import matplotlib.pyplot as plt

#蓝图文件
#target_path = "./ScreenShots/target_test_bp.png"
target_path = "./test/blueprint_test.png"
target_img = Image.open(target_path).convert("RGB")

#配置文件
recipe_path = "./config/machine_config/product_to_factory.json"
recipe_config = json.load(open(recipe_path, "r"))
machine_detect_classes = ["machine", "power_pole", "power_station", "res_in_port", "res_out_port", "storage_box"]

#数据
#w_index, h_index = 9, 11
w_index, h_index = 12, 5
width, height = target_img.size

grid_width = width // w_index
grid_height = height // h_index
final_cell_size = (grid_height + grid_width) // 2

target_ndarray = np.array(target_img)
target_batch = [target_ndarray]

#检测机器
result_machine_detect = valMachineDetect(target_batch)
machine_detect_boxes = result_machine_detect[0]['boxes']
machine_detect_boxes = [box for box in machine_detect_boxes if box.conf[0] >= 0.6]

#可视化展示机器检测结果
if True:
    draw = ImageDraw.Draw(target_img)
    class_names = ["machine", "power_pole", "power_station", "res_in_port", "res_out_port", "storage_box"]
    for result in result_machine_detect:
        boxes = result['boxes']
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id = int(box.cls[0])
            class_name = class_names[class_id]
            conf = float(box.conf[0])
            if conf >= 0.5:
                draw.rectangle([x1, y1, x2, y2], outline='red', width=2)
                draw.text((x1, y1 + 10), f"{class_name} {conf:.2f}", fill='red')
    target_img.show()

#特殊数据结构-遍历cell自动跳过该范围
skip_range = []
#debug记录一些cell片段
rotate_cls_not_found_error = []
#test_image = target_img.copy()
#draw = ImageDraw.Draw(test_image)

for box in machine_detect_boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0])

    class_name = machine_detect_classes[int(box.cls[0])]

    box_width = x2 - x1
    box_height = y2 - y1
    
    grid_w = int(np.around(box_width / final_cell_size))
    grid_h = int(np.around(box_height / final_cell_size))

    grid_w_not_floor = box_width / final_cell_size
    grid_h_not_floor = box_height / final_cell_size

    #print(f"grid_w: {grid_w}, grid_h: {grid_h}, grid_w_not_floor: {grid_w_not_floor}, grid_h_not_floor: {grid_h_not_floor}, class_name: {class_name}")
    
    start_x = round(x1 / final_cell_size)
    start_y = round(y1 / final_cell_size)

    if class_name == "power_pole":
        print("power_pole", start_x, start_y, grid_w, grid_h)

    for i in range(grid_w):
        for j in range(grid_h):
            skip_range.append((start_x + i, start_y + j))
            #draw.rectangle([(start_x + i) * final_cell_size, (start_y + j) * final_cell_size, (start_x + i + 1) * final_cell_size, (start_y + j + 1) * final_cell_size], outline='red', width=2)
            
#test_image.show()
#检测机器类别
data = []
for box in machine_detect_boxes:
    
    #框选裁剪数据预处理
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    box_width = x2 - x1
    box_height = y2 - y1

    grid_w = int(np.round(box_width / final_cell_size))
    grid_h = int(np.round(box_height / final_cell_size))

    start_x = round(x1 / final_cell_size)
    start_y = round(y1 / final_cell_size)

    #power_pole 供电桩 power_station 热能池 不进行后续处理
    if box.cls[0] == 1 or box.cls[0] == 2: 
        data.append({
            "class_name": None,
            "machine_detect_type": machine_detect_classes[int(box.cls[0])],
            "producer": None,
            "rotate": 0,
            "x": start_x,
            "y": start_y,
            "w": grid_w,
            "h": grid_h,
        })
        #print(f"box_width / final_cell_size: {box_width / final_cell_size}, box_height / final_cell_size: {box_height / final_cell_size}")
        #print(f"grid_w: {grid_w}, grid_h: {grid_h}")
        continue


    #裁剪目标中心ICON
    ndarray_product_icon = None
    result_product_cls = None

    average_x = (x1 + x2) / 2
    average_y = (y1 + y2) / 2
    start_crop_x = int(average_x - (final_cell_size / 2))
    start_crop_y = int(average_y - (final_cell_size / 2))
    end_crop_x = start_crop_x + final_cell_size
    end_crop_y = start_crop_y + final_cell_size
    
    #识别目标中心ICON类别
    ndarray_product_icon = target_ndarray[start_crop_y:end_crop_y, start_crop_x:end_crop_x]
    result_product_cls = valProductCls([ndarray_product_icon])[0]
    pre_class_name = result_product_cls['class_name']
    pre_conf = result_product_cls['conf']

    #裁剪边缘ICON并识别 用于判断rotate类型
    rotate_id = 0
    #machine 机器 / storage_box 存储箱
    if box.cls[0] == 0 or box.cls[0] == 5: 
        start_crop_x_top = int(x1 + final_cell_size)
        start_crop_y_top = int(y1)

        end_crop_x_top = start_crop_x_top + final_cell_size
        end_crop_y_top = start_crop_y_top + final_cell_size
        
        start_crop_x_side = int(x1)
        start_crop_y_side = int(y1 + final_cell_size)

        end_crop_x_side = start_crop_x_side + final_cell_size
        end_crop_y_side = start_crop_y_side + final_cell_size

        ndarray_side_port = target_ndarray[start_crop_y_side:end_crop_y_side, start_crop_x_side:end_crop_x_side]
        ndarray_top_port = target_ndarray[start_crop_y_top:end_crop_y_top, start_crop_x_top:end_crop_x_top]
        
        # 测试记录数据
        if False:
            rotate_cls_not_found_error.append(ndarray_top_port)
            rotate_cls_not_found_error.append(ndarray_side_port)

        #识别边缘ICON类别
        machine_rotate_detect_batch = [ndarray_top_port, ndarray_side_port]
        result_machine_rotate = valMachineRotateCls(machine_rotate_detect_batch)
        top_id , top_class_name, top_conf = result_machine_rotate[0].values()
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
        
        #测试可视化
        if False:
            Image.fromarray(ndarray_side_port).show()
            Image.fromarray(ndarray_top_port).show()
            break
    #res_in_port / res_out_port 进出口
    if box.cls[0] == 3 or box.cls[0] == 4:
        if grid_w > grid_h:
            rotate_id = 0
        else:
            rotate_id = 1


    if pre_class_name in getClasses():
        convert_bgr = cv2.cvtColor(ndarray_product_icon, cv2.COLOR_RGB2BGR)
        best_match, best_score = find_best_match(convert_bgr, pre_class_name)
        pre_class_name = best_match.split(".")[0]
        pre_conf = best_score
    
    #这里进行机器数据打包
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

#测试可视化
if False:
    # 计算布局：比如按每行2张排列
    n_images = len(data)
    n_cols = 4
    n_rows = (n_images + n_cols - 1) // n_cols  # 向上取整计算行数

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(8, 4*n_rows))
    axes = axes.flatten()  # 将二维数组展平为一维，方便遍历

    len_file = len(os.listdir("./pieces_with_bg"))

    # 遍历数据，将图片绘制到子图中
    for i, item in enumerate(data):
        ax = axes[i]
        ax.imshow(item["image"])
        ax.set_title(f"{item['class_name']} ({item['conf']:.2f})")
        ax.axis('off')  # 关闭坐标轴
        #保存子图,根据文件数量
        if False:
            image = Image.fromarray(item["image"])
            file = f"./pieces_with_bg/output_{i + len_file}.png"
            image.save(file)
    
    # 如果子图数量大于数据数量，隐藏多余的子图
    for j in range(i+1, len(axes)):
        axes[j].axis('off')

    plt.tight_layout()
    plt.show()

#这里进行区域分割
SHOW_VISUALIZATION = True
visualization_data = []
data_belts = []
#遍历区域解析beltApipe
for xindex in range(w_index):
    for yindex in range(h_index):

        #跳过特殊范围
        if (xindex, yindex) in skip_range:
            continue
        
        start_crop_x = xindex * final_cell_size
        start_crop_y = yindex * final_cell_size
        end_crop_x = start_crop_x + final_cell_size
        end_crop_y = start_crop_y + final_cell_size
        grid_ndarray = target_ndarray[start_crop_y:end_crop_y, start_crop_x:end_crop_x]
        
        #判断是否为背景
        if np.std(grid_ndarray) < 15:
            continue

        seg_outputs = valSegModel([grid_ndarray])[0]
        confs = seg_outputs['confs']
        seg_images = seg_outputs['segmented_images']
        seg_images = [img for img, conf in zip(seg_images, confs) if conf >= 0.5]
        
        if len(seg_images) == 0:
            print(f"Error: 未检测到有效区域, xindex: {xindex}, yindex: {yindex}")
            continue

        #识别分类：belt / pipe / model
        grid_class_outputs = valClassModel(seg_images)
        #[{'class_id': 0, 'class_name': 'belt', 'conf': 0.5158471465110779}]

        muti_layer = []

        #遍历后进行rotate判断
        for i in range(len(grid_class_outputs)):
            class_id, class_name, conf = grid_class_outputs[i].values()
            class_name_split = class_name.split("_")
            seg_image = seg_images[i]
            seg_image = cv2.cvtColor(seg_image, cv2.COLOR_BGR2RGB)
            #pipe / belt
            if len(class_name_split) == 1:
                rotate_cls_output = valRotateCls([seg_image])
                rotate_cls_output.sort(key=lambda x: x['conf'], reverse=True)
                rotate_id = None
                if not rotate_cls_output:
                    print(f"Error: 未检测到有效旋转分类, xindex: {xindex}, yindex: {yindex}, class_name: {class_name}")
                    rotate_cls_not_found_error.append(seg_image)
                else: 
                    rotate_id = convertForStraight(rotate_cls_output[0]["class_name"])
                muti_layer.append({
                    "class_name": class_name,
                    "conf": conf,
                    "rotate_id": rotate_id,
                })
                continue
            #corner1 and corner2
            elif class_name_split[1] in ["corner1", "corner2"]:
                class_name_rotate = find_rotate_match(seg_image, range_out= 1)
                rotate_id = None
                try:
                    rotate_id = convertForCorner(class_name_rotate)
                except Exception as e:
                    print(f"Error: 无效的旋转分类, xindex: {xindex}, yindex: {yindex}, class_name: {class_name}, error: {e}")
                    rotate_cls_not_found_error.append(seg_image)
                muti_layer.append({
                    "class_name": class_name,
                    "conf": conf,
                    "rotate_id": rotate_id,
                })
                continue
            #model
            elif class_name_split[1] in ["connector", "converger", "splitter"]:
                rotate_cls_output = valPipeBeltRotateCls([seg_image])
                rotate_id = None
                if not rotate_cls_output:
                    print(f"Error: 未检测到有效旋转分类, xindex: {xindex}, yindex: {yindex}, class_name: {class_name}")
                    rotate_cls_not_found_error.append(seg_image)
                else:  
                    rotate_id = convertForModel(rotate_cls_output[0]["class_name"])
                muti_layer.append({
                    "class_name": class_name,
                    "conf": conf,
                    "rotate_id": rotate_id,
                })
                continue
        
        data_belts.append({
            "x": xindex,
            "y": yindex,
            "muti_layer": muti_layer,
        })

        #可视化展示
        if SHOW_VISUALIZATION:
            for img, output in zip(seg_images, grid_class_outputs):
                visualization_data.append({
                    "image": img,
                    "class_name": output['class_name'],
                    "conf": output['conf']
                })

print("机器识别结果\n")
print(data)
print("传送带/管道/物流模块 识别结果\n")
print(data_belts)

convert_blueprint(data, data_belts, save = True)

#遍历完毕后统一展示可视化
if SHOW_VISUALIZATION and len(visualization_data) > 0:
    num_images = len(visualization_data)
    cols = min(5, num_images)
    rows = (num_images + cols - 1) // cols
    
    plt.figure(figsize=(15, 3 * rows))
    for i, data in enumerate(visualization_data):
        plt.subplot(rows, cols, i + 1)
        plt.imshow(cv2.cvtColor(data["image"], cv2.COLOR_BGR2RGB))
        plt.title(f"{data['class_name']}\n{data['conf']:.2f}")
        plt.axis('off')
    
    plt.tight_layout()
    plt.show()
    print(f"可视化展示完成，共 {num_images} 个分割图像")

#可视化展示旋转异常的图片
if False and len(rotate_cls_not_found_error) > 0:
    num_images = len(rotate_cls_not_found_error)
    cols = min(5, num_images)
    rows = (num_images + cols - 1) // cols
    
    plt.figure(figsize=(15, 3 * rows))
    for i, img in enumerate(rotate_cls_not_found_error):
        plt.subplot(rows, cols, i + 1)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.title(f"rotate_cls_not_found_error")
        plt.axis('off')
    
    plt.tight_layout()
    plt.show()
    print(f"可视化展示完成，共 {num_images} 个未找到有效旋转分类的图像")
    print("是否保存这些图像到文件？(y/n)")
    save_choice = input().strip().lower()
    if save_choice == 'y':
        save_dir = Path("./pieces_with_bg")
        save_dir.mkdir(parents=True, exist_ok=True)
        for i, img in enumerate(rotate_cls_not_found_error):
            img_path = save_dir / f"error_{i}.png"
            cv2.imwrite(str(img_path), img)
        print(f"已保存 {num_images} 张图像到 {save_dir}")
    else:
        print("未保存任何图像")

