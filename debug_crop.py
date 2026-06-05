# debug_crop.py
import cv2
import os
from config.settings import TABLE_ROI

def check_my_crop():
    image_path = "test_screen.png"
    if not os.path.exists(image_path):
        print("Error: test_screen.png is missing in Root!")
        return
        
    # قراءة الصورة الكبيرة
    frame = cv2.imread(image_path)
    
    # جلب أبعاد الـ ROI من الـ Config
    top, left = TABLE_ROI["top"], TABLE_ROI["left"]
    width, height = TABLE_ROI["width"], TABLE_ROI["height"]
    
    # قص منطقة اللعب
    cropped = frame[top:top+height, left:left+width]
    
    # حفظ الصورة المقصوصة للتأكد منها
    cv2.imwrite("crop_test.png", cropped)
    print("=== Done! 'crop_test.png' has been saved. ===")
    print(f"Please check if it shows ONLY the blue pool table area. Current ROI: {TABLE_ROI}")

if __name__ == "__main__":
    check_my_crop()
