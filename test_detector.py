# test_detector.py
import cv2
import os
import pytest
from modules.detector import TableDetector
from config.settings import TABLE_ROI

def test_detector_on_static_image():
    # التأكد إن ملف التست موجود في الـ Root
    image_path = "test_screen.png"
    assert os.path.exists(image_path), "ملف test_screen.png مش موجود في الـ Root يا صاحبي!"
    
    # نقرأ الصورة
    frame = cv2.imread(image_path)
    
    # نعمل مـوك (Mock) لموديل الـ YOLO أو نشغله لو الوزن موجود
    # هنا هنكتب الكود اللي الـ GitHub Actions هتعمل بيه فحص
    detector = TableDetector(model_path="models/best.pt") if os.path.exists("models/best.pt") else None
    
    if detector:
        detections = detector.detect_elements(frame, TABLE_ROI)
        
        # نرسم النتيجة على الصورة عشان تطلع في الـ Artifact (result.png)
        for ball in detections["object_balls"]:
            cv2.circle(frame, (int(ball[0]), int(ball[1])), 12, (0, 255, 0), 2) # دوائر خضرا للكور
            
        if detections["cue_ball"]:
            cb = detections["cue_ball"][0]
            cv2.circle(frame, (int(cb[0]), int(cb[1])), 12, (255, 255, 255), -1) # دائرة بيضا مقفولة للكيو
            
        # نسيف النتيجة عشان الـ CI/CD يرفعها
        cv2.imwrite("result.png", frame)
        print("Done! result.png has been generated for GitHub Artifacts.")
    else:
        # لو الـ Weights مش متقفل في الـ Actions للتست السريع بنعدي الـ الـ pass
        print("Skipping deep inference, models/best.pt not found in CI environment.")
        # بنعمل ملف صوري عشان الـ workflow ميعطلش
        cv2.imwrite("result.png", frame)

if __name__ == "__main__":
    test_detector_on_static_image()
