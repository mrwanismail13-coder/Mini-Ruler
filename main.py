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


class ProToolOrchestrator:

    def __init__(self, is_ci_environment: bool = False):

        self.is_ci = is_ci_environment

        # CORE
        self.detector = TableDetector("models/best.pt")
        self.drawer = ScreenDrawer()
        self.controller = InputController()

        # AI
        self.tracker = WhiteBallTracker()
        self.menu = HUDMenu()
        self.overlay = TransparentOverlay()

        # NEW SYSTEMS
        self.obstacles = ObstacleDetector()
        self.rerouter = AutoReroute(TABLE_ROI)

        # STATE
        self.locked_target = None
        self.selected_pocket = 0

    # =========================
    # AUTO TARGET RANKING
    # =========================
    def rank_targets(self, cue, object_balls, pocket):

        best_ball = None
        best_score = float("inf")

        for ball in object_balls:

            bx, by = ball[0], ball[1]

            # distance cue -> ball
            d1 = np.hypot(cue[0] - bx, cue[1] - by)

            # distance ball -> pocket
            d2 = np.hypot(pocket[0] - bx, pocket[1] - by)

            # obstacle penalty (simple check)
            blockers = self.obstacles.find_blocking_balls(
                cue,
                (bx, by),
                [(b[0], b[1]) for b in object_balls]
            )

            penalty = len(blockers) * 200  # كل عائق يقلل الاختيار

            score = d1 + d2 + penalty

            if score < best_score:
                best_score = score
                best_ball = ball

        return best_ball

    # =========================
    # PROCESS FRAME
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
        # AUTO TARGET RANKING (NEW)
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

        # render base
        frame = self.drawer.draw_detected_table(frame, detections)

        # draw route
        frame = self.drawer.draw_trajectory(frame, route, "combo_line", 2)

        # ghost ball
        ghost = (
            int(target[0]),
            int(target[1])
        )

        frame = self.drawer.draw_ghost_ball(frame, ghost, BALL_RADIUS)

        # debug info
        cv2.putText(frame, f"MODE: {mode}", (30, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        cv2.putText(frame, f"TARGET SCORE SYSTEM ACTIVE", (30, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        return frame

    # =========================
    # LIVE
    # =========================
    def run_live(self):

        if self.is_ci:
            return

        cv2.namedWindow("AI_OVERLAY", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("AI_OVERLAY", cv2.WND_PROP_TOPMOST, 1)

        while True:

            start = time.time()

            frame = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

            output = self.process_frame(frame)

            fps = 1.0 / (time.time() - start)

            cv2.putText(output, f"FPS: {int(fps)}", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            self.overlay.show(output)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cv2.destroyAllWindows()


# ENTRY
if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "--ci":
        ProToolOrchestrator(True).run_static_test("test_screen.png", "result.png")
    else:
        ProToolOrchestrator().run_live()