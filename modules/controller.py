# modules/controller.py
import mouse
import keyboard
from typing import Tuple, Optional

class InputController:
    def __init__(self):
        pass

    def get_mouse_position(self) -> Tuple[int, int]:
        """
        بتجيب إحداثيات الماوس الحالية على الشاشة بالملي
        """
        return mouse.get_position()

    def is_key_pressed(self, key: str) -> bool:
        """
        بتفحص لو الزرار مضغوط حالياً ولا لأ من غير ما تعمل بلوك للكود
        """
        return keyboard.is_pressed(key)

    def get_active_pocket_by_hotkey(self) -> Optional[int]:
        """
        بتشوف لو المستخدم داس على رقم من 1 لـ 6 عشان يختار الجيب يدوياً
        """
        for i in range(1, 7):
            if keyboard.is_pressed(str(i)):
                return i
        return None
