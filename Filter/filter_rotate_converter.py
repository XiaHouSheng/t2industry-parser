
config_straight = {
    "right": 0,
    "bottom": 1,
    "left": 2,
    "up": 3,
}

config_corner = {
    "left_top": 0,
    "right_top": 1,
    "right_bottom": 2,
    "left_bottom": 3,
}

def convertForStraight(class_name):
    return config_straight[class_name]

def convertForCorner(class_name):
    return config_corner[class_name]

def convertForModel(class_name):
    return class_name.split("_")[-1]