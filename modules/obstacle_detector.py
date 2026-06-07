import numpy as np
from typing import List, Tuple


class ObstacleDetector:
    def __init__(self, min_clearance: float = 18.0):
        """
        min_clearance:
        أقل مسافة بين الكورة وخط الضربة عشان تعتبر عائق
        """
        self.min_clearance = min_clearance

    # =========================
    # DISTANCE FROM POINT TO LINE
    # =========================
    def point_line_distance(self, p, a, b) -> float:
        """
        حساب المسافة العمودية من نقطة إلى خط (a -> b)
        """
        p = np.array(p, dtype=float)
        a = np.array(a, dtype=float)
        b = np.array(b, dtype=float)

        if np.all(a == b):
            return np.linalg.norm(p - a)

        return np.abs(np.cross(b - a, a - p)) / np.linalg.norm(b - a)

    # =========================
    # FIND BLOCKERS
    # =========================
    def find_blocking_balls(
        self,
        cue: Tuple[int, int],
        target: Tuple[int, int],
        object_balls: List[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        """
        يرجع الكور اللي واقفة في خط الضربة
        """
        blockers = []

        for ball in object_balls:
            x, y = ball[0], ball[1]

            dist = self.point_line_distance((x, y), cue, target)

            if dist < self.min_clearance:
                blockers.append(ball)

        return blockers

    # =========================
    # CLEAR SHOT CHECK
    # =========================
    def is_clear_shot(
        self,
        cue: Tuple[int, int],
        target: Tuple[int, int],
        object_balls: List[Tuple[int, int]]
    ) -> bool:

        return len(self.find_blocking_balls(cue, target, object_balls)) == 0