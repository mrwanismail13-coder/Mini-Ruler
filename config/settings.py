# config/settings.py

# الأبعاد السحرية المظبوطة باليد - كادر الكشف الشامل لـ YOLO11
TABLE_ROI = {
    "top": 246,         # بداية الطاولة من فوق
    "left": 314,        # بداية الطاولة من الشمال
    "width": 1291,      # العرض الخارجي الصافي شامل الجيوب اليمين
    "height": 710       # الارتفاع الخارجي الصافي شامل الجيوب التحتانية
}

# الحدود الهندسية الصافية لارتداد الكور (منطقة القماش الأزرق الداخلي بالظبط)
# تم ضبطها لتكون متناسقة تماماً ومحاذية لأول نقطة ارتداد جوة الـ ROI الجديدة
PLAYABLE_CUSHIONS = {
    "top": 296,         # الـ top الخارجي + سمك البند الفوقاني
    "bottom": 906,      # الـ top + الـ height الكلي - سمك البند التحتاني
    "left": 364,        # الـ left الخارجي + سمك البند الشمال
    "right": 1555       # الـ left + الـ width الكلي - سمك البند اليمين
}

BALL_RADIUS = 15  # نصف قطر الكورة الثابت

# Hotkeys المتفق عليها
HOTKEYS = {
    "CALIBRATE": "t",       
    "TARGET_LOCK": "z",    
    "POCKET_1": "1", "POCKET_2": "2", "POCKET_3": "3",        
    "POCKET_4": "4", "POCKET_5": "5", "POCKET_6": "6",        
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
