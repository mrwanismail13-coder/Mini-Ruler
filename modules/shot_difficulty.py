import numpy as np
import math


class ShotDifficultyEngine:

    def __init__(self):
        pass

    # =========================
    # ANGLE DIFFICULTY
    # =========================
    def angle_penalty(self, a, b, c):

        # زاوية بين 3 نقاط (cue -> target -> pocket)
        ba = np.array([a[0] - b[0], a[1] - b[1]])
        bc = np.array([c[0] - b[0], c[1] - b[1]])

        dot = np.dot(ba, bc)
        norm = np.linalg.norm(ba) * np.linalg.norm(bc)

        if norm == 0:
            return 100

        cos_angle = dot / norm
        cos_angle = np.clip(cos_angle, -1, 1)

        angle = math.degrees(math.acos(cos_angle))

        # كل ما الزاوية تكبر = أسهل
        return abs(180 - angle)

    # =========================
    # DISTANCE DIFFICULTY
    # =========================
    def distance_penalty(self, p1, p2, scale=1.0):

        dist = np.hypot(p1[0] - p2[0], p1[1] - p2[1])
        return dist * scale

    # =========================
    # BLOCKER CHECK
    # =========================
    def blocker_penalty(self, cue, target, balls):

        penalty = 0

        for b in balls:

            bx, by = b

            # check if ball is near line (cue -> target)
            dist = self._point_line_distance((bx, by), cue, target)

            if dist < 20:   # threshold
                penalty += 150

        return penalty

    # =========================
    # CORE FUNCTION
    # =========================
    def evaluate_shot(self, cue, target, pocket, balls):

        angle = self.angle_penalty(cue, target, pocket)
        distance = self.distance_penalty(cue, target)
        distance += self.distance_penalty(target, pocket, 0.5)
        blockers = self.blocker_penalty(cue, target, balls)

        score = angle + distance + blockers

        return score

    # =========================
    # UTILS
    # =========================
    def _point_line_distance(self, p, a, b):

        # line AB
        ax, ay = a
        bx, by = b
        px, py = p

        if a == b:
            return np.hypot(px - ax, py - ay)

        num = abs((by - ay)*px - (bx - ax)*py + bx*ay - by*ax)
        den = np.hypot(bx - ax, by - ay)

        return num / den