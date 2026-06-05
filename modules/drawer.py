# modules/drawer.py
import cv2
import numpy as np
from typing import List, Tuple, Dict

class ScreenDrawer:
    def __init__(self):
        # تعريف الألوان الاحترافية لخطوط الشيتو (BGR Format)
        self.colors = {
            "cue_line": (255, 255, 255),    # خط أبيض ناصع للكيو
            "target_line": (0, 255, 0),     # خط أخضر للكورة المستهدفة
            "bounce_line": (0, 255, 255),   # خط أصفر للبناد والمرتدات
            "combo_line": (255, 0, 255),    # خط فوشيا (Pink) للـ Combo Shots
            "pocket_match": (0, 0, 255),    # دايرة حمراء على الجيب المستهدف
            "ghost_ball": (200, 200, 200)   # كورة وهمية رمادي فاتح بتبين نقطة التصادم
        }

    def draw_trajectory(self, frame: np.ndarray, points: List[Tuple[int, int]], line_type: str = "cue_line", thickness: int = 2) -> np.ndarray:
        """
        بترسم مسار متحرك كامل بين مجموعة نقط متتالية (مثلاً من الكيو للكورة للبند للجيب)
        """
        if len(points) < 2:
            return frame

        color = self.colors.get(line_type, (255, 255, 255))
        
        # رسم الخطوط بين النقط
        for i in range(len(points) - 1):
            p1 = (int(points[i][0]), int(points[i][1]))
            p2 = (int(points[i+1][0]), int(points[i+1][1]))
            cv2.line(frame, p1, p2, color, thickness, cv2.LINE_AA) # LINE_AA عشان الخطوط تطلع ناعمة ومفيهاش زجزاج
            
        return frame

    def draw_ghost_ball(self, frame: np.ndarray, position: Tuple[int, int], radius: int = 12) -> np.ndarray:
        """
        ترسم الكورة الوهمية (Ghost Ball) في مكان التصادم بالملي عشان توريك زاوية الضرب الصح
        """
        pos = (int(position[0]), int(position[1]))
        color = self.colors["ghost_ball"]
        # رسم حدود الكورة الوهمية خط منقط أو خفيف
        cv2.circle(frame, pos, radius, color, 1, cv2.LINE_AA)
        # نقطة صغيرة في المركز للـ Precision
        cv2.circle(frame, pos, 2, color, -1)
        return frame

    def draw_detected_table(self, frame: np.ndarray, detections: Dict) -> np.ndarray:
        """
        ترسم خطوط توضيحية خفيفة حوالين كل الكور والجيوب المكتشفة زي الهكر الأصلي
        """
        # رسم الكور المكتشفة
        for ball in detections.get("object_balls", []):
            pos = (int(ball[0]), int(ball[1]))
            cv2.circle(frame, pos, 12, (0, 255, 0), 1, cv2.LINE_AA)
            
        # الكورة البيضا
        if detections.get("cue_ball"):
            cb = detections["cue_ball"][0]
            cv2.circle(frame, (int(cb[0]), int(cb[1])), 12, (255, 255, 255), 2, cv2.LINE_AA)
            
        # الجيوب (Pockets)
        for pocket in detections.get("pockets", []):
            pos = (int(pocket[0]), int(pocket[1]))
            cv2.circle(frame, pos, 15, (255, 0, 0), 1, cv2.LINE_AA)
            
        return frame

    def create_transparent_overlay(self, width: int, height: int) -> np.ndarray:
        """
        بتعمل كادر شفاف بالكامل (BGRA) عشان يترسم فوق اللعبة اللايف في الويندوز
        """
        overlay = np.zeros((height, width, 4), dtype=np.uint8)
        return overlay
