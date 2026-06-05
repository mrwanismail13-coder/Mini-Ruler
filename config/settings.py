# config/settings.py

# تصحيح إحداثيات الطاولة الزرقاء (منطقة اللعب الحقيقية فقط بدون الهوامش السوداء) بناءً على كادر الشاشة الكاملة
TABLE_ROI = {
    "top": 222,
    "left": 164,
    "width": 1592,
    "height": 636
}

BALL_RADIUS = 15  # تعديل نصف القطر ليتناسب مع الحجم الظاهري للكور في الصورة

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
