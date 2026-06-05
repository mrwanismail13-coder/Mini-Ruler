import cv2
import numpy as np
import time
import sys

from config.settings import TABLE_ROI, BALL_RADIUS, HOTKEYS, POWER_MODES
from modules.detector import TableDetector
from modules.physics_engine import PhysicsEngine
from modules.drawer import ScreenDrawer
from modules.controller import InputController
from modules.hud_overlay import HUDOverlay


class ProToolOrchestrator:
    def __init__(self, is_ci_environment: bool = False):
        self.is_ci = is_ci_environment

        # Core systems
        self.detector = TableDetector("models/best.pt")
        self.physics = PhysicsEngine(TABLE_ROI, cushion_elasticity=0.85)
        self.drawer = ScreenDrawer()
        self.controller = InputController()
        self.hud = HUDOverlay()

        # State
        self.current_pocket_index = 0
        self.locked_target = None

    # =========================
    # MAIN PIPELINE
    # =========================
    def process_frame(self, frame: np.ndarray) -> np.ndarray:

        detections = self.detector.detect_elements(frame, TABLE_ROI)

        cue_list = detections.get("cue_ball", [])
        object_balls = detections.get("object_balls", [])
        pockets = detections.get("pockets", [])

        # لازم يكون فيه cue ball
        if not cue_list:
            return self.hud.draw_balls(frame, detections)

        cue = (int(cue_list[0][0]), int(cue_list[0][1]))

        # =========================
        # TARGET SELECTION (manual + auto)
        # =========================
        if object_balls:
            if self.controller.is_key_pressed(HOTKEYS["TARGET_LOCK"]):
                mouse = self.controller.get_mouse_position()

                self.locked_target = min(
                    object_balls,
                    key=lambda b: np.hypot(b[0] - mouse[0], b[1] - mouse[1])
                )

        target = self.locked_target if self.locked_target else object_balls[0] if object_balls else None

        if target is None or len(pockets) == 0:
            return self.hud.draw_balls(frame, detections)

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
        # PHYSICS CORE
        # =========================

        dx = target[0] - pocket[0]
        dy = target[1] - pocket[1]
        dist = np.hypot(dx, dy)

        if dist == 0:
            return frame

        # Ghost ball calculation
        ghost_ball = (
            int(target[0] + (dx / dist) * (BALL_RADIUS * 2)),
            int(target[1] + (dy / dist) * (BALL_RADIUS * 2))
        )

        # Cushion decision (simple heuristic)
        cushion_side = "top" if target[1] < pocket[1] else "bottom"

        bounce = self.physics.calculate_reflection_point(
            start=cue,
            pocket=pocket,
            cushion_side=cushion_side,
            power_mode=POWER_MODES["MEDIUM"]
        )

        # =========================
        # DRAWING SYSTEM (HUD STYLE)
        # =========================

        # balls + pockets
        frame = self.hud.draw_balls(frame, detections)

        # cue → target
        frame = self.hud.draw_path(frame, [cue, target], "path")

        # target → pocket
        frame = self.hud.draw_path(frame, [target, pocket], "bank")

        # bounce path
        frame = self.hud.draw_path(frame, [cue, bounce], "combo")

        # ghost ball
        frame = self.hud.draw_ghost(frame, ghost_ball)

        # multi-layer preview (optional future paths)
        frame = self.hud.draw_multi_paths(frame, [
            [cue, target, pocket],
            [cue, bounce, pocket]
        ])

        # UI panel
        frame = self.hud.draw_panel(
            frame,
            target,
            self.current_pocket_index,
            mode="MEDIUM"
        )

        return frame

    # =========================
    # CI TEST MODE
    # =========================
    def run_static_test(self, input_path: str, output_path: str):
        frame = cv2.imread(input_path)

        if frame is None:
            raise FileNotFoundError(f"Missing file: {input_path}")

        result = self.process_frame(frame)

        cv2.imwrite(output_path, result)
        print(f"[OK] Output saved → {output_path}")

    # =========================
    # LIVE MODE
    # =========================
    def run_live(self):
        import pyautogui

        if self.is_ci:
            print("CI mode active - live disabled")
            return

        cv2.namedWindow("8BP AI HUD", cv2.WINDOW_NORMAL)

        while True:
            start = time.time()

            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            output = self.process_frame(frame)

            fps = 1.0 / (time.time() - start)
            cv2.putText(output, f"FPS: {int(fps)}", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("8BP AI HUD", output)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cv2.destroyAllWindows()


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "--ci":
        ProToolOrchestrator(is_ci_environment=True).run_static_test(
            "test_screen.png",
            "result.png"
        )
    else:
        ProToolOrchestrator().run_live()
