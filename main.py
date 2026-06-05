import cv2
import numpy as np
import sys
import time
import platform

from config.settings import TABLE_ROI, PLAYABLE_CUSHIONS, BALL_RADIUS, HOTKEYS
from modules.detector import TableDetector
from modules.physics_engine import PhysicsEngine
from modules.drawer import ScreenDrawer
from modules.controller import InputController

# محاولة استيراد pyautogui (مهم للـ CI)
try:
    import pyautogui
except Exception:
    pyautogui = None


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
                closest_ball = min(
                    object_balls,
                    key=lambda b: np.hypot(b[0] - mouse_pos[0], b[1] - mouse_pos[1])
                )
                self.locked_ball_pos = (int(closest_ball[0]), int(closest_ball[1]))

        chosen_pocket = self.controller.get_active_pocket_by_hotkey()
        if chosen_pocket is not None:
            self.selected_pocket_index = chosen_pocket - 1

        if pockets and self.selected_pocket_index < len(pockets):
            pock_pos = (
                int(pockets[self.selected_pocket_index][0]),
                int(pockets[self.selected_pocket_index][1])
            )
        else:
            pock_pos = (
                self.current_roi["left"] + self.playable_cushions["right"],
                self.current_roi["top"] + self.playable_cushions["bottom"]
            )

        if self.locked_ball_pos:
            frame = self.drawer.draw_trajectory(frame, [cue_pos, self.locked_ball_pos], "cue_line", 3)
            frame = self.drawer.draw_ghost_ball(frame, self.locked_ball_pos, BALL_RADIUS)
            frame = self.drawer.draw_trajectory(frame, [self.locked_ball_pos, pock_pos], "target_line", 3)

        return self.drawer.draw_detected_table(frame, detections)

    # =========================
    # CI SAFE MODE (NO SCREENSHOT)
    # =========================
    def run_static_test(self, input_path: str, output_path: str):
        frame = cv2.imread(input_path)

        if frame is None:
            raise FileNotFoundError(f"Missing test image: {input_path}")

        result = self.process_frame(frame)

        cv2.imwrite(output_path, result)
        print(f"Test completed → {output_path}")

    # =========================
    # LIVE MODE (WINDOWS ONLY)
    # =========================
    def run_live(self):
        if self.is_ci or pyautogui is None:
            print("Live mode disabled in CI environment")
            return

        cv2.namedWindow("8BP Tool", cv2.WINDOW_NORMAL)

        while True:
            start = time.time()

            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            output = self.process_frame(frame)

            fps = 1.0 / (time.time() - start)
            cv2.putText(output, f"FPS: {int(fps)}", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("8BP Tool", output)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ci":
        ProToolOrchestrator(is_ci_environment=True).run_static_test(
            "test_screen.png",
            "result.png"
        )
    else:
        ProToolOrchestrator().run_live()
