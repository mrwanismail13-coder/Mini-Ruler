import cv2
import numpy as np
import time

from config.settings import TABLE_ROI, PLAYABLE_CUSHIONS, BALL_RADIUS, POWER_MODES, HOTKEYS
from modules.detector import TableDetector
from modules.physics_engine import PhysicsEngine
from modules.drawer import ScreenDrawer
from modules.controller import InputController


class ProToolOrchestrator:
    def __init__(self):
        self.detector = TableDetector("models/best.pt")
        self.physics = PhysicsEngine(TABLE_ROI, cushion_elasticity=0.85)
        self.drawer = ScreenDrawer()
        self.controller = InputController()

        self.current_pocket_index = 0
        self.locked_target = None

    # =========================
    # CORE PIPELINE
    # =========================
    def process_frame(self, frame: np.ndarray) -> np.ndarray:

        detections = self.detector.detect_elements(frame, TABLE_ROI)

        cue_list = detections.get("cue_ball", [])
        object_balls = detections.get("object_balls", [])
        pockets = detections.get("pockets", [])

        # لازم يكون فيه كورة بيضا
        if not cue_list or len(object_balls) == 0 or len(pockets) == 0:
            return self.drawer.draw_detected_table(frame, detections)

        cue = (int(cue_list[0][0]), int(cue_list[0][1]))

        # =========================
        # TARGET SELECTION (Closest ball)
        # =========================
        if self.controller.is_key_pressed(HOTKEYS["TARGET_LOCK"]):
            mouse = self.controller.get_mouse_position()

            self.locked_target = min(
                object_balls,
                key=lambda b: np.hypot(b[0] - mouse[0], b[1] - mouse[1])
            )

        if self.locked_target is None:
            target = object_balls[0]
        else:
            target = self.locked_target

        target = (int(target[0]), int(target[1]))

        # =========================
        # POCKET SELECTION
        # =========================
        pocket_index = self.controller.get_active_pocket_by_hotkey()
        if pocket_index:
            self.current_pocket_index = pocket_index - 1

        pocket = pockets[self.current_pocket_index]
        pocket = (int(pocket[0]), int(pocket[1]))

        # =========================
        # PHYSICS INTEGRATION (CORE FIX)
        # =========================

        # 1- Ghost ball position (critical physics step)
        dx = target[0] - pocket[0]
        dy = target[1] - pocket[1]
        dist = np.hypot(dx, dy)

        if dist == 0:
            return frame

        ghost_ball = (
            int(target[0] + (dx / dist) * (BALL_RADIUS * 2)),
            int(target[1] + (dy / dist) * (BALL_RADIUS * 2))
        )

        # 2- Choose cushion dynamically (simple heuristic)
        cushion_side = "top" if target[1] < pocket[1] else "bottom"

        # 3- Physics bounce calculation (REAL USE)
        bounce = self.physics.calculate_reflection_point(
            start=cue,
            pocket=pocket,
            cushion_side=cushion_side,
            power_mode=POWER_MODES["MEDIUM"]
        )

        # =========================
        # DRAW RESULTS
        # =========================

        # cue → target
        frame = self.drawer.draw_trajectory(frame, [cue, target], "cue_line", 3)

        # target → pocket (direct line)
        frame = self.drawer.draw_trajectory(frame, [target, pocket], "target_line", 2)

        # physics bounce indicator
        frame = self.drawer.draw_trajectory(frame, [cue, bounce], "bounce_line", 2)

        # ghost ball visualization
        frame = self.drawer.draw_ghost_ball(frame, ghost_ball, BALL_RADIUS)

        # pocket highlight path
        frame = self.drawer.draw_trajectory(frame, [bounce, pocket], "combo_line", 2)

        return frame

    # =========================
    # LIVE MODE
    # =========================
    def run_live(self):
        import pyautogui

        cv2.namedWindow("8BP Physics AI", cv2.WINDOW_NORMAL)

        while True:
            start = time.time()

            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            output = self.process_frame(frame)

            fps = 1.0 / (time.time() - start)
            cv2.putText(output, f"FPS: {int(fps)}", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("8BP Physics AI", output)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cv2.destroyAllWindows()


if __name__ == "__main__":
    ProToolOrchestrator().run_live()
