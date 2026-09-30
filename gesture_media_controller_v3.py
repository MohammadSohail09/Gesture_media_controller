"""
Hand Gesture Media Controller (v3 - Splash Screen + Pinch Volume)
--------------------------------------------------------------------
New in this version:
  - Startup splash screen (professional intro before webcam starts)
  - Pinch gesture (thumb + index finger) -> smooth, continuous volume
    control, with an on-screen volume bar that moves live as you
    pinch closer/farther apart

Other gestures (unchanged):
  Open Palm  -> Play
  Fist       -> Pause
  Index Up   -> Next Track
  Peace Sign -> Previous Track
  Pinch      -> Continuous Volume Control (replaces thumbs up/down)

Libraries used: OpenCV, MediaPipe, pyautogui
"""

import cv2
import mediapipe as mp
import pyautogui
import time
import math
import numpy as np
from collections import deque, Counter

# ---------------------------------------------------------
# Setup: MediaPipe Hands
# ---------------------------------------------------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)

TIP_IDS = [4, 8, 12, 16, 20]
PIP_IDS = [3, 6, 10, 14, 18]

GESTURE_INFO = {
    "OPEN_PALM":  ("Open Palm", (80, 220, 100), "playpause", "Play"),
    "FIST":       ("Fist", (60, 60, 220), "playpause", "Pause"),
    "INDEX_ONLY": ("Index Up", (230, 180, 60), "nexttrack", "Next Track"),
    "PEACE":      ("Peace Sign", (230, 140, 230), "prevtrack", "Previous Track"),
    "PINCH":      ("Pinch (Volume)", (60, 200, 230), None, "Adjusting Volume"),
    "NONE":       ("No Gesture", (120, 120, 120), None, "-"),
}


# ---------------------------------------------------------
# Fingers up detection
# ---------------------------------------------------------
def fingers_up(landmarks, handedness_label):
    fingers = []
    if handedness_label == "Right":
        fingers.append(1 if landmarks[TIP_IDS[0]].x < landmarks[PIP_IDS[0]].x else 0)
    else:
        fingers.append(1 if landmarks[TIP_IDS[0]].x > landmarks[PIP_IDS[0]].x else 0)

    for i in range(1, 5):
        fingers.append(1 if landmarks[TIP_IDS[i]].y < landmarks[PIP_IDS[i]].y else 0)
    return fingers


def classify_gesture(fingers):
    total_up = sum(fingers)

    if total_up == 0:
        return "FIST"
    elif total_up == 5:
        return "OPEN_PALM"
    elif fingers == [0, 1, 0, 0, 0]:
        return "INDEX_ONLY"
    elif fingers == [0, 1, 1, 0, 0]:
        return "PEACE"
    elif fingers == [1, 1, 0, 0, 0]:
        return "PINCH"   # thumb + index extended, rest curled -> pinch mode
    else:
        return "NONE"


# ---------------------------------------------------------
# UI helpers
# ---------------------------------------------------------
def draw_panel(frame, x, y, w, h, alpha=0.55, color=(20, 20, 20)):
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def draw_cooldown_bar(frame, x, y, w, h, progress, color):
    cv2.rectangle(frame, (x, y), (x + w, y + h), (70, 70, 70), -1)
    filled_w = int(w * progress)
    if filled_w > 0:
        cv2.rectangle(frame, (x, y), (x + filled_w, y + h), color, -1)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (150, 150, 150), 1)


def draw_volume_bar(frame, volume_percent):
    """Vertical volume bar on the right side of the screen."""
    h, w, _ = frame.shape
    bar_x, bar_y, bar_w, bar_h = w - 80, 120, 35, 300

    draw_panel(frame, bar_x - 15, bar_y - 40, bar_w + 30, bar_h + 80, alpha=0.5)

    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (80, 80, 80), 2)

    fill_h = int((volume_percent / 100) * bar_h)
    top_y = bar_y + bar_h - fill_h
    color = (60, 220, 130) if volume_percent > 15 else (60, 60, 220)
    cv2.rectangle(frame, (bar_x, top_y), (bar_x + bar_w, bar_y + bar_h), color, -1)

    cv2.putText(frame, f"{int(volume_percent)}%", (bar_x - 8, bar_y + bar_h + 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "VOL", (bar_x, bar_y - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)


# ---------------------------------------------------------
# Splash screen
# ---------------------------------------------------------
def show_splash_screen():
    width, height = 900, 550
    splash = np.zeros((height, width, 3), dtype=np.uint8)
    splash[:] = (35, 25, 20)   # dark background (BGR)

    # Decorative gradient bar
    for i in range(width):
        color_val = int(255 * (i / width))
        splash[0:8, i] = (color_val, 100, 255 - color_val)

    cv2.putText(splash, "HAND GESTURE", (180, 180),
                cv2.FONT_HERSHEY_DUPLEX, 2.0, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(splash, "MEDIA CONTROLLER", (130, 240),
                cv2.FONT_HERSHEY_DUPLEX, 2.0, (100, 220, 255), 3, cv2.LINE_AA)

    cv2.putText(splash, "Built with OpenCV + MediaPipe", (250, 300),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 180, 180), 1, cv2.LINE_AA)

    instructions = [
        "Open Palm  ->  Play",
        "Fist       ->  Pause",
        "Index Up   ->  Next Track",
        "Peace Sign ->  Previous Track",
        "Pinch (Thumb+Index) -> Volume Control",
    ]
    y = 360
    for line in instructions:
        cv2.putText(splash, line, (260, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1, cv2.LINE_AA)
        y += 32

    cv2.putText(splash, "Press any key to start...", (280, 520),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (150, 255, 150), 2, cv2.LINE_AA)

    cv2.imshow("Hand Gesture Media Controller", splash)
    cv2.waitKey(0)


# ---------------------------------------------------------
# Main loop
# ---------------------------------------------------------
def main():
    show_splash_screen()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    BUFFER_SIZE = 8
    STABILITY_THRESHOLD = 6
    gesture_buffer = deque(maxlen=BUFFER_SIZE)

    confirmed_gesture = "NONE"
    last_triggered_gesture = "NONE"
    last_action_time = 0
    cooldown = 1.0
    last_action_label = "-"

    # Pinch/volume state
    volume_percent = 50.0          # just an on-screen representation, starts at 50
    last_pinch_dist = None
    PINCH_MIN = 0.02               # normalized distance when fingers touching
    PINCH_MAX = 0.25               # normalized distance when fingers fully apart
    last_volume_key_time = 0
    VOLUME_KEY_COOLDOWN = 0.08     # small delay between key presses for smoothness

    prev_time = time.time()
    fps = 0

    while True:
        success, frame = cap.read()
        if not success:
            print("Camera not accessible.")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        raw_gesture = "NONE"
        pinch_point_a = pinch_point_b = None

        if result.multi_hand_landmarks and result.multi_handedness:
            hand_landmarks = result.multi_hand_landmarks[0]
            handedness_label = result.multi_handedness[0].classification[0].label

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_styles.get_default_hand_landmarks_style(),
                mp_styles.get_default_hand_connections_style()
            )

            landmarks = hand_landmarks.landmark
            fingers = fingers_up(landmarks, handedness_label)
            raw_gesture = classify_gesture(fingers)

            if raw_gesture == "PINCH":
                thumb_tip = landmarks[4]
                index_tip = landmarks[8]
                dist = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)

                h, w, _ = frame.shape
                pinch_point_a = (int(thumb_tip.x * w), int(thumb_tip.y * h))
                pinch_point_b = (int(index_tip.x * w), int(index_tip.y * h))

                # Map distance directly to a volume percentage (absolute, smooth)
                clamped = max(PINCH_MIN, min(PINCH_MAX, dist))
                volume_percent = ((clamped - PINCH_MIN) / (PINCH_MAX - PINCH_MIN)) * 100

                # Push actual system volume toward target using key presses,
                # rate-limited so it feels smooth instead of spammy
                now = time.time()
                if last_pinch_dist is not None and (now - last_volume_key_time) > VOLUME_KEY_COOLDOWN:
                    delta = dist - last_pinch_dist
                    if delta > 0.004:
                        pyautogui.press("volumeup")
                        last_volume_key_time = now
                    elif delta < -0.004:
                        pyautogui.press("volumedown")
                        last_volume_key_time = now
                last_pinch_dist = dist
            else:
                last_pinch_dist = None
        else:
            last_pinch_dist = None

        gesture_buffer.append(raw_gesture)
        most_common_gesture, count = Counter(gesture_buffer).most_common(1)[0]
        confirmed_gesture = most_common_gesture if count >= STABILITY_THRESHOLD else "NONE"

        current_time = time.time()
        elapsed = current_time - last_action_time
        can_trigger = elapsed > cooldown

        # Discrete (single-press) actions - pinch is handled continuously above
        if (confirmed_gesture != "NONE"
                and confirmed_gesture != "PINCH"
                and confirmed_gesture != last_triggered_gesture
                and can_trigger):
            label, color, key, action_name = GESTURE_INFO[confirmed_gesture]
            if key:
                pyautogui.press(key)
                last_action_label = action_name
                last_action_time = current_time
                last_triggered_gesture = confirmed_gesture

        if confirmed_gesture == "NONE":
            last_triggered_gesture = "NONE"
        if confirmed_gesture == "PINCH":
            last_action_label = "Adjusting Volume"
            last_triggered_gesture = "PINCH"

        now = time.time()
        fps = 1 / (now - prev_time) if now != prev_time else fps
        prev_time = now

        # ---------------- UI Overlay ----------------
        label, color, _, _ = GESTURE_INFO[confirmed_gesture]

        panel_w = 380
        draw_panel(frame, 15, 15, panel_w, 150)

        cv2.putText(frame, "GESTURE MEDIA CONTROLLER", (30, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, f"Gesture: {label}", (30, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2, cv2.LINE_AA)
        cv2.putText(frame, f"Last Action: {last_action_label}", (30, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

        progress = min(elapsed / cooldown, 1.0)
        draw_cooldown_bar(frame, 30, 128, panel_w - 30, 12, progress, (100, 220, 140))

        cv2.putText(frame, f"FPS: {int(fps)}", (frame.shape[1] - 120, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)

        # Volume bar always visible
        draw_volume_bar(frame, volume_percent)

        # Draw pinch line between fingers when active
        if pinch_point_a and pinch_point_b:
            cv2.line(frame, pinch_point_a, pinch_point_b, (60, 200, 230), 3)
            cv2.circle(frame, pinch_point_a, 8, (60, 200, 230), -1)
            cv2.circle(frame, pinch_point_b, 8, (60, 200, 230), -1)

        cv2.putText(frame, "Press 'q' to quit", (30, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)

        cv2.imshow("Hand Gesture Media Controller", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
