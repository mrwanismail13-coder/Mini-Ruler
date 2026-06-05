# config/settings.py
import cv2

# Screen and Table Calibration Defaults (Will be updated via calibration 'T')
TABLE_ROI = {
    "top": 200,
    "left": 300,
    "width": 1280,
    "height": 720
}

BALL_RADIUS = 12  # In pixels, depends on screen resolution

# Hotkey Definitions
HOTKEYS = {
    "CALIBRATE": "t",       # Auto / Manual calibration
    "TARGET_LOCK": "z",    # Locks closest ball to mouse
    "POCKET_1": "1",        # Top-Left Pocket
    "POCKET_2": "2",        # Top-Middle Pocket
    "POCKET_3": "3",        # Top-Right Pocket
    "POCKET_4": "4",        # Bottom-Left Pocket
    "POCKET_5": "5",        # Bottom-Middle Pocket
    "POCKET_6": "6",        # Bottom-Right Pocket
    "AUTO_BANK": "s",       # Smart bank shot calculation
    "COMBO_SHOT": "o",      # Combination/Plant shot calculation
}

# Advanced Physics Constants
CUSHION_ELASTICITY = 0.85  # Normal bounce factor
POWER_MODES = {
    "SOFT": {"elasticity": 0.88, "angle_compression": 1.0},
    "MEDIUM": {"elasticity": 0.85, "angle_compression": 0.98},
    "HARD": {"elasticity": 0.80, "angle_compression": 0.92}  # Hard shots compress cushion, tightening the angle
}
