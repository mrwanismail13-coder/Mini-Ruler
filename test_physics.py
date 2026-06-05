import pytest
from modules.physics_engine import PhysicsEngine
from config.settings import TABLE_ROI, POWER_MODES


def test_top_cushion_reflection_validity():
    engine = PhysicsEngine(
        table_bounds=TABLE_ROI,
        cushion_elasticity=0.85
    )

    start_pos = (400, 300)
    target_pocket = (600, 200)

    bounce_point = engine.calculate_reflection_point(
        start=start_pos,
        pocket=target_pocket,
        cushion_side="top",
        power_mode=POWER_MODES["MEDIUM"]
    )

    # 1- لازم تكون موجودة
    assert bounce_point is not None

    x, y = bounce_point

    # 2- لازم تكون على حدود الطاولة (مش شرط تساوي exact)
    assert TABLE_ROI["top"] - 5 <= y <= TABLE_ROI["top"] + 5

    # 3- لازم تكون داخل العرض الطبيعي للطاولة
    assert TABLE_ROI["left"] <= x <= TABLE_ROI["left"] + TABLE_ROI["width"]

    print(f"[OK] Bounce point validated: {bounce_point}")


def test_reflection_stability_multiple_runs():
    engine = PhysicsEngine(TABLE_ROI, 0.85)

    results = []

    for _ in range(10):
        p = engine.calculate_reflection_point(
            start=(400, 300),
            pocket=(600, 200),
            cushion_side="top",
            power_mode=POWER_MODES["MEDIUM"]
        )
        results.append(p)

    # لازم النتائج تكون مستقرة (deterministic)
    assert all(r == results[0] for r in results)

    print("[OK] Physics is deterministic")


if __name__ == "__main__":
    test_top_cushion_reflection_validity()
    test_reflection_stability_multiple_runs()
