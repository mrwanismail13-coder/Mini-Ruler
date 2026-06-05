# modules/detector.py
import cv2
import numpy as np
from ultralytics import YOLO
from typing import Dict, List

class TableDetector:
    def __init__(self, model_path: str = "models/best.pt"):
        """
        تحميل موديل YOLO11 المستهدف بدعم الـ CPU/GPU أوتوماتيكياً
        """
        self.model = YOLO(model_path)
        # أسماء الكلاسات المتوقعة من التدريب في Roboflow
        # 0: cue_ball, 1: object_ball, 2: pocket
        self.class_names = {0: "cue_ball", 1: "object_ball", 2: "pockets"}

    def detect_elements(self, frame: np.ndarray, roi: Dict[str, int]) -> Dict[str, List]:
        """
        قص منطقة اللعب وتشغيل الـ Inference بعناية شديدة لتوفير الـ FPS
        """
        results_dict = {"cue_ball": [], "object_balls": [], "pockets": []}
        
        if frame is None:
            return results_dict

        h, w, _ = frame.shape
        
        # أخذ الأبعاد من الـ Config
        top = max(0, roi["top"])
        left = max(0, roi["left"])
        width = min(w - left, roi["width"])
        height = min(h - top, roi["height"])
        
        # قص منطقة الطاولة (ROI)
        cropped_frame = frame[top:top+height, left:left+width]
        
        # تشغيل الموديل على المنطقة المقصوصة مع تفعيل الـ Conf الطفيف لضمان لقط الكور في الإضاءة الضعيفة
        # verbose=False عشان نمنع زحمة اللوجات ونحافظ على سرعة المعالجة
        results = self.model.predict(cropped_frame, conf=0.25, verbose=False)
        
        if not results:
            return results_dict
            
        boxes = results[0].boxes
        
        for box in boxes:
            # جلب الإحداثيات بالنسبة للمستطيل المقصوص (Bounding Box)
            xyxy = box.xyxy[0].cpu().numpy()
            cls_id = int(box.cls[0].cpu().numpy())
            conf = float(box.conf[0].cpu().numpy())
            
            # حساب مركز الكورة أو الجيب بالظبط (X_center, Y_center)
            x_center = (xyxy[0] + xyxy[2]) / 2.0
            y_center = (xyxy[1] + xyxy[3]) / 2.0
            
            # تحويل الإحداثيات من المستطيل المقصوص إلى إحداثيات الشاشة الكاملة الحقيقية (Global Coordinates)
            global_x = int(x_center + left)
            global_y = int(y_center + top)
            
            # تصنيف العناصر بناءً على الـ Class ID المستخرج من الـ Weights
            if cls_id == 0 or cls_id == 3: # الكورة البيضا (بعض الموديلات بتعتبرها كلاس منفصل)
                results_dict["cue_ball"].append((global_x, global_y, conf))
            elif cls_id == 1: # الكور الملونة المستهدفة
                results_dict["object_balls"].append((global_x, global_y, conf))
            elif cls_id == 2: # الجيوب الستة
                results_dict["pockets"].append((global_x, global_y, conf))

        # --- الـ Fallback الذكي ---
        # لو الموديل ملقاش الكورة البيضا الحقيقية بسبب ترحيل الـ ROI، هنجبره يبص على الشاشة كاملة فوراً
        if not results_dict["cue_ball"] and (roi["top"] != 0 or roi["left"] != 0):
            full_results = self.model.predict(frame, conf=0.30, verbose=False)
            if full_results:
                for box in full_results[0].boxes:
                    cls_id = int(box.cls[0].cpu().numpy())
                    if cls_id == 0: # لقط الكورة البيضا على الشاشة الكبيرة
                        xyxy = box.xyxy[0].cpu().numpy()
                        gx = int((xyxy[0] + xyxy[2]) / 2.0)
                        gy = int((xyxy[1] + xyxy[3]) / 2.0)
                        conf = float(box.conf[0].cpu().numpy())
                        results_dict["cue_ball"].append((gx, gy, conf))
                        break # لقيناها خلاص قفل الحسبة
                        
        return results_dict
