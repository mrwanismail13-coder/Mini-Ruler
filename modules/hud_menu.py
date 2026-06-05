import cv2


class HUDMenu:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def draw(self, frame):
        x, y = 20, 20

        panel = [
            "8BP AI SYSTEM",
            "-------------------",
            "Z  -> Lock Target",
            "1-6 -> Select Pocket",
            "T  -> Calibrate Table",
            "S  -> Bank Mode",
            "O  -> Combo Mode",
            "ESC -> Exit"
        ]

        # background
        cv2.rectangle(frame, (10, 10), (300, 220), (0, 0, 0), -1)

        for i, text in enumerate(panel):
            cv2.putText(
                frame,
                text,
                (x, y + i * 25),
                self.font,
                0.6,
                (255, 255, 255),
                1
            )

        return frame
