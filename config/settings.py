# config/settings.py

# كادر الكشف الشامل لـ YOLO11 (يشمل الجيوب والحواف كاملة)
TABLE_ROI = {
    "top": 200,
    "left": 130,
    "width": 1660,
    "height": 710
}

# الإحداثيات الصافية لحدود القماش الأزرق الداخلي بالظبط لمنع خروج خطوط البند
PLAYABLE_CUSHIONS = {
    "top": 236,
    "bottom": 824,
    "left": 172,
    "right": 1748
}

BALL_RADIUS = 15  # نصف القطر الظاهري المظبوط للكور

# Hotkey Definitions
HOTKEYS = {
    "CALIBRATE": "t",       
    "TARGET_LOCK": "z",    
    "POCKET_1": "1",        
    "POCKET_2": "2",        
    "POCKET_3": "3",        
    "POCKET_4": "4",        
    "POCKET_5": "5",        
    "POCKET_6": "6",        
    "AUTO_BANK": "s",       
    "COMBO_SHOT": "o",      
}

# Advanced Physics Constants
CUSHION_ELASTICITY = 0.85
POWER_MODES = {
    "SOFT": {"elasticity": 0.88, "angle_compression": 1.0},
    "MEDIUM": {"elasticity": 0.85, "angle_compression": 0.98},
    "HARD": {"elasticity": 0.80, "angle_compression": 0.92}
}
