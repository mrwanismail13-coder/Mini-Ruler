# config/settings.py

# الإحداثيات العالمية الموسعة والشاملة للطاولة كاملة من الحافة للحافة لشاشة 1920x1080
TABLE_ROI = {
    "top": 200,         # رفعنا الكادر لفوق عشان نجيب الحواف كاملة
    "left": 130,        # رجعنا الكادر للشمال عشان الجيوب الشمال تبان كاملة
    "width": 1660,      # وسعنا العرض الكلي ليغطي الجيوب اليمنى بالكامل
    "height": 710       # زودنا الارتفاع الكلي ليغطي الجيوب السفلية كاملة
}

BALL_RADIUS = 15  # نصف القطر الظاهري المثالي للكور جوة المحاكي

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
