import win32gui
import win32con
import win32api
import numpy as np
import cv2


class TransparentOverlay:
    def __init__(self, window_name="AI_OVERLAY"):

        self.name = window_name
        cv2.namedWindow(self.name, cv2.WINDOW_NORMAL)

        hwnd = win32gui.FindWindow(None, self.name)

        # make window layered + topmost
        win32gui.SetWindowLong(
            hwnd,
            win32con.GWL_EXSTYLE,
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            | win32con.WS_EX_LAYERED
            | win32con.WS_EX_TRANSPARENT
            | win32con.WS_EX_TOPMOST
        )

        win32gui.SetLayeredWindowAttributes(
            hwnd,
            0x000000,
            0,
            win32con.LWA_COLORKEY
        )

    def show(self, frame):
        cv2.imshow(self.name, frame)
        cv2.waitKey(1)
