import cv2
import mediapipe as mp
import pyautogui
import math
import time

# =========================
# HAND DETECTOR
# =========================
class HandDetector:
    def __init__(self):
        self.hands = mp.solutions.hands.Hands(min_detection_confidence=0.7)
        self.draw = mp.solutions.drawing_utils

    def findHands(self, img):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)
        if self.results.multi_hand_landmarks:
            for hand in self.results.multi_hand_landmarks:
                self.draw.draw_landmarks(img, hand, mp.solutions.hands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img):
        lmList = []
        if self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[0]
            h, w, _ = img.shape
            for id, lm in enumerate(hand.landmark):
                lmList.append((id, int(lm.x*w), int(lm.y*h)))
        return lmList


# =========================
# BUTTON CLASS
# =========================
class Button:
    def __init__(self, pos, text, size):
        self.pos = pos
        self.size = size
        self.text = text


# =========================
# AUTO-SCALING KEYBOARD
# =========================
def createKeyboard(img_shape):
    h, w, _ = img_shape

    keys = [
        ["1","2","3","4","5","6","7","8","9","0"],
        ["Q","W","E","R","T","Y","U","I","O","P"],
        ["A","S","D","F","G","H","J","K","L"],
        ["Z","X","C","V","B","N","M"],
        ["SPACE","BACK","ENTER"]
    ]

    buttonList = []
    rows = len(keys)
    max_cols = max(len(row) for row in keys)

    margin_x = int(w * 0.05)
    margin_y = int(h * 0.08)

    usable_w = w - 2 * margin_x
    usable_h = h - 2 * margin_y

    key_w = usable_w // max_cols
    key_h = usable_h // (rows + 1)

    for i, row in enumerate(keys):
        row_width = len(row) * key_w
        start_x = (w - row_width) // 2

        for j, key in enumerate(row):
            x = start_x + j * key_w
            y = margin_y + i * key_h

            if key == "SPACE":
                size = [key_w * 3, key_h]
            elif key == "BACK":
                size = [key_w * 2, key_h]
            elif key == "ENTER":
                size = [key_w * 2, key_h]
            else:
                size = [key_w - 10, key_h - 10]

            buttonList.append(Button([x, y], key, size))

    return buttonList


# =========================
# DRAW TRANSPARENT TEXT UI
# =========================
def drawUI(img, buttonList):
    for b in buttonList:
        x, y = b.pos
        w, h = b.size

        cv2.putText(img, b.text,
                    (x + 10, y + int(h * 0.7)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9, (255, 255, 255), 2)

    return img


# =========================
# MAIN
# =========================
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Optional: set resolution (better performance)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector()

buttons = None
finalText = ""
last_click = 0

# Full screen mode
cv2.namedWindow("Virtual Keyboard", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Virtual Keyboard", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    success, img = cap.read()
    if not success or img is None:
        continue

    img = cv2.flip(img, 1)

    # Create keyboard once
    if buttons is None:
        buttons = createKeyboard(img.shape)

    img = detector.findHands(img)
    lmList = detector.findPosition(img)

    img = drawUI(img, buttons)

    if lmList:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # Cursor dot
        cv2.circle(img, (x1, y1), 6, (255, 255, 255), -1)

        for b in buttons:
            x, y = b.pos
            w, h = b.size

            if x < x1 < x+w and y < y1 < y+h:

                # Hover (yellow glow)
                cv2.putText(img, b.text,
                            (x + 10, y + int(h * 0.7)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 255), 3)

                length = math.hypot(x2-x1, y2-y1)

                if length < 30 and time.time() - last_click > 0.4:

                    # Click (green)
                    cv2.putText(img, b.text,
                                (x + 10, y + int(h * 0.7)),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1.1, (0, 255, 0), 3)

                    if b.text == "SPACE":
                        finalText += " "
                        pyautogui.press("space")

                    elif b.text == "BACK":
                        finalText = finalText[:-1]
                        pyautogui.press("backspace")

                    elif b.text == "ENTER":
                        finalText += "\n"
                        pyautogui.press("enter")

                    else:
                        finalText += b.text
                        pyautogui.press(b.text.lower())
                    last_click = time.time()

    # Output text
    h, w, _ = img.shape
    cv2.putText(img, finalText, (50, h - 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

    cv2.imshow("Virtual Keyboard", img)
memoryview
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
