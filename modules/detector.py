import cv2
import numpy as np
import os
import sys
from ultralytics import YOLO
from typing import Dict, List


def get_base_path():
    """
    بيحدد مكان تشغيل البرنامج سواء:
    - تشغيل عادي (python)
    - أو exe (PyInstaller)
    """
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TableDetector:
    def __init__(self, model_path: str = "models/best.pt"):

        base_path = get_base_path()

        # المسار الحقيقي للموديل بعد build
        self.model_path = os.path.join(base_path, "models", "best.pt")

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"YOLO model not found: {self.model_path}")

        self.model = YOLO(self.model_path)

        # mapping الكلاسات حسب تدريبك
        self.class_names = {
            0: "white_cue_ball",
            1: "object_ball",
            2: "pocket",
            3: "cushion"
        }

    def detect_elements(self, frame: np.ndarray, roi: Dict[str, int]) -> Dict[str, List]:

        results_dict = {
            "cue_ball": [],
            "object_balls": [],
            "pockets": [],
            "cushions": []
        }

        if frame is None:
            return results_dict

        h, w, _ = frame.shape

        top = roi["top"]
        left = roi["left"]
        width = roi["width"]
        height = roi["height"]

        cropped = frame[top:top + height, left:left + width]

        results = self.model.predict(cropped, conf=0.25, verbose=False)

        if not results:
            return results_dict

        boxes = results[0].boxes

        for box in boxes:

            xyxy = box.xyxy[0].cpu().numpy()
            cls_id = int(box.cls[0].cpu().numpy())
            conf = float(box.conf[0].cpu().numpy())

            x_center = (xyxy[0] + xyxy[2]) / 2
            y_center = (xyxy[1] + xyxy[3]) / 2

            global_x = int(x_center + left)
            global_y = int(y_center + top)

            if cls_id == 0:
                results_dict["cue_ball"].append((global_x, global_y, conf))

            elif cls_id == 1:
                results_dict["object_balls"].append((global_x, global_y, conf))

            elif cls_id == 2:
                results_dict["pockets"].append((global_x, global_y, conf))

            elif cls_id == 3:
                results_dict["cushions"].append((global_x, global_y, conf))

        return results_dict
