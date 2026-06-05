# test_physics.py
import pytest
from modules.physics_engine import PhysicsEngine
from config.settings import TABLE_ROI, POWER_MODES

def test_physics_reflection():
    engine = PhysicsEngine(table_bounds=TABLE_ROI, cushion_elasticity=0.85)
    
    start_pos = (400, 300)
    target_pocket = (600, 200)  # On the top cushion border
    
    # Test top cushion bounce calculation
    bounce_point = engine.calculate_reflection_point(
        start=start_pos,
        pocket=target_pocket,
        cushion_side="top",
        power_mode=POWER_MODES["MEDIUM"]
    )
    
    assert bounce_point is not None
    assert bounce_point[1] == TABLE_ROI["top"]  # Y coordinate must sit perfectly on the cushion line
    print(f"Test Passed! Calculated bounce point at: {bounce_point}")

if __name__ == "__main__":
    test_physics_reflection()
