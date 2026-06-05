# main.py
import cv2
import numpy as np
import os
import sys
import time
from config.settings import TABLE_ROI, BALL_RADIUS, HOTKEYS, POWER_MODES
from modules.detector import TableDetector
from modules.physics_engine import PhysicsEngine
from modules.drawer import ScreenDrawer
from modules.controller import InputController

class ProToolOrchestrator:
    def __init__(self, is_ci_environment: bool = False):
        self.is_ci = is_ci_environment
        
        # استدعاء الموديولات الفرعية بالفصل التام (Separation of Concerns)
        self.detector = TableDetector(model_path="models/best.pt")
        self.physics = PhysicsEngine(table_bounds=TABLE_ROI, cushion_elasticity=0.85)
        self.drawer = ScreenDrawer()
        self.controller = InputController()
        
        # متغيرات الحالة الداخلية للبرنامج (State Management)
        self.selected_pocket_index = 0
        self.locked_ball_pos = None

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        العملية المركزية: قراءة ⬅️ تحليل ⬅️ فيزكس ⬅️ رسم
        """
        # 1. تشغيل الـ YOLO11 المخصص وجلب العناصر المكتشفة بالـ ROI Cropping
        detections = self.detector.detect_elements(frame, TABLE_ROI)
        
        # رسم الدوائر الأساسية للهكر حول الكور والجيوب المكتشفة
        frame = self.drawer.draw_detected_table(frame, detections)
        
        cue_ball_list = detections.get("cue_ball", [])
        object_balls = detections.get("object_balls", [])
        pockets = detections.get("pockets", [])
        
        # إذا لم يتم رصد الكرة البيضاء، نرجع الكادر المرسوم مبدئياً
        if not cue_ball_list:
            return frame
            
        cue_pos = (int(cue_ball_list[0][0]), int(cue_ball_list[0][1]))
        mouse_pos = self.controller.get_mouse_position() if not self.is_ci else (620, 430)
        
        # 2. نظام الـ Target Lock بالـ (Z Key) أو التوجيه الذكي لأقرب كورة للماوس
        if self.controller.is_key_pressed(HOTKEYS["TARGET_LOCK"]) or self.is_ci:
            if object_balls:
                # العثور على أقرب كرة مستهدفة لموقع الماوس الحالي
                closest_ball = min(object_balls, key=lambda b: np.hypot(b[0] - mouse_pos[0], b[1] - mouse_pos[1]))
                self.locked_ball_pos = (int(closest_ball[0]), int(closest_ball[1]))
        
        # قراءة لو تم اختيار جيب يدوي بالزراير من 1 لـ 6
        chosen_pocket = self.controller.get_active_pocket_by_hotkey()
        if chosen_pocket is not None:
            self.selected_pocket_index = chosen_pocket - 1
        elif self.is_ci and pockets:
            # في بيئة التيست بنقفل على أول جيب متاح أوتوماتيك
            self.selected_pocket_index = 0

        # 3. حساب المسارات بالـ Physics وصنع خطوط التوجيه الشبيهة بالشيتو
        if self.locked_ball_pos:
            # المسار المباشر (Direct Shot)
            cue_to_target = [cue_pos, self.locked_ball_pos]
            frame = self.drawer.draw_trajectory(frame, cue_to_target, line_type="cue_line", thickness=2)
            
            # رسم الكورة الوهمية (Ghost Ball) بمسافة التلامس الهندسية
            frame = self.drawer.draw_ghost_ball(frame, self.locked_ball_pos, radius=BALL_RADIUS)
            
            # لو رصدنا الجيوب، بنرسم خط الخروج للجيب المختار
            if pockets and self.selected_pocket_index < len(pockets):
                target_pocket = pockets[self.selected_pocket_index]
                pock_pos = (int(target_pocket[0]), int(target_pocket[1]))
                
                target_to_pocket = [self.locked_ball_pos, pock_pos]
                frame = self.drawer.draw_trajectory(frame, target_to_pocket, line_type="target_line", thickness=2)
                
                # 4. ضربات البند الذكية والـ Bank Shots بالـ (S Key)
                if self.controller.is_key_pressed(HOTKEYS["AUTO_BANK"]) or self.is_ci:
                    # حساب نقطة الارتداد على البند العلوي كمثال تطبيقي لـ Mirror Principle
                    bounce_p = self.physics.calculate_reflection_point(
                        start=self.locked_ball_pos,
                        pocket=pock_pos,
                        cushion_side="top",
                        power_mode=POWER_MODES["MEDIUM"]
                    )
                    bounce_path = [self.locked_ball_pos, (int(bounce_p[0]), int(bounce_p[1])), pock_pos]
                    frame = self.drawer.draw_trajectory(frame, bounce_path, line_type="bounce_line", thickness=2)

        return frame

    def run_live(self):
        """
        تشغيل المحرك لايف على الجهاز والتقاط الشاشة في الـ Real-time
        """
        import pyautogui
        print("=== 8BP Pro Tool Active (Press Ctrl+C to Stop) ===")
        
        # عمل تسمية للويندوز الشفاف الخاص بالـ Overlay
        cv2.namedWindow("8BP_Pro_Overlay", cv2.WINDOW_NORMAL)
        
        while True:
            start_time = time.time()
            
            # لقطة للشاشة كاملة
            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # المعالجة والتحليل
            output_frame = self.process_frame(frame)
            
            # حساب الـ FPS وعرضه بنعومة
            fps = 1.0 / (time.time() - start_time)
            cv2.putText(output_frame, f"FPS: {int(fps)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # عرض الرسم على الشاشة
            cv2.imshow("8BP_Pro_Overlay", output_frame)
            
            # زر الخروج Esc
            if cv2.waitKey(1) & 0xFF == 27:
                break
                
        cv2.destroyAllWindows()

    def run_static_test(self, input_path: str, output_path: str):
        """
        تشغيل وضع الفحص للـ GitHub Actions على الصورة الثابتة
        """
        print(f"Running CI Validation on {input_path}...")
        frame = cv2.imread(input_path)
        if frame is None:
            print(f"Error: Unable to load {input_path}")
            sys.exit(1)
            
        output_frame = self.process_frame(frame)
        cv2.imwrite(output_path, output_frame)
        print(f"Success! Verification output saved as {output_path}")

if __name__ == "__main__":
    # فحص البيئة لو كانت GitHub Actions أو تشغيل عادي
    if len(sys.argv) > 1 and sys.argv[1] == "--ci":
        orchestrator = ProToolOrchestrator(is_ci_environment=True)
        orchestrator.run_static_test("test_screen.png", "result.png")
    else:
        # التشغيل العادي على جهازك يا صاحبي
        orchestrator = ProToolOrchestrator(is_ci_environment=False)
        # إذا لم تكن الصورة موجودة كـ اختبار محلي يعمل لايف، وإلا يشغل التيست لغايات الفحص والـ Pipeline
        if os.path.exists("test_screen.png"):
            orchestrator.run_static_test("test_screen.png", "result.png")
        else:
            orchestrator.run_live()
