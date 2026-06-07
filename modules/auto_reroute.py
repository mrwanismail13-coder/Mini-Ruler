import numpy as np
from typing import List, Tuple, Optional


class AutoReroute:
    def __init__(self, table_bounds: dict):
        self.bounds = table_bounds

    # =========================
    # CHECK IF PATH BLOCKED
    # =========================
    def is_blocked(self, blockers: List[Tuple[int, int]]) -> bool:
        return len(blockers) > 0

    # =========================
    # MIDPOINT STRATEGY (SAFE POINT)
    # =========================
    def get_mid_bounce_point(
        self,
        cue: Tuple[int, int],
        target: Tuple[int, int]
    ) -> Tuple[int, int]:

        mx = (cue[0] + target[0]) / 2
        my = (cue[1] + target[1]) / 2

        # slight upward bias for better angles
        my -= 40

        return int(mx), int(my)

    # =========================
    # CUSHION POINTS GENERATION
    # =========================
    def generate_cushion_points(self) -> List[Tuple[int, int]]:
        left = self.bounds["left"]
        top = self.bounds["top"]
        right = left + self.bounds["width"]
        bottom = top + self.bounds["height"]

        return [
            (left, top),
            (right, top),
            (left, bottom),
            (right, bottom)
        ]

    # =========================
    # SELECT BEST REROUTE PATH
    # =========================
    def find_best_route(
        self,
        cue: Tuple[int, int],
        target: Tuple[int, int],
        blockers: List[Tuple[int, int]]
    ) -> Tuple[List[Tuple[int, int]], str]:

        # 1) If no blockers → direct shot
        if not self.is_blocked(blockers):
            return [cue, target], "DIRECT"

        # 2) Try cushion bounce routes
        cushions = self.generate_cushion_points()

        best_path = None
        best_score = float("inf")

        for c in cushions:
            # cue → cushion → target
            path = [cue, c, target]

            score = (
                self.distance(cue, c) +
                self.distance(c, target)
            )

            # prefer shorter safer routes
            if score < best_score:
                best_score = score
                best_path = path

        # 3) fallback
        if best_path is None:
            mid = self.get_mid_bounce_point(cue, target)
            best_path = [cue, mid, target]

        return best_path, "REROUTE"

    # =========================
    # DISTANCE
    # =========================
    def distance(self, a, b) -> float:
        return np.hypot(a[0] - b[0], a[1] - b[1])