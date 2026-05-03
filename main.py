import cv2
import mediapipe as mp
import pyautogui
import math
import time

# =========================
# HAND DETECTOR CLASS
# =========================
class HandDetector:
    def __init__(self, detectionCon=0.7, maxHands=1):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            min_detection_confidence=detectionCon,
            max_num_hands=maxHands
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img):
        lmList = []
        if self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[0]
            h, w, _ = img.shape
            for id, lm in enumerate(hand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((id, cx, cy))
        return lmList


# =========================
# BUTTON CLASS
# =========================
class Button:
    def __init__(self, pos, text, size=[60, 60]):
        self.pos = pos
        self.size = size
        self.text = text


# =========================
# DRAW KEYBOARD
# =========================
def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size

        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, button.text, (x + 15, y + 40),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    return img


# =========================
# KEYBOARD LAYOUT
# =========================
keys = [
    ["Q","8","E","R","T","Y","U","I","O","P"],
    ["A","S","D","F","G","H","J","K","L"],
    ["Z","X","C","V","B","N","M"]
]

buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([100 * j + 50, 100 * i + 50], key))


# =========================
# MAIN
# =========================
cap = cv2.VideoCapture(0)
detector = HandDetector()

finalText = ""
last_click_time = 0

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    img = detector.findHands(img)
    lmList = detector.findPosition(img)

    img = drawAll(img, buttonList)

    if lmList:
        x1, y1 = lmList[8][1], lmList[8][2]   # Index finger
        x2, y2 = lmList[12][1], lmList[12][2] # Middle finger

        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            # Hover detection
            if x < x1 < x + w and y < y1 < y + h:
                cv2.rectangle(img, (x, y), (x + w, y + h),
                              (0, 255, 0), cv2.FILLED)
                cv2.putText(img, button.text, (x + 15, y + 40),
                            cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

                # Distance between fingers
                length = math.hypot(x2 - x1, y2 - y1)

                # Click condition
                if length < 30:
                    current_time = time.time()

                    # Debounce (avoid multiple clicks)
                    if current_time - last_click_time > 0.5:
                        finalText += button.text
                        pyautogui.press(button.text.lower())
                        last_click_time = current_time

                        cv2.rectangle(img, (x, y), (x + w, y + h),
                                      (0, 0, 255), cv2.FILLED)

    # Display typed text
    cv2.rectangle(img, (50, 350), (1000, 450), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, finalText, (60, 420),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

    cv2.imshow("Virtual Keyboad", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()