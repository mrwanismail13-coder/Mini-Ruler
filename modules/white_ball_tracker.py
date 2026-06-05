import numpy as np
import cv2


class WhiteBallTracker:
    def __init__(self):
        self.last_pos = None
        self.alpha = 0.35  # smoothing factor

    def update(self, detections):
        cue_list = detections.get("cue_ball", [])

        if not cue_list:
            return self.last_pos

        x, y = cue_list[0][0], cue_list[0][1]

        if self.last_pos is None:
            self.last_pos = (x, y)
            return self.last_pos

        # smoothing (important for stability)
        lx, ly = self.last_pos

        nx = int(lx + self.alpha * (x - lx))
        ny = int(ly + self.alpha * (y - ly))

        self.last_pos = (nx, ny)
        return self.last_pos
