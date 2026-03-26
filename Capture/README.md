# Capture 模块说明

## 功能描述
Capture 模块是专为 Windows 用户设计的自动截图工具，主要用于捕获游戏窗口（如 Endfield）的蓝图界面，并支持滚动截图和图像拼接功能。

## 核心功能
- 自动定位游戏窗口
- 垂直和水平方向的滚动截图
- 图像拼接和处理
- 鼠标自动控制（模拟用户操作）

## 依赖包
运行环境要求：**Python 3.9+**

该模块依赖以下 Python 包：
- numpy
- pygetwindow
- pyautogui
- mss
- PIL (Pillow)
- cv2 (OpenCV)
- ctypes (Windows 系统内置)

### 安装命令
推荐先创建并使用虚拟环境（venv）：

```bash
# 进入 Capture 目录
cd Capture

# 创建虚拟环境（Python 3.9+）
python -m venv .venv

# 激活虚拟环境（Windows PowerShell）
.\.venv\Scripts\Activate.ps1

# 激活虚拟环境（Windows CMD）
.\.venv\Scripts\activate.bat
```

激活后安装依赖：

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

或手动安装：

```bash
python -m pip install numpy pygetwindow pyautogui mss Pillow opencv-python
```

安装完成后，如需退出虚拟环境：

```bash
deactivate
```

## 部署说明
**重要：** 由于该模块主要用于 Windows 环境下的自动截图操作，包含依赖于 Windows 系统的功能（如 `ctypes.windll` 调用），因此在部署到其他环境或作为服务运行时，**不需要安装该模块的依赖包**。

如果您的部署环境不需要截图功能，可以完全忽略该模块，不会影响其他功能的正常运行。

## 使用方法
1. 确保游戏窗口（如 Endfield）处于打开状态(全屏)
2. 运行 `capture.py` 文件 - `python capture.py` 需要以管理员权限运行 - 先开一个管理员权限的命令行窗口（可以问AI如何开启）
4. 打开蓝图窗口，选择蓝图并查看
5. 按照提示按 Enter 键开始捕获
6. 捕获的图像会保存在 `./screen_shots/blueprints/` 目录中

## 注意事项
- 仅支持 Windows 操作系统
- 运行时需要游戏窗口处于可见状态
- 可能需要管理员权限才能正常控制鼠标