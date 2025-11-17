import cv2
import mediapipe as mp
import pygame
import os
import time

# Init pygame and load music
pygame.mixer.init()
music_folder = "music"
music_files = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]
if not music_files:
    print("\n❌ No MP3 files found in 'music' folder!")
    exit()
print("\nMusic files found:", music_files)
current_index = 0
pygame.mixer.music.load(os.path.join(music_folder, music_files[current_index]))
pygame.mixer.music.play()

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Camera setup
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("\n❌ Failed to access camera.")
    exit()

# Gesture control state
last_action_time = 0
gesture_cooldown = 1.5  # seconds
PAUSE_STATE = False
music_status = "playing"
prev_gesture = None
last_hand_x = None

# Helper function to count raised fingers
def count_fingers(hand_landmarks):
    fingers = []
    tips_ids = [4, 8, 12, 16, 20]

    for i in range(1, 5):
        fingers.append(hand_landmarks[tips_ids[i]].y < hand_landmarks[tips_ids[i] - 2].y)

    thumb = hand_landmarks[tips_ids[0]].x > hand_landmarks[tips_ids[0] - 1].x
    fingers.insert(0, thumb)
    return fingers.count(True)

# Gesture detection loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    curr_time = time.time()
    gesture = None

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            landmarks = handLms.landmark
            finger_count = count_fingers(landmarks)
            hand_x = landmarks[0].x

            if finger_count == 0:
                gesture = "PAUSE"
            elif finger_count == 5:
                if last_hand_x is not None:
                    if hand_x - last_hand_x > 0.1:
                        gesture = "NEXT"
                    elif last_hand_x - hand_x > 0.1:
                        gesture = "PREVIOUS"
                last_hand_x = hand_x
            elif finger_count == 5 and prev_gesture != "STOP":
                gesture = "STOP"

    if gesture and gesture != prev_gesture and curr_time - last_action_time >= gesture_cooldown:
        if gesture == "NEXT":
            current_index = (current_index + 1) % len(music_files)
            pygame.mixer.music.load(os.path.join(music_folder, music_files[current_index]))
            pygame.mixer.music.play()
            print("\n➡️ Next song playing:", music_files[current_index])
            music_status = "playing"
            PAUSE_STATE = False

        elif gesture == "PREVIOUS":
            current_index = (current_index - 1) % len(music_files)
            pygame.mixer.music.load(os.path.join(music_folder, music_files[current_index]))
            pygame.mixer.music.play()
            print("\n⬅️ Previous song playing:", music_files[current_index])
            music_status = "playing"
            PAUSE_STATE = False

        elif gesture == "STOP" and music_status != "stopped":
            pygame.mixer.music.stop()
            print("\n🛑 Music stopped")
            music_status = "stopped"

        elif gesture == "PAUSE":
            if music_status == "paused":
                pygame.mixer.music.unpause()
                print("\n▶️ Music resumed")
                music_status = "playing"
            elif music_status == "playing":
                pygame.mixer.music.pause()
                print("\n⏸️ Music paused")
                music_status = "paused"

        last_action_time = curr_time
        prev_gesture = gesture

    cv2.imshow("Gesture Music Player", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
