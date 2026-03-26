from numpy import floor
import pygetwindow
import pyautogui
import time
import ctypes
import numpy as np
import os
from mss import mss
from PIL import Image
from pathlib import Path
from Capture.utils import *
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent

class Capture:
    def __init__(self, title="Endfield", step=100):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            ctypes.windll.user32.SetProcessDPIAware()
        self.title = title
        self.window = pygetwindow.getWindowsWithTitle(self.title)[0]
        self.mss = mss()
        self.step = step
        if self.window:
            self.window.activate()
            self.windowX, self.windowY, self.windowWidth, self.windowHeight = self.window.left, self.window.top, self.window.width, self.window.height
            self.verticalBarX, self.verticalBarY = 1888, 160
            self.horizontalBarX, self.horizontalBarY = 95, 1520
            self.blueprintX, self.blueprintY, self.blueprintWidth, self.blueprintHeight = 0, 122, 1880, 1390
    
    def verticalScanATogether(self) -> tuple:
        index = 1
        bias = []
        root_array = None
        root_before = None
        custom_monitor = {
            "left": self.windowX + self.blueprintX,
            "top": self.windowY + self.blueprintY,
            "width": self.blueprintWidth,
            "height": self.blueprintHeight,
        }
        pyautogui.moveTo(self.windowX + self.verticalBarX, self.windowY + self.verticalBarY)
        pyautogui.mouseDown(button="left")
        time.sleep(0.5)
        sct_img = self.mss.grab(custom_monitor)
        img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
        root_array = root_before = np.array(img)

        while True:
            pyautogui.mouseDown(button="left")
            time.sleep(0.5)
            pyautogui.moveTo(self.windowX + self.verticalBarX, self.windowY + self.verticalBarY + (index * self.step))
            time.sleep(0.5)
            pyautogui.mouseUp(button="left")

            sct_img = self.mss.grab(custom_monitor)
            img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
            imgarray = np.array(img)

            shift, response = isMove(root_before, imgarray)

            if floor(shift[1]) == 0:
                break
            
            root_array = pieceTogetherVertical(root_array, imgarray, shift[1])
            root_before = imgarray
            bias.append(shift[1])    
            index += 1
        return bias, root_array

    def horizontalScan(self) -> list:
        index = 1
        bias = []
        root_before = None
        custom_monitor = {
            "left": self.windowX + self.blueprintX,
            "top": self.windowY + self.blueprintY,
            "width": self.blueprintWidth,
            "height": self.blueprintHeight,
        }
        pyautogui.moveTo(self.windowX + self.horizontalBarX, self.windowY + self.horizontalBarY)
        pyautogui.mouseDown(button="left")
        time.sleep(1)
        sct_img = self.mss.grab(custom_monitor)
        img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
        root_before = np.array(img)
        while True:
            pyautogui.mouseDown(button="left")
            time.sleep(0.5)
            pyautogui.moveTo(self.windowX + self.horizontalBarX + (index * self.step), self.windowY + self.horizontalBarY)
            time.sleep(0.5)
            pyautogui.mouseUp(button="left")

            sct_img = self.mss.grab(custom_monitor)
            img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
            imgarray = np.array(img)

            shift, response = isMove(root_before, imgarray)
            print(shift, response)

            if floor(shift[0]) == 0:
                break

            root_before = imgarray
            bias.append(shift[0])    
            index += 1
        return bias

    def resetPosition(self) -> None:
        pyautogui.moveTo(self.windowX + self.verticalBarX, self.windowY + self.verticalBarY)
        pyautogui.mouseDown(button="left")
        time.sleep(0.2)
        pyautogui.mouseUp(button="left")
        time.sleep(0.2)
        pyautogui.moveTo(self.windowX + self.horizontalBarX, self.windowY + self.horizontalBarY)
        pyautogui.mouseDown(button="left")
        time.sleep(0.2)
        pyautogui.mouseUp(button="left")
        time.sleep(0.2)

    def captureImageScroll2Dimens(self, show = False) -> np.ndarray:
        self.resetPosition()
        #[-122.91144910302171, -122.92015612422131, -36.53526832314037]
        biasHorizontal = self.horizontalScan()
        self.resetPosition()
        bias, root_array = self.verticalScanATogether()
        self.resetPosition()
        index = 1
        for biasX in biasHorizontal:
            self.resetPosition()
            pyautogui.mouseDown(button="left")
            time.sleep(0.2)
            pyautogui.moveTo(self.windowX + self.horizontalBarX + (index * self.step), self.windowY + self.horizontalBarY)
            time.sleep(0.2)
            pyautogui.mouseUp(button="left")
            time.sleep(0.2)
            _, mid_array = self.verticalScanATogether()
            root_array = pieceTogetherHorizontal(root_array, mid_array, biasX)
            index += 1
        root_array_crop = root_array # cropImageScroll2(root_array)
        if show:
            img = Image.fromarray(root_array_crop)
            img.show()
        return root_array_crop

    def testMoveMouse(self) -> None:
        pyautogui.moveTo(self.windowX + self.verticalBarX, self.windowY + self.verticalBarY)

if __name__ == "__main__":
    capture = Capture()
    output_dir = BASE_DIR / "screen_shots" / "blueprints"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    existing_files = list(output_dir.glob("blueprint_*.png"))
    start_num = len(existing_files) + 1
    
    while True:
        input("按 Enter 开始捕获...")
        output_ndarray = capture.captureImageScroll2Dimens(show=True)
        img = Image.fromarray(output_ndarray)
        save_path = output_dir / f"blueprint_{start_num}.png"
        file = open(save_path, "wb")
        img.save(file)
        file.close()
        print(f"已保存: {save_path}")
        start_num += 1
        

    


