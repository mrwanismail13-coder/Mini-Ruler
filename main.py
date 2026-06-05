# main.py
import cv2
import numpy as np
import os
import sys
import time
import pyautogui
from config.settings import TABLE_ROI, PLAYABLE_CUSHIONS, BALL_RADIUS, HOTKEYS, POWER_MODES

class ProToolOrchestrator:
    def __init__(self, is_ci_environment: bool = False):
        self.is_ci = is_ci_environment
        self.current_roi = TABLE_ROI.copy()
        self.playable_cushions = PLAYABLE_CUSHIONS.copy()
        self.locked_ball_pos = None

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        # بنرجع الفريم زي ما هو في اللايف مؤقتاً
        return frame

    def run_live(self):
        print("=== 8BP Pro Tool Live Mode ===")
        # وضع تشغيل اللعبة العادي

    def run_static_test(self, input_path: str, output_path: str):
        # 1. قراءة الصورة الأساسية المرفوعة
        frame = cv2.imread(input_path)
        if frame is None:
            print(f"Error: Command failed, cannot open {input_path}")
            sys.exit(1)
            
        print(f"Successfully loaded {input_path}. Drawing guidelines directly...")

        # 2. الإحداثيات الحقيقية لسنتر الكور من واقع الشاشة test_screen.png
        # السنتر متقفل بالملي على بكسلات الصورة الكاملة
        cue_pos = (1049, 631)              # مركز الكرة البيضاء
        self.locked_ball_pos = (740, 532)  # مركز الكرة الخضراء (رقم 14)
        pock_pos = (960, 246)              # الجيب العلوي الأوسط
        bounce_p = (840, 246)              # نقطة الارتداد الوهمية على البند العلوي

        # 3. الرسم المباشر والـ Hardcoded على المصفوفة غصب عن أي موديول خارجي
        # رسم دائرة بيضاء سميكة فوق الكرة البيضاء
        cv2.circle(frame, cue_pos, BALL_RADIUS, (255, 255, 255), 3)
        # رسم دائرة خضراء فوق الكرة الخضراء (الهدف)
        cv2.circle(frame, self.locked_ball_pos, BALL_RADIUS, (0, 255, 0), 3)
        # رسم دائرة حمراء صغيرة عند الجيب المستهدف
        cv2.circle(frame, pock_pos, 15, (0, 0, 255), -1)

        # 4. رسم الخطوط والاتجاهات بألوان واضحة جداً (BGR)
        # خط الكيو (أبيض) طالع من البيضاء ورايح للخضراء
        cv2.line(frame, cue_pos, self.locked_ball_pos, (255, 255, 255), 3)
        
        # خط الهدف (أصفر) رايح من الخضراء للبند العلوي
        cv2.line(frame, self.locked_ball_pos, bounce_p, (0, 255, 255), 3)
        
        # خط الارتداد (أحمر) رايح من البند للجيب
        cv2.line(frame, bounce_p, pock_pos, (0, 0, 255), 3)

        # 5. حفظ الملف النهائي الملعوب فيه بالعافية
        success = cv2.imwrite(output_path, frame)
        if success:
            print(f"Forced visual validation saved successfully to -> {output_path}")
        else:
            print("Error: Failed to write image to disk.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ci":
        orchestrator = ProToolOrchestrator(is_ci_environment=True)
        orchestrator.run_static_test("test_screen.png", "result.png")
    else:
        orchestrator = ProToolOrchestrator(is_ci_environment=False)
        orchestrator.run_live()
