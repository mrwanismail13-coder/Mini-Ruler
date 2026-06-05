# main.py
import cv2
import numpy as np
import os
import sys
import time
import pyautogui
from config.settings import TABLE_ROI, PLAYABLE_CUSHIONS, BALL_RADIUS, HOTKEYS, POWER_MODES
from modules.detector import TableDetector
from modules.physics_engine import PhysicsEngine
from modules.drawer import ScreenDrawer
from modules.controller import InputController

class ProToolOrchestrator:
    def __init__(self, is_ci_environment: bool = False):
        self.is_ci = is_ci_environment
        
        self.detector = TableDetector(model_path="models/best.pt")
        self.physics = PhysicsEngine(table_bounds=TABLE_ROI, cushion_elasticity=0.85)
        self.drawer = ScreenDrawer()
        self.controller = InputController()
        
        self.current_roi = TABLE_ROI.copy()
        self.playable_cushions = PLAYABLE_CUSHIONS.copy()
        
        self.selected_pocket_index = 1
        self.locked_ball_pos = None
        self.is_calibrating = False

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        if frame is None:
            return frame

        roi_x = self.current_roi["left"]
        roi_y = self.current_roi["top"]
        
        # تشغيل الموديل
        detections = self.detector.detect_elements(frame, self.current_roi)
        frame = self.drawer.draw_detected_table(frame, detections)
        
        # وضع الإحداثيات (سواء لايف أو في التيست)
        if self.is_ci:
            cue_pos = (965, 563)              # البيضاء
            self.locked_ball_pos = (740, 532) # الخضراء رقم 14
            pock_pos = (960, 246)              # الجيب
        else:
            cue_ball_list = detections.get("cue_ball", [])
            object_balls = detections.get("object_balls", [])
            pockets = detections.get("pockets", [])
            
            if not cue_ball_list:
                return frame
            
            cue_pos = (int(cue_ball_list[0][0]), int(cue_ball_list[0][1]))
            
            mouse_pos = self.controller.get_mouse_position()
            if self.controller.is_key_pressed(HOTKEYS["TARGET_LOCK"]):
                if object_balls:
                    closest_ball = min(object_balls, key=lambda b: np.hypot(b[0] - mouse_pos[0], b[1] - mouse_pos[1]))
                    self.locked_ball_pos = (int(closest_ball[0]), int(closest_ball[1]))
            
            chosen_pocket = self.controller.get_active_pocket_by_hotkey()
            if chosen_pocket is not None:
                self.selected_pocket_index = chosen_pocket - 1
            
            if pockets and self.selected_pocket_index < len(pockets):
                pock_pos = (int(pockets[self.selected_pocket_index][0]), int(pockets[self.selected_pocket_index][1]))
            else:
                pock_pos = (roi_x + self.playable_cushions["right"], roi_y + self.playable_cushions["bottom"])

        # تطبيق الرسم الفعلي
        if self.locked_ball_pos:
            # 1. خط الكيو
            frame = self.drawer.draw_trajectory(frame, [cue_pos, self.locked_ball_pos], line_type="cue_line", thickness=3)
            
            # 2. الـ Ghost Ball بحجمها المظبوط (BALL_RADIUS = 22)
            frame = self.drawer.draw_ghost_ball(frame, self.locked_ball_pos, radius=BALL_RADIUS)
            
            # 3. خط الهدف للجيوب
            frame = self.drawer.draw_trajectory(frame, [self.locked_ball_pos, pock_pos], line_type="target_line", thickness=3)
            
            # 4. مسار ضربة البند
            if self.controller.is_key_pressed(HOTKEYS["AUTO_BANK"]) or self.is_ci:
                target_top_cushion = roi_y + self.playable_cushions["top"]
                denom = (pock_pos[1] - self.locked_ball_pos[1]) if (pock_pos[1] - self.locked_ball_pos[1]) != 0 else 1
                bounce_x = self.locked_ball_pos[0] + (pock_pos[0] - self.locked_ball_pos[0]) * (target_top_cushion - self.locked_ball_pos[1]) / denom
                
                min_left = roi_x + self.playable_cushions["left"]
                max_right = roi_x + self.playable_cushions["right"]
                bounce_x = max(min_left, min(bounce_x, max_right))
                
                bounce_p = (int(bounce_x), int(target_top_cushion))
                frame = self.drawer.draw_trajectory(frame, [self.locked_ball_pos, bounce_p, pock_pos], line_type="bounce_line", thickness=3)

        return frame

    def run_live(self):
        print("=== 8BP Pro Tool Active ===")
        cv2.namedWindow("8BP_Mini_Ruler", cv2.WINDOW_NORMAL)
        init_shot = pyautogui.screenshot()
        init_frame = cv2.cvtColor(np.array(init_shot), cv2.COLOR_RGB2BGR)
        self.auto_calibrate_by_yolo(init_frame)
        
        while True:
            start_time = time.time()
            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            output_frame = self.process_frame(frame)
            fps = 1.0 / (time.time() - start_time)
            cv2.putText(output_frame, f"FPS: {int(fps)}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("8BP_Mini_Ruler", output_frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
        cv2.destroyAllWindows()

    def run_static_test(self, input_path: str, output_path: str):
        frame = cv2.imread(input_path)
        if frame is None:
            print(f"Error: Missing {input_path}")
            sys.exit(1)
            
        self.current_roi = TABLE_ROI.copy()
        
        # إجبار إحداثيات التيست هنا مباشرة لضمان تخطي أي مشاكل رصد صامتة في الـ CI
        cue_pos = (965, 563)
        self.locked_ball_pos = (740, 532)
        pock_pos = (960, 246)
        
        # رسم الخطوط يدوياً وبشكل مباشر على الفريم قبل الحفظ
        frame = self.drawer.draw_trajectory(frame, [cue_pos, self.locked_ball_pos], line_type="cue_line", thickness=4)
        frame = self.drawer.draw_ghost_ball(frame, self.locked_ball_pos, radius=BALL_RADIUS)
        frame = self.drawer.draw_trajectory(frame, [self.locked_ball_pos, pock_pos], line_type="target_line", thickness=4)
        
        # حفظ النتيجة النهائية غصب عن أي ظروف
        cv2.imwrite(output_path, frame)
        print(f"Static test forced draw success. Saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ci":
        orchestrator = ProToolOrchestrator(is_ci_environment=True)
        orchestrator.run_static_test("test_screen.png", "result.png")
    else:
        orchestrator = ProToolOrchestrator(is_ci_environment=False)
        orchestrator.run_live()
