import cv2
import numpy as np
import win32gui
import win32ui
import win32con
import win32api


class GameOverlay:
    def __init__(self, window_name="8BP Overlay"):
        self.window_name = window_name
        self.hwnd = self.create_window()

    def create_window(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(
            self.window_name,
            cv2.WND_PROP_TOPMOST,
            1
        )
        return None

    def show(self, frame):
        cv2.imshow(self.window_name, frame)
        cv2.waitKey(1)
