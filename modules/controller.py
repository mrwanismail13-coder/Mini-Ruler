# modules/controller.py
from typing import Tuple, Optional
import platform

# فحص نظام التشغيل فوراً من نواة السيستم
# لو شغالين على Linux (زي سيرفرات GitHub Actions) بنقفل الـ Imports تماماً لمنع الكراش الداخلي للمكتبات
CURRENT_OS = platform.system().lower()
IS_LINUX_SERVER = (CURRENT_OS == "linux")

if not IS_LINUX_SERVER:
    import mouse
    import keyboard
else:
    print("[INFO] Headless Linux detected. Bypassing Windows input libraries entirely.")

class InputController:
    def __init__(self):
        pass

    def get_mouse_position(self) -> Tuple[int, int]:
        """
        بتجيب إحداثيات الماوس الحالية. لو في الـ Cloud بترجع إحداثيات وهمية للتست.
        """
        if IS_LINUX_SERVER:
            return (620, 430)  # نقطة افتراضية قريبة من الكورة في صورة التست
        return mouse.get_position()

    def is_key_pressed(self, key: str) -> bool:
        """
        بتفحص لو الزرار مضغوط. في الـ Cloud بنخليها تطلع True دايماً عشان نشغل كل حسابات الفيزكس والتستات تلقائياً.
        """
        if IS_LINUX_SERVER:
            return True
        return keyboard.is_pressed(key)

    def get_active_pocket_by_hotkey(self) -> Optional[int]:
        """
        بتجيب رقم الجيب المختار. في الـ Cloud بترجع أول جيب دايماً.
        """
        if IS_LINUX_SERVER:
            return 1
            
        for i in range(1, 7):
            if keyboard.is_pressed(str(i)):
                return i
        return None
