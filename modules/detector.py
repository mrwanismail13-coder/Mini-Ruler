# modules/detector.py
import cv2
import numpy as np
from ultralytics import YOLO
from typing import Dict, List, Tuple

class TableDetector:
    def __init__(self, model_path: str = "models/best.pt"):
        """
        بنعرف موديل YOLO11 المخصص بتاعنا
        """
        self.model = YOLO(model_path)
        # تعريف الـ Classes بناءً على الـ data.yaml بتاعة الـ Dataset
        self.class_names = {
            0: "cue_ball",
            1: "object_ball",
            2: "pocket",
            3: "cushion_top_left",
            4: "cushion_top_right",
            5: "cushion_bottom_left",
            6: "cushion_bottom_right",
            7: "cushion_left",
            8: "cushion_right"
        }

    def crop_to_roi(self, frame: np.ndarray, roi: Dict[str, int]) -> np.ndarray:
        """
        ROI Cropping: بنقطع منطقة اللعب بس (الأخضر/الأزرق) عشان نزود الـ FPS
        ونمنع الـ Model إنه يتشتت في إعلانات اللعبة أو أسامي اللاعبين.
        """
        top, left = roi["top"], roi["left"]
        width, height = roi["width"], roi["height"]
        return frame[top:top+height, left:left+width]

    def detect_elements(self, frame: np.ndarray, roi: Dict[str, int]) -> Dict[str, List[Tuple[float, float, float, float, float]]]:
        """
        بندخل كادر الشاشة، نعمله Crop، ونشغل الـ Inference
        النتيجة بترجع متقسمة لـ كرات، جيوب، وحواف (6-Cushion Rule)
        كل عنصر عبارة عن: (x_center, y_center, width, height, confidence)
        """
        cropped_frame = self.crop_to_roi(frame, roi)
        results = self.model(cropped_frame, verbose=False)[0]
        
        detections = {
            "cue_ball": [],
            "object_balls": [],
            "pockets": [],
            "cushions": []
        }
        
        for box in results.boxes:
            cls_id = int(box.cls[0].item())
            label = self.class_names.get(cls_id, "unknown")
            conf = float(box.conf[0].item())
            
            # نجيب الإحداثيات الـ Bounding Box (xywh)
            xywh = box.xywh[0].cpu().numpy()
            x_c, y_c, w, h = xywh[0], xywh[1], xywh[2], xywh[3]
            
            # تحويل الإحداثيات عشان ترجع لمقاس الشاشة الأصلي (Global Coordinates)
            global_x_c = x_c + roi["left"]
            global_y_c = y_c + roi["top"]
            
            data_tuple = (global_x_c, global_y_c, w, h, conf)
            
            if label == "cue_ball":
                detections["cue_ball"].append(data_tuple)
            elif label == "object_ball":
                detections["object_balls"].append(data_tuple)
            elif label == "pocket":
                detections["pockets"].append(data_tuple)
            elif "cushion" in label:
                # الـ 6 حواف الرفيعة جداً اللي الكورة بتخبط فيها
                detections["cushions"].append((global_x_c, global_y_c, w, h, conf, label))
                
        return detections
