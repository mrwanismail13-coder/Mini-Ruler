# modules/physics_engine.py
import math
from typing import Tuple, List, Optional

class PhysicsEngine:
    def __init__(self, table_bounds: dict, cushion_elasticity: float):
        """
        table_bounds: {'top', 'left', 'width', 'height'} of the active play area.
        """
        self.bounds = table_bounds
        self.elasticity = cushion_elasticity

    def get_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def calculate_reflection_point(self, start: Tuple[float, float], pocket: Tuple[float, float], cushion_side: str, power_mode: dict) -> Tuple[float, float]:
        """
        Calculates the exact bounce point on a cushion using the Mirror Principle.
        Incorporates power compression to dynamically adjust the output angle.
        """
        x_start, y_start = start
        x_pock, y_pock = pocket
        
        # Determine the mirrored pocket position based on which cushion we hit
        if cushion_side == "top":
            mirrored_y = self.bounds["top"] - (y_pock - self.bounds["top"])
            mirrored_pock = (x_pock, mirrored_y)
        elif cushion_side == "bottom":
            mirrored_y = (self.bounds["top"] + self.bounds["height"]) + ((self.bounds["top"] + self.bounds["height"]) - y_pock)
            mirrored_pock = (x_pock, mirrored_y)
        elif cushion_side == "left":
            mirrored_x = self.bounds["left"] - (x_pock - self.bounds["left"])
            mirrored_pock = (mirrored_x, y_pock)
        elif cushion_side == "right":
            mirrored_x = (self.bounds["left"] + self.bounds["width"]) + ((self.bounds["left"] + self.bounds["width"]) - x_pock)
            mirrored_pock = (mirrored_x, y_pock)
        else:
            return (0, 0)

        # Intersection line between start point and mirrored pocket to find the bounce point on the cushion
        # Line equation: y - y1 = m(x - x1)
        if mirrored_pock[0] == x_start:  # Prevent division by zero
            return (x_start, self.bounds["top"] if cushion_side == "top" else y_pock)

        slope = (mirrored_pock[1] - y_start) / (mirrored_pock[0] - x_start)
        
        if cushion_side in ["top", "bottom"]:
            bounce_y = self.bounds["top"] if cushion_side == "top" else (self.bounds["top"] + self.bounds["height"])
            bounce_x = x_start + (bounce_y - y_start) / slope
            
            # Apply dynamic power correction (tightens the angle based on force/compression)
            compression_factor = power_mode.get("angle_compression", 1.0)
            mid_x = (x_start + x_pock) / 2
            bounce_x = mid_x + (bounce_x - mid_x) * compression_factor
            return (bounce_x, bounce_y)
            
        else:  # left or right
            bounce_x = self.bounds["left"] if cushion_side == "left" else (self.bounds["left"] + self.bounds["width"])
            bounce_y = y_start + slope * (bounce_x - x_start)
            return (bounce_x, bounce_y)

    def calculate_combo_shot(self, cue_ball: Tuple[float, float], target_ball: Tuple[float, float], ghost_ball: Tuple[float, float], pocket: Tuple[float, float], ball_radius: float) -> List[Tuple[float, float]]:
        """
        Recursive backwards calculation for Combination (Plant) shots.
        Calculates path from Pocket -> Ghost Ball -> Target Ball -> Cue Ball.
        """
        # Step 1: Calculate the line from pocket to the ghost_ball (the intermediate ball)
        dx_target = ghost_ball[0] - pocket[0]
        dy_target = ghost_ball[1] - pocket[1]
        dist_target = math.hypot(dx_target, dy_target)
        
        if dist_target == 0:
            return []

        # Position where target_ball needs to be hit by ghost_ball
        hit_pos_ghost_x = ghost_ball[0] + (dx_target / dist_target) * (ball_radius * 2)
        hit_pos_ghost_y = ghost_ball[1] + (dy_target / dist_target) * (ball_radius * 2)
        
        # Step 2: Now treat hit_pos_ghost as the target for the cue ball hitting the target ball
        dx_cue = target_ball[0] - hit_pos_ghost_x
        dy_cue = target_ball[1] - hit_pos_ghost_y
        dist_cue = math.hypot(dx_cue, dy_cue)
        
        if dist_cue == 0:
            return []

        hit_pos_cue_x = target_ball[0] + (dx_cue / dist_cue) * (ball_radius * 2)
        hit_pos_cue_y = target_ball[1] + (dy_cue / dist_cue) * (ball_radius * 2)

        # Return the sequence of points to draw the complete trajectory path
        return [cue_ball, (hit_pos_cue_x, hit_pos_cue_y), target_ball, (hit_pos_ghost_x, hit_pos_ghost_y), ghost_ball, pocket]
