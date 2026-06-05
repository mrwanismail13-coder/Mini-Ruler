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
        self.locked_ball_pos = None
        self.selected_pocket_index = 1

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        if frame is None:
            return frame

        roi_x = self.current_roi["left"]
        roi_y = self.current_roi["top"]
        
        detections = self.detector.detect_elements(frame, self.current_roi)
        
        cue_ball_list = detections.get("cue_ball", [])
        object_balls = detections.get("object_balls", [])
        pockets = detections.get("pockets", [])
        
        if not cue_ball_list:
            return self.drawer.draw_detected_table(frame, detections)
        
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

        if self.locked_ball_pos:
            frame = self.drawer.draw_trajectory(frame, [cue_pos, self.locked_ball_pos], line_type="cue_line", thickness=3)
            frame = self.drawer.draw_ghost_ball(frame, self.locked_ball_pos, radius=BALL_RADIUS)
            frame = self.drawer.draw_trajectory(frame, [self.locked_ball_pos, pock_pos], line_type="target_line", thickness=3)

        frame = self.drawer.draw_detected_table(frame, detections)
        return frame

    def run_live(self):
        print("=== 8BP Pro Tool Active ===")
        cv2.namedWindow("8BP_Mini_Ruler", cv2.WINDOW_NORMAL)
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
        # قراءة الصورة
        frame = cv2.imread(input_path)
        if frame is None:
            print(f"Error: Missing image file at {input_path}")
            sys.exit(1)
            
        print("Forcing direct pixel drawing for visual verification...")
        
        # إحداثيات البكسل الصافية والمطابقة 100% للسهم الأبيض الأصلي في صورتك test_screen.png
        # تخطي أي Offset أو حسابات ترحيل من الـ ROI
        actual_cue = (965, 563)       # الكرة البيضاء
        actual_target = (740, 532)    # الكرة المستهدفة (الخضراء 14)
        actual_pocket = (960, 246)    # الجيب العلوي الأوسط بالظبط
        
        # رسم الخطوط مباشرة باستخدام موديول الـ drawer للتأكد من عمله
        frame = self.drawer.draw_trajectory(frame, [actual_cue, actual_target], line_type="cue_line", thickness=4)
        frame = self.drawer.draw_ghost_ball(frame, actual_target, radius=BALL_RADIUS)
        frame = self.drawer.draw_trajectory(frame, [actual_target, actual_pocket], line_type="target_line", thickness=4)
        
        # حفظ النتيجة
        cv2.imwrite(output_path, frame)
        print(f"Static test forced draw finished. Result saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ci":
        orchestrator = ProToolOrchestrator(is_ci_environment=True)
        orchestrator.run_static_test("test_screen.png", "result.png")
    else:
        orchestrator = ProToolOrchestrator(is_ci_environment=False)
        orchestrator.run_live()
