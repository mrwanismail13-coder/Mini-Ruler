import math
from typing import Tuple, List, Optional


class PhysicsEngine:
    def __init__(self, table_bounds: dict, cushion_elasticity: float = 0.85):
        """
        table_bounds:
        {
            "top": int,
            "left": int,
            "width": int,
            "height": int
        }
        """
        self.bounds = table_bounds
        self.elasticity = cushion_elasticity

    # =========================
    # BASIC DISTANCE
    # =========================
    def get_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    # =========================
    # REFLECTION (BANK SHOT CORE)
    # =========================
    def calculate_reflection_point(
        self,
        start: Tuple[float, float],
        pocket: Tuple[float, float],
        cushion_side: str,
        power_mode: dict
    ) -> Tuple[float, float]:

        x1, y1 = start
        x2, y2 = pocket

        # منع القسمة على صفر
        dx = (x2 - x1)
        dy = (y2 - y1)

        if dx == 0:
            dx = 1e-6

        slope = dy / dx

        # حدود الطاولة
        left = self.bounds["left"]
        top = self.bounds["top"]
        right = left + self.bounds["width"]
        bottom = top + self.bounds["height"]

        bounce_x, bounce_y = x1, y1

        # =========================
        # TOP CUSHION
        # =========================
        if cushion_side == "top":
            bounce_y = top
            bounce_x = x1 + (bounce_y - y1) / slope

        # =========================
        # BOTTOM CUSHION
        # =========================
        elif cushion_side == "bottom":
            bounce_y = bottom
            bounce_x = x1 + (bounce_y - y1) / slope

        # =========================
        # LEFT CUSHION
        # =========================
        elif cushion_side == "left":
            bounce_x = left
            bounce_y = y1 + slope * (bounce_x - x1)

        # =========================
        # RIGHT CUSHION
        # =========================
        elif cushion_side == "right":
            bounce_x = right
            bounce_y = y1 + slope * (bounce_x - x1)

        else:
            return (0.0, 0.0)

        # =========================
        # CLAMP (IMPORTANT FOR CI + REAL WORLD)
        # =========================
        bounce_x = max(left, min(right, bounce_x))
        bounce_y = max(top, min(bottom, bounce_y))

        # =========================
        # POWER MODULATION
        # =========================
        compression = power_mode.get("angle_compression", 1.0)

        mid_x = (x1 + x2) / 2
        bounce_x = mid_x + (bounce_x - mid_x) * compression

        return (float(bounce_x), float(bounce_y))

    # =========================
    # COMBO SHOTS (PLANT SYSTEM)
    # =========================
    def calculate_combo_shot(
        self,
        cue_ball: Tuple[float, float],
        target_ball: Tuple[float, float],
        ghost_ball: Tuple[float, float],
        pocket: Tuple[float, float],
        ball_radius: float
    ) -> List[Tuple[float, float]]:

        dx = ghost_ball[0] - pocket[0]
        dy = ghost_ball[1] - pocket[1]

        dist = math.hypot(dx, dy)
        if dist == 0:
            return []

        # ghost impact point
        ghost_hit_x = ghost_ball[0] + (dx / dist) * (ball_radius * 2)
        ghost_hit_y = ghost_ball[1] + (dy / dist) * (ball_radius * 2)

        dx2 = target_ball[0] - ghost_hit_x
        dy2 = target_ball[1] - ghost_hit_y

        dist2 = math.hypot(dx2, dy2)
        if dist2 == 0:
            return []

        cue_hit_x = target_ball[0] + (dx2 / dist2) * (ball_radius * 2)
        cue_hit_y = target_ball[1] + (dy2 / dist2) * (ball_radius * 2)

        return [
            cue_ball,
            (cue_hit_x, cue_hit_y),
            target_ball,
            (ghost_hit_x, ghost_hit_y),
            ghost_ball,
            pocket
        ]

    # =========================
    # SAFE CHECKS
    # =========================
    def is_valid_point(self, p: Tuple[float, float]) -> bool:
        left = self.bounds["left"]
        top = self.bounds["top"]
        right = left + self.bounds["width"]
        bottom = top + self.bounds["height"]

        return left <= p[0] <= right and top <= p[1] <= bottom
