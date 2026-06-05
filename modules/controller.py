# modules/controller.py
from typing import Tuple, Optional
import sys

# فحص ذكي: لو شغالين على سيرفر Linux (زي الـ GitHub Actions) بنعمل Mock للمكتبات عشان نمنع الـ ModuleNotFoundError
try:
    import mouse
    import keyboard
    IS_LINUX_SERVER = False
except ImportError:
    IS_LINUX_SERVER = True

class InputController:
    def __init__(self):
        if IS_LINUX_SERVER:
            print("[INFO] Running in a headless/server environment. Input simulation is mocked.")

    def get_mouse_position(self) -> Tuple[int, int]:
        """
        بتجيب إحداثيات الماوس الحالية على الشاشة بالملي
        """
        if IS_LINUX_SERVER:
            return (620, 430)  # إحداثيات وهمية ثابتة لبيئة التيست في الـ Cloud
        return mouse.get_position()

    def is_key_pressed(self, key: str) -> bool:
        """
        بتفحص لو الزرار مضغوط حالياً ولا لأ من غير ما تعمل بلوك للكود
        """
        if IS_LINUX_SERVER:
            return True  # بنخليها True في التيست عشان نشغل كل حسابات الفيزكس أوتوماتيك
        return keyboard.is_pressed(key)

    def get_active_pocket_by_hotkey(self) -> Optional[int]:
        """
        بتشوف لو المستخدم داس على رقم من 1 لـ 6 عشان يختار الجيب يدوياً
        """
        if IS_LINUX_SERVER:
            return 1  # الجيب الأول الافتراضي للتست
            
        for i in range(1, 7):
            if keyboard.is_pressed(str(i)):
                return i
        return None
