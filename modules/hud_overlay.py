import cv2
import numpy as np


class HUDOverlay:
    def __init__(self):
        self.colors = {
            "cue": (255, 255, 255),
            "object": (0, 255, 0),
            "pocket": (0, 0, 255),
            "ghost": (200, 200, 200),
            "path": (255, 255, 0),
            "bank": (0, 255, 255),
            "combo": (255, 0, 255),
            "ui_bg": (30, 30, 30)
        }

    # =========================
    # DRAW BALLS
    # =========================
    def draw_balls(self, frame, detections):
        for b in detections.get("object_balls", []):
            cv2.circle(frame, (int(b[0]), int(b[1])), 10, self.colors["object"], 2)

        if detections.get("cue_ball"):
            c = detections["cue_ball"][0]
            cv2.circle(frame, (int(c[0]), int(c[1])), 12, self.colors["cue"], 2)

        for p in detections.get("pockets", []):
            cv2.circle(frame, (int(p[0]), int(p[1])), 14, self.colors["pocket"], 2)

        return frame

    # =========================
    # DRAW PATH LINE
    # =========================
    def draw_path(self, frame, points, color="path", thickness=2):
        for i in range(len(points) - 1):
            cv2.line(
                frame,
                (int(points[i][0]), int(points[i][1])),
                (int(points[i + 1][0]), int(points[i + 1][1])),
                self.colors[color],
                thickness
            )
        return frame

    # =========================
    # GHOST BALL
    # =========================
    def draw_ghost(self, frame, pos):
        cv2.circle(frame, (int(pos[0]), int(pos[1])), 12, self.colors["ghost"], 1)
        cv2.circle(frame, (int(pos[0]), int(pos[1])), 2, self.colors["ghost"], -1)
        return frame

    # =========================
    # UI PANEL (LIKE VIDEO MENU)
    # =========================
    def draw_panel(self, frame, target, pocket_index, mode="MEDIUM"):
        h, w = frame.shape[:2]

        cv2.rectangle(frame, (10, 10), (280, 180), self.colors["ui_bg"], -1)

        cv2.putText(frame, "8BP AI HUD", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.putText(frame, f"Target: {target}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.putText(frame, f"Pocket: {pocket_index + 1}", (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.putText(frame, f"Mode: {mode}", (20, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        return frame

    # =========================
    # MULTI PATH PREVIEW
    # =========================
    def draw_multi_paths(self, frame, paths):
        colors = ["path", "bank", "combo"]

        for i, path in enumerate(paths):
            color = colors[i % len(colors)]
            frame = self.draw_path(frame, path, color=color, thickness=2)

        return frame
