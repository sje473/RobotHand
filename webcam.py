import cv2
import mediapipe as mp
from collections import deque
import serial
import time

# Initialize serial connection to Arduino
try:
    arduino = serial.Serial('COM10', 9600, timeout=1)
    time.sleep(2)
    print("Connected to Arduino!")
except:
    print("Could not connect to Arduino. Running without serial.")
    arduino = None

# Status history buffers for smoothing
BUFFER_SIZE = 10
THUMB_BUFFER_SIZE = 3  # shorter buffer for more responsive thumb
thumb_history = deque(maxlen=THUMB_BUFFER_SIZE)
index_history = deque(maxlen=BUFFER_SIZE)
middle_history = deque(maxlen=BUFFER_SIZE)
ring_history = deque(maxlen=BUFFER_SIZE)
pinky_history = deque(maxlen=BUFFER_SIZE)

def get_smoothed_status(history_buffer):
    if len(history_buffer) == 0:
        return "Unknown"
    status_counts = {}
    for status in history_buffer:
        status_counts[status] = status_counts.get(status, 0) + 1
    return max(status_counts, key=status_counts.get)

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ---- Camera open (robust) ----
def open_camera():
    # Try common backends on Windows and a few indices
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    indices = [0, 1, 2, 3]
    for be in backends:
        for idx in indices:
            cap = cv2.VideoCapture(idx, be)
            if cap.isOpened():
                ok, _ = cap.read()
                if ok:
                    print(f"Camera opened on index {idx} (backend {be}).")
                    # Optional: request MJPG for smoother capture if supported
                    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                    return cap
                cap.release()
    return None

webcam = open_camera()
if webcam is None:
    print("ERROR: Could not open any camera. "
          "Close apps using the camera (Zoom/Teams/OBS/Browser), "
          "then check Windows Settings > Privacy & security > Camera "
          "and allow desktop apps. Try replugging the webcam.")
    hands.close()
    raise SystemExit

def get_finger_bend_status(hand_landmarks, finger_name):
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    if finger_name == "INDEX":
        tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
        mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    elif finger_name == "MIDDLE":
        tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
        mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    elif finger_name == "RING":
        tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
        pip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP]
        mcp = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
    elif finger_name == "PINKY":
        tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
        pip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]
        mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
    else:
        return "Unknown"
    tip_dist = ((tip.x - wrist.x)**2 + (tip.y - wrist.y)**2 + (tip.z - wrist.z)**2)**0.5
    pip_dist = ((pip.x - wrist.x)**2 + (pip.y - wrist.y)**2 + (pip.z - wrist.z)**2)**0.5
    if tip_dist > pip_dist * 1.15:
        return "Straight"
    elif tip_dist > pip_dist * 1.05:
        return "Half Bent"
    else:
        return "Bent"

def get_thumb_sweep_status(hand_landmarks):
    """Determines if thumb is swept across palm or not (sensitive but not stuck)"""
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_cmc = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_CMC]
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    middle_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]

    thumb_extension = abs(thumb_tip.x - wrist.x)
    base_extension  = abs(thumb_cmc.x - wrist.x)
    extension_ratio = thumb_extension / base_extension if base_extension > 1e-6 else 1.0

    palm_size = ((middle_mcp.x - wrist.x)**2 + (middle_mcp.y - wrist.y)**2 + (middle_mcp.z - wrist.z)**2)**0.5 + 1e-6
    y_gap_norm = abs(thumb_tip.y - middle_mcp.y) / palm_size

    if (extension_ratio < 1.05) and (y_gap_norm < 0.50):
        return "Fully Swept"
    elif (extension_ratio < 1.70) and (y_gap_norm < 0.50):
        return "Half Swept"
    else:
        return "Not Swept"

# ---- Fullscreen window (added) ----
WINDOW_NAME = "Hand Tracking - Press 'q' to quit"
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, frame = webcam.read()
    if not ret:
        print("No frame from camera, trying to reopen...")
        webcam.release()
        webcam = open_camera()
        if webcam is None:
            print("ERROR: Camera lost and could not be reopened.")
            break
        continue

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(
            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style()
        )

        # Get statuses
        index_status = get_finger_bend_status(hand_landmarks, "INDEX")
        middle_status = get_finger_bend_status(hand_landmarks, "MIDDLE")
        ring_status = get_finger_bend_status(hand_landmarks, "RING")
        pinky_status = get_finger_bend_status(hand_landmarks, "PINKY")
        thumb_status = get_thumb_sweep_status(hand_landmarks)

        # Add to buffers
        thumb_history.append(thumb_status)
        index_history.append(index_status)
        middle_history.append(middle_status)
        ring_history.append(ring_status)
        pinky_history.append(pinky_status)

        # Smoothed outputs
        thumb_smooth = get_smoothed_status(thumb_history)
        index_smooth = get_smoothed_status(index_history)
        middle_smooth = get_smoothed_status(middle_history)
        ring_smooth = get_smoothed_status(ring_history)
        pinky_smooth = get_smoothed_status(pinky_history)

        # Display statuses
        y_offset = 30
        for label, value in [
            ("Thumb", thumb_smooth), ("Index", index_smooth),
            ("Middle", middle_smooth), ("Ring", ring_smooth),
            ("Pinky", pinky_smooth)
        ]:
            cv2.putText(frame, f"{label}: {value}", (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            y_offset += 35

        # Print & send to Arduino
        print(f"T:{thumb_smooth}, I:{index_smooth}, M:{middle_smooth}, R:{ring_smooth}, P:{pinky_smooth}")
        if arduino:
            serial_msg = f"T:{thumb_smooth},I:{index_smooth},M:{middle_smooth},R:{ring_smooth},P:{pinky_smooth}\n"
            arduino.write(serial_msg.encode())

    cv2.imshow(WINDOW_NAME, frame)
    if cv2.waitKey(20) & 0xFF == ord("q"):
        break

# Cleanup
hands.close()
webcam.release()
cv2.destroyAllWindows()
