from cv2 import videoio_registry
import cv2
import mediapipe as mp
import pyautogui
import math
import time
import numpy as np

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
                self.draw.draw_landmarks(
                    img, hand, mp.solutions.hands.HAND_CONNECTIONS,
                    self.draw.DrawingSpec(color=(255, 255, 0), thickness=2, circle_radius=2),
                    self.draw.DrawingSpec(color=(255, 0, 255), thickness=2, circle_radius=2)
                )
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
# UI UTILS
# =========================
def draw_rounded_rect(img, pt1, pt2, color, thickness, r):
    x1, y1 = pt1
    x2, y2 = pt2
    r = min(r, abs(x2 - x1) // 2, abs(y2 - y1) // 2)
    if r <= 0:
        cv2.rectangle(img, pt1, pt2, color, thickness)
        return
        
    if thickness < 0:
        cv2.rectangle(img, (x1 + r, y1), (x2 - r, y2), color, -1)
        cv2.rectangle(img, (x1, y1 + r), (x2, y2 - r), color, -1)
        cv2.circle(img, (x1 + r, y1 + r), r, color, -1)
        cv2.circle(img, (x2 - r, y1 + r), r, color, -1)
        cv2.circle(img, (x1 + r, y2 - r), r, color, -1)
        cv2.circle(img, (x2 - r, y2 - r), r, color, -1)
    else:
        cv2.line(img, (x1 + r, y1), (x2 - r, y1), color, thickness)
        cv2.line(img, (x1 + r, y2), (x2 - r, y2), color, thickness)
        cv2.line(img, (x1, y1 + r), (x1, y2 - r), color, thickness)
        cv2.line(img, (x2, y1 + r), (x2, y2 - r), color, thickness)
        cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)
        cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)

# =========================
# BUTTON CLASS
# =========================
class Button:
    def __init__(self, pos, text, size, is_special=False):
        self.pos = pos
        self.size = size
        self.text = text
        self.is_special = is_special
        self.current_scale = 1.0
        self.target_scale = 1.0
        self.alpha = 0.5
        self.target_alpha = 0.5

    def update_animation(self):
        self.current_scale += (self.target_scale - self.current_scale) * 0.2
        self.alpha += (self.target_alpha - self.alpha) * 0.2

    def draw(self, img):
        self.update_animation()
        
        x, y = self.pos
        w, h = self.size
        
        scaled_w = int(w * self.current_scale)
        scaled_h = int(h * self.current_scale)
        
        offset_x = (scaled_w - w) // 2
        offset_y = (scaled_h - h) // 2
        
        px1, py1 = x - offset_x, y - offset_y
        px2, py2 = x + w + offset_x, y + h + offset_y

        overlay = img.copy()
        
        color = (40, 40, 40) if not self.is_special else (60, 60, 60)
        
        if self.target_scale > 1.0: 
            color = (255, 220, 0) # Cyan accent when hovered
            
        draw_rounded_rect(overlay, (px1, py1), (px2, py2), color, -1, 15)
        draw_rounded_rect(overlay, (px1, py1), (px2, py2), (255, 255, 255), 2, 15)

        cv2.addWeighted(overlay, self.alpha, img, 1 - self.alpha, 0, img)

        text_color = (255, 255, 255)
        if self.target_scale > 1.0:
            text_color = (0, 0, 0)
            
        font_scale = 0.8 * self.current_scale if len(self.text) > 1 else 1.2 * self.current_scale
        text_size = cv2.getTextSize(self.text, cv2.FONT_HERSHEY_DUPLEX, font_scale, 2)[0]
        text_x = px1 + (scaled_w - text_size[0]) // 2
        text_y = py1 + (scaled_h + text_size[1]) // 2
        
        cv2.putText(img, self.text, (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX, font_scale, text_color, 2)


# =========================
# KEYBOARD LAYOUT
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

    margin_x = int(w * 0.20)
    margin_y = int(h * 0.45)

    usable_w = w - 2 * margin_x
    usable_h = h - margin_y - int(h * 0.15)

    key_w = usable_w // max_cols
    key_h = usable_h // rows

    for i, row in enumerate(keys):
        row_width_total = 0
        row_keys_data = []
        
        for key in row:
            if key == "SPACE":
                w_ = key_w * 4
            elif key in ["BACK", "ENTER"]:
                w_ = int(key_w * 2.5)
            else:
                w_ = key_w
                
            row_keys_data.append((key, w_))
            row_width_total += w_
            
        start_x = (w - row_width_total) // 2
        current_x = start_x
        
        for key, w_ in row_keys_data:
            y = margin_y + i * key_h
            is_special = key in ["SPACE", "BACK", "ENTER"]
            size = [w_ - 15, key_h - 15]
            buttonList.append(Button([current_x + 7, y + 7], key, size, is_special))
            current_x += w_

    return buttonList

# =========================
# MAIN LOOP
# =========================
def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3, 1280)
    cap.set(4, 720)

    detector = HandDetector()

    buttons = None
    finalText = ""
    last_click = 0
    
    keyboard_expanded = True
    toggle_button = None

    cv2.namedWindow("Premium Virtual Keyboard", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Premium Virtual Keyboard", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        success, img = cap.read()
        if not success or img is None:
            continue

        img = cv2.flip(img, 1)
        h, w, _ = img.shape

        if buttons is None:
            buttons = createKeyboard(img.shape)
            toggle_button = Button([w // 2 - 100, h - 80], "TOGGLE UI", [200, 60], True)

        img = detector.findHands(img)
        lmList = detector.findPosition(img)

        # Draw Output Text Box (Sleek Glassmorphism)
        overlay = img.copy()
        draw_rounded_rect(overlay, (50, 30), (w - 50, 120), (20, 20, 20), -1, 20)
        draw_rounded_rect(overlay, (50, 30), (w - 50, 120), (255, 255, 255), 2, 20)
        cv2.addWeighted(overlay, 0.85, img, 0.15, 0, img)
        
        # Blinking cursor
        cursor = "|" if int(time.time() * 2) % 2 == 0 else ""
        display_text = finalText + cursor
        cv2.putText(img, display_text, (80, 90), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 3)

        x1, y1 = 0, 0
        x2, y2 = 0, 0
        click_length = 100
        
        if lmList:
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
            
            click_length = math.hypot(x2 - x1, y2 - y1)
            
            cv2.circle(img, (x1, y1), 8, (255, 200, 0), -1)
            cv2.circle(img, (x1, y1), 12, (255, 255, 255), 2)

        # Handle Toggle Button
        tx, ty = toggle_button.pos
        tw, th = toggle_button.size
        
        if tx < x1 < tx + tw and ty < y1 < ty + th:
            toggle_button.target_scale = 1.1
            toggle_button.target_alpha = 0.95
            if click_length < 40 and time.time() - last_click > 0.5:
                keyboard_expanded = not keyboard_expanded
                last_click = time.time()
                draw_rounded_rect(img, (tx, ty), (tx + tw, ty + th), (255, 255, 255), -1, 15)
        else:
            toggle_button.target_scale = 1.0
            toggle_button.target_alpha = 0.7
            
        toggle_button.draw(img)

        if keyboard_expanded:
            for b in buttons:
                x, y = b.pos
                w_, h_ = b.size

                if x < x1 < x + w_ and y < y1 < y + h_:
                    b.target_scale = 1.15 
                    b.target_alpha = 0.95
                    
                    if click_length < 40 and time.time() - last_click > 0.8:
                        draw_rounded_rect(img, (x, y), (x + w_, y + h_), (0, 255, 0), -1, 15)
                        
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
                else:
                    b.target_scale = 1.0
                    b.target_alpha = 0.6

                b.draw(img)

        cv2.imshow("Premium Virtual Keyboard", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
