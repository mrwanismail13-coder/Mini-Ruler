import cv2
import numpy as np
import time
import sys
import pyautogui

from config.settings import TABLE_ROI, BALL_RADIUS, HOTKEYS

from modules.detector import TableDetector
from modules.physics_engine import PhysicsEngine
from modules.drawer import ScreenDrawer
from modules.controller import InputController
from modules.white_ball_tracker import WhiteBallTracker
from modules.hud_menu import HUDMenu
from modules.transparent_overlay import TransparentOverlay

from modules.obstacle_detector import ObstacleDetector
from modules.auto_reroute import AutoReroute
from modules.shot_difficulty import ShotDifficultyEngine


class ProToolOrchestrator:

    def __init__(self, is_ci_environment: bool = False):

        self.is_ci = is_ci_environment

        # ================= CORE =================
        self.detector = TableDetector("models/best.pt")
        self.drawer = ScreenDrawer()
        self.controller = InputController()

        # ================= AI MODULES =================
        self.tracker = WhiteBallTracker()
        self.menu = HUDMenu()
        self.overlay = TransparentOverlay()

        self.obstacles = ObstacleDetector()
        self.rerouter = AutoReroute(TABLE_ROI)
        self.shot_ai = ShotDifficultyEngine()

        # ================= STATE =================
        self.locked_target = None
        self.selected_pocket = 0

    # =========================
    # AUTO TARGET RANKING (WITH SHOT AI)
    # =========================
    def rank_targets(self, cue, object_balls, pocket):

        best_ball = None
        best_score = float("inf")

        for ball in object_balls:

            bx, by = ball[0], ball[1]

            score = self.shot_ai.evaluate_shot(
                cue,
                (bx, by),
                pocket,
                [(b[0], b[1]) for b in object_balls]
            )

            if score < best_score:
                best_score = score
                best_ball = ball

        return best_ball

    # =========================
    # FRAME PROCESSING
    # =========================
    def process_frame(self, frame):

        detections = self.detector.detect_elements(frame, TABLE_ROI)

        cue = self.tracker.update(detections)

        object_balls = detections.get("object_balls", [])
        pockets = detections.get("pockets", [])

        if cue is None or len(object_balls) == 0 or len(pockets) == 0:
            return self.menu.draw(frame)

        cue = (int(cue[0]), int(cue[1]))

        # pocket selection
        pocket = pockets[self.selected_pocket]
        pocket = (int(pocket[0]), int(pocket[1]))

        # =========================
        # TARGET SELECTION (AI)
        # =========================
        target = self.rank_targets(cue, object_balls, pocket)
        target = (int(target[0]), int(target[1]))

        # obstacles
        blockers = self.obstacles.find_blocking_balls(
            cue,
            target,
            [(b[0], b[1]) for b in object_balls]
        )

        # reroute
        route, mode = self.rerouter.find_best_route(
            cue,
            target,
            blockers
        )

        # =========================
        # RENDER
        # =========================
        frame = self.drawer.draw_detected_table(frame, detections)

        frame = self.drawer.draw_trajectory(frame, route, "combo_line", 2)

        frame = self.drawer.draw_ghost_ball(frame, target, BALL_RADIUS)

        # ================= DEBUG =================
        cv2.putText(frame, f"SHOT AI ACTIVE", (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.putText(frame, f"MODE: {mode}", (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.putText(frame, f"TARGET: AUTO RANKED", (30, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        return frame

    # =========================
    # LIVE MODE
    # =========================
    def run_live(self):

        if self.is_ci:
            return

        cv2.namedWindow("AI_OVERLAY", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("AI_OVERLAY", cv2.WND_PROP_TOPMOST, 1)

        while True:

            start = time.time()

            screen = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

            output = self.process_frame(frame)

            fps = 1.0 / (time.time() - start)

            cv2.putText(output, f"FPS: {int(fps)}", (30, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            self.overlay.show(output)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cv2.destroyAllWindows()


# ================= ENTRY =================
if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "--ci":
        ProToolOrchestrator(True).run_static_test(
            "test_screen.png",
            "result.png"
        )
    else:
        ProToolOrchestrator().run_live()