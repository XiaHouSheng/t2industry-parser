# t2industry-parser
终末地 蓝图解析工具 | 用于实现 游戏内蓝图 -> 蓝图站蓝图 的自动转换 | 基于 YOLO 目标检测与 OpenCV 图像处理

## 项目简介

`t2industry-parser` 是一个专为终末地游戏设计的蓝图解析工具，能够自动识别游戏内蓝图中的各种元素（如机器、传送带、管道等），并将其转换为蓝图站格式的蓝图数据。

**主站链接**：[t2industry](https://github.com/XiaHouSheng/t2industry) - 终末地产线模拟工具平台，提供蓝图分享、蓝图编辑等功能

后续会进行服务端部署，为主站提供解析服务

## 功能特点

- **自动蓝图解析**：使用 YOLO 模型自动检测和识别蓝图中的各种元素
- **智能分类**：准确识别机器类型、传送带、管道等游戏元素
- **方向识别**：自动检测元素的旋转方向
- **批量处理**：支持批量处理多个蓝图图像
- **配置灵活**：可通过配置文件自定义解析参数
- **跨平台**：核心功能支持跨平台运行（Capture 模块仅支持 Windows）

## 项目结构

```
t2industry-parser/
├── Capture/           # Windows 自动截图模块（仅 Windows 平台使用）
│   ├── README.md      # Capture 模块说明
│   ├── capture.py     # 截图核心功能
│   └── utils.py       # 截图工具函数
├── Filter/            # 蓝图解析核心模块
│   ├── blueprint_cli.py          # 命令行接口
│   ├── blueprint_debug.py        # 调试接口
│   ├── filter.py                 # 核心过滤功能
│   ├── filter_process.py         # 处理流程
│   ├── filter_rotate_converter.py # 旋转转换
│   └── filter_sub.py             # 辅助函数
├── config/            # 配置文件目录
│   ├── machine_config/           # 机器配置
│   └── standard_images/          # 标准图像
├── model/             # YOLO 模型文件
├── output/            # 输出目录
├── test/              # 测试文件
├── yaml/              # 模型配置文件
├── .gitignore         # Git 忽略文件
├── LICENSE            # 许可证
└── README.md          # 项目说明
```

## 安装说明

### 核心依赖

- Python 3.8+
- NumPy
- OpenCV
- PyTorch
- YOLOv8 (ultralytics)
- Pillow

### 安装步骤

1. 克隆项目到本地
   ```bash
   git clone <repository-url>
   cd t2industry-parser
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

### 注意事项

- **Capture 模块**：该模块仅用于 Windows 平台的自动截图功能，部署时不需要安装其依赖（如 pygetwindow、pyautogui 等）
- **模型文件**：确保 `model/` 目录中包含所有必要的 YOLO 模型文件

## 使用方法

### 命令行接口

```bash
python Filter/blueprint_cli.py -i <blueprint-image-path> [options]
```

### 参数说明

- `-i, --input`：蓝图图像路径（必填）
- `-c, --config`：产品到工厂的配置文件路径（默认：`./config/machine_config/product_to_factory.json`）
- `--grid-x`：网格 X 方向数量（默认：16）
- `--grid-y`：网格 Y 方向数量（默认：17）

### 示例

```bash
# 解析蓝图图像
python Filter/blueprint_cli.py -i test/blueprint.png

# 自定义网格大小
python Filter/blueprint_cli.py -i test/blueprint.png --grid-x 20 --grid-y 20
```

### 输出

解析完成后，结果将保存到 `output/blueprint.json` 文件中，可直接导入到蓝图站使用。

## 技术栈

- **目标检测**：YOLOv8
- **图像处理**：OpenCV
- **数值计算**：NumPy
- **图像操作**：Pillow
- **命令行工具**：argparse
- **配置管理**：JSON

## 注意事项

1. **蓝图图像要求**：建议使用清晰、无遮挡的蓝图图像，确保元素能被正确识别
2. **性能要求**：解析大型蓝图可能需要较高的计算资源
3. **模型精度**：识别精度取决于训练模型的质量，可能存在一定的误识别情况
4. **Capture 模块**：仅支持 Windows 操作系统，部署时可忽略

## 部署说明

- **生产环境**：部署时不需要安装 Capture 模块的依赖，核心解析功能可在任何支持 Python 的环境中运行
- **Docker 部署**：可通过 Docker 容器化部署，仅包含核心依赖
- **服务化**：可将解析功能封装为 API 服务，供其他系统调用

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 更新日志

- **2026-03-15**：重构命令行工具，优化解析流程
- **2026-03-10**：添加传送带和管道的方向识别功能
- **2026-03-05**：集成 YOLOv8 模型，提高识别精度

## 贡献

欢迎提交 Issue 和 Pull Request 来改进本项目！