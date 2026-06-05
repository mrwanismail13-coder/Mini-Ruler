# config/settings.py

# الإحداثيات العالمية الدقيقة لساحة اللعب كاملة (الست جيوب جوة الكادر) لشاشة 1920x1080
TABLE_ROI = {
    "top": 222,        # بداية الحافة العلوية للطاولة
    "left": 155,       # بداية الحافة اليسرى للطاولة
    "width": 1610,     # العرض الكامل الشامل للجيوب اليمين
    "height": 660      # الارتفاع الكامل الشامل للجيوب التحتانية
}

BALL_RADIUS = 15  # نصف القطر الظاهري المظبوط للكور في المحاكي

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
