import platform

IS_WINDOWS = platform.system().lower() == "windows"


class TransparentOverlay:
    def __init__(self, window_name="AI_OVERLAY"):

        self.window_name = window_name

        if not IS_WINDOWS:
            print("[INFO] Overlay disabled (not Windows environment)")
            self.enabled = False
            return

        self.enabled = True

        import cv2
        import win32gui
        import win32con

        self.cv2 = cv2
        self.win32gui = win32gui
        self.win32con = win32con

        self.cv2.namedWindow(self.window_name, self.cv2.WINDOW_NORMAL)

        hwnd = self.win32gui.FindWindow(None, self.window_name)

        self.win32gui.SetWindowLong(
            hwnd,
            self.win32con.GWL_EXSTYLE,
            self.win32gui.GetWindowLong(hwnd, self.win32con.GWL_EXSTYLE)
            | self.win32con.WS_EX_LAYERED
            | self.win32con.WS_EX_TOPMOST
        )

    def show(self, frame):

        if not self.enabled:
            return

        self.cv2.imshow(self.window_name, frame)
        self.cv2.waitKey(1)
