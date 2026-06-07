import cv2
import numpy as np
import time
import sys

from config.settings import TABLE_ROI, BALL_RADIUS, HOTKEYS, POWER_MODES
from modules.detector import TableDetector
from modules.physics_engine import PhysicsEngine
from modules.drawer import ScreenDrawer
from modules.controller import InputController
from modules.white_ball_tracker import WhiteBallTracker
from modules.hud_menu import HUDMenu
from modules.transparent_overlay import TransparentOverlay


class ProToolOrchestrator:
    def __init__(self, is_ci_environment: bool = False):

        self.is_ci = is_ci_environment

        # ================= CORE =================
        self.detector = TableDetector("models/best.pt")
        self.physics = PhysicsEngine(TABLE_ROI, cushion_elasticity=0.85)
        self.drawer = ScreenDrawer()
        self.controller = InputController()

        # ================= AI HELPERS =================
        self.tracker = WhiteBallTracker()
        self.menu = HUDMenu()
        self.overlay = TransparentOverlay()

        # ================= STATE =================
        self.locked_target = None
        self.selected_pocket = 0

    # =========================================================
    # 🎯 AUTO TARGET RANKING ENGINE
    # =========================================================
    def score_ball(self, cue, ball, pocket):
        d_cue = np.hypot(ball[0] - cue[0], ball[1] - cue[1])
        d_pocket = np.hypot(ball[0] - pocket[0], ball[1] - pocket[1])

        score = 0
        score += max(0, 1000 - d_pocket)
        score += max(0, 1000 - d_cue)

        return score

    def select_best_target(self, cue, object_balls, pocket):
        best_ball = None
        best_score = -1

        for ball in object_balls:
            score = self.score_ball(cue, ball, pocket)

            if score > best_score:
                best_score = score
                best_ball = ball

        return best_ball

    # ================= FRAME PIPELINE =================
    def process_frame(self, frame: np.ndarray) -> np.ndarray:

        detections = self.detector.detect_elements(frame, TABLE_ROI)

        cue = self.tracker.update(detections)

        object_balls = detections.get("object_balls", [])
        pockets = detections.get("pockets", [])

        if cue is None or len(object_balls) == 0 or len(pockets) == 0:
            return self.menu.draw(frame)

        cue = (int(cue[0]), int(cue[1]))

        # ================= TARGET LOCK =================
        if self.controller.is_key_pressed(HOTKEYS["TARGET_LOCK"]):
            mouse = self.controller.get_mouse_position()

            self.locked_target = min(
                object_balls,
                key=lambda b: np.hypot(b[0] - mouse[0], b[1] - mouse[1])
            )

        # ================= AUTO TARGET RANKING =================
        if self.locked_target:
            target = self.locked_target
        else:
            target = self.select_best_target(
                cue,
                object_balls,
                pockets[self.selected_pocket]
            )

        target = (int(target[0]), int(target[1]))

        # ================= POCKET =================
        pocket = pockets[self.selected_pocket]
        pocket = (int(pocket[0]), int(pocket[1]))

        # ================= PHYSICS =================
        dx = target[0] - pocket[0]
        dy = target[1] - pocket[1]
        dist = np.hypot(dx, dy)

        if dist == 0:
            return frame

        ghost_ball = (
            int(target[0] + (dx / dist) * (BALL_RADIUS * 2)),
            int(target[1] + (dy / dist) * (BALL_RADIUS * 2))
        )

        bounce = self.physics.calculate_reflection_point(
            start=cue,
            pocket=pocket,
            cushion_side="top" if target[1] < pocket[1] else "bottom",
            power_mode=POWER_MODES["MEDIUM"]
        )

        # ================= RENDER =================
        frame = self.drawer.draw_detected_table(frame, detections)

        frame = self.drawer.draw_trajectory(frame, [cue, target], "cue_line", 2)
        frame = self.drawer.draw_trajectory(frame, [target, pocket], "target_line", 2)
        frame = self.drawer.draw_trajectory(frame, [cue, bounce], "combo_line", 2)

        frame = self.drawer.draw_ghost_ball(frame, ghost_ball, BALL_RADIUS)

        frame = self.menu.draw(frame)

        return frame

    # ================= CI TEST =================
    def run_static_test(self, input_path: str, output_path: str):

        frame = cv2.imread(input_path)

        if frame is None:
            raise FileNotFoundError(f"Missing file: {input_path}")

        result = self.process_frame(frame)

        cv2.imwrite(output_path, result)
        print(f"[OK] Saved → {output_path}")

    # ================= LIVE MODE =================
    def run_live(self):

        if self.is_ci:
            print("CI mode active")
            return

        import pyautogui

        cv2.namedWindow("AI_OVERLAY", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("AI_OVERLAY", cv2.WND_PROP_TOPMOST, 1)

        while True:

            start = time.time()

            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            output = self.process_frame(frame)

            fps = 1.0 / (time.time() - start)

            cv2.putText(output, f"FPS: {int(fps)}", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            self.overlay.show(output)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cv2.destroyAllWindows()


# ================= ENTRY =================
if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "--ci":
        ProToolOrchestrator(is_ci_environment=True).run_static_test(
            "test_screen.png",
            "result.png"
        )
    else:
        ProToolOrchestrator().run_live()