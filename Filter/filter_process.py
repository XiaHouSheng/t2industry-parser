import json
import time
import random

machine_class_config = {
  # 这部分是改了ID的
  "res_out_port": "warehouseWithdrawalPort",
  "res_in_port": "warehouseDepositPort",
  "power_pole": "powerSupplier",
  "power_station": "powerStation",
  "storage_box": "protocolStorageBox",
  # 基本机器
  "furnance_1": "refineryFurnace",
  "grinder_1": "crusher",
  "cmpt_mc_1": "accessoryMachine",
  "shaper_1": "shapingMachine",
  "seedcol_1": "seedHarvester",
  "planter_1": "planter",
  "winder_1": "equipmentComponentMachine",
  "filling_pd_mc_1": "fillingMachine",
  "tools_asm_mc_1": "packagingMachine",
  "thickener_1": "grinder",
  #"power_sta_1": "powerStation",
  # —— Wuling 专属 —— | 这里还没有做组件，后续直接生成
  "dismantler_1": "dismantlerMachine",
  "mix_pool_1": "reactionPool",
  "xiranite_oven_1": "xiraniteFurnace",
  "pump_1": "waterPump" #水泵需要从蓝图区域外拉，暂不添加
}

layer_type_map = {
    "belt": "belt-img",
    "belt_connector": "cross-img",
    "belt_converger": "conveyer-img",
    "belt_corner1": "turn-img",
    "belt_corner2": "turn-img",
    "belt_splitter": "splitter-img",

    "pipe": "belt-img-pipe",
    "pipe_connector": "cross-img-pipe",
    "pipe_converger": "conveyer-img-pipe",
    "pipe_corner1": "turn-img-pipe",
    "pipe_corner2": "turn-img-pipe",
    "pipe_splitter": "splitter-img-pipe",
}

def generate_unique_id(root_id: str) -> str:
    timestamp = int(time.time() * 1000)
    random_num = random.randint(0, 999)
    return f"{root_id}_{timestamp}_{random_num}"

def convert_machines(data, machine_class_config):

    machines = []
    widget_ids = []

    for obj in data:

        # ---------- machine key ----------
        if obj["machine_detect_type"] == "machine":
            machine_key = obj["producer"]
        else:
            machine_key = obj["machine_detect_type"]

        if machine_key not in machine_class_config:
            continue

        machine_id = machine_class_config[machine_key]

        # ---------- recipe ----------
        recipe = obj["class_name"] if obj["class_name"] else ""

        # ---------- id ----------
        mid = generate_unique_id(machine_id)

        machine = {
            "id": mid,
            "machine_id": machine_id,
            "recipe": recipe,
            "rotate": obj["rotate"],
            "x": obj["x"],
            "y": obj["y"],
            "w": obj["w"],
            "h": obj["h"],
            "part": "part0"
        }

        machines.append(machine)
        widget_ids.append(mid)

    return machines, widget_ids

def convert_transport(data_belt):

    belts = []
    pipes = []

    belt_keys = []
    pipe_keys = []

    for obj in data_belt:

        x = obj["x"]
        y = obj["y"]

        for layer in obj["muti_layer"]:

            cname = layer["class_name"]
            rotate = layer["rotate_id"]

            if cname not in layer_type_map:
                continue

            type_name = layer_type_map[cname]

            entry = {
                "id": cname,
                "type": type_name,
                "rotate": rotate,
                "position": {
                    "x": x,
                    "y": y
                }
            }

            if cname.startswith("pipe"):
                pipes.append(entry)
                pipe_keys.append(f"{x}-{y}")
            else:
                belts.append(entry)
                belt_keys.append(f"{x}-{y}")

    return belts, pipes, belt_keys, pipe_keys

def convert_blueprint(data, data_belt):

    machines, widget_ids = convert_machines(data, machine_class_config)

    belts, pipes, belt_keys, pipe_keys = convert_transport(data_belt)

    blueprint = {
        "machine": machines,
        "belt": belts,
        "pipe": pipes,
        "part": {
            "parts":[{"name":"part0","code":"","show":True}],
            "partsWidgetId":{"part0": widget_ids},
            "partsBelts":{"part0": belt_keys},
            "partsPipes":{"part0": pipe_keys},
            "editPartChoose":"part0"
        }
    }

    with open("./output/blueprint.json", "w") as f:
        json.dump(blueprint, f, indent=4)


    
