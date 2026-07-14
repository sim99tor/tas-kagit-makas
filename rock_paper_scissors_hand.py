import os
import urllib.request
import cv2
import numpy as np
import random
import time

from mediapipe.tasks.python.vision import hand_landmarker as hl
from mediapipe.tasks.python.core import base_options as bo
from mediapipe.tasks.python.vision.core import image as mp_image

MODEL_URL = "https://storage.googleapis.com/mediapipe-assets/hand_landmarker.task"
MODEL_FILE = "hand_landmarker.task"

secenekler = ["Tas", "Kagit", "Makas"]
pc_secim = ""
oyuncu_secim = "Bilinmiyor"
sonuc = ""
countdown_start = 0.0
pending_choice = None
countdown_state = "waiting"  # waiting, countdown, result

TIP_IDS = [hl.HandLandmark.INDEX_FINGER_TIP.value,
           hl.HandLandmark.MIDDLE_FINGER_TIP.value,
           hl.HandLandmark.RING_FINGER_TIP.value,
           hl.HandLandmark.PINKY_TIP.value]
PIP_IDS = [hl.HandLandmark.INDEX_FINGER_PIP.value,
           hl.HandLandmark.MIDDLE_FINGER_PIP.value,
           hl.HandLandmark.RING_FINGER_PIP.value,
           hl.HandLandmark.PINKY_PIP.value]


def ensure_model_exists() -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_path = os.path.join(script_dir, MODEL_FILE)
    if os.path.exists(local_path):
        return local_path

    print("Model dosyası indiriliyor...")
    urllib.request.urlretrieve(MODEL_URL, local_path)
    print("Model indirildi:", local_path)
    return local_path


def create_landmarker() -> hl.HandLandmarker:
    model_path = ensure_model_exists()
    base_options = bo.BaseOptions(model_asset_path=model_path)
    options = hl.HandLandmarkerOptions(base_options=base_options, num_hands=1)
    return hl.HandLandmarker.create_from_options(options)


def draw_hand_landmarks(image: np.ndarray, landmarks):
    h, w, _ = image.shape
    for connection in hl.HandLandmarksConnections.HAND_CONNECTIONS:
        start = landmarks[connection.start]
        end = landmarks[connection.end]
        cv2.line(
            image,
            (int(start.x * w), int(start.y * h)),
            (int(end.x * w), int(end.y * h)),
            (0, 255, 0),
            2,
        )
    for lm in landmarks:
        cv2.circle(image, (int(lm.x * w), int(lm.y * h)), 4, (0, 0, 255), -1)


def get_player_choice(landmarks) -> str:
    fingers = []
    for tip_id, pip_id in zip(TIP_IDS, PIP_IDS):
        if landmarks[tip_id].y < landmarks[pip_id].y:
            fingers.append(1)
        else:
            fingers.append(0)

    if fingers == [0, 0, 0, 0]:
        return "Tas"
    if fingers == [1, 1, 1, 1]:
        return "Kagit"
    if fingers == [1, 1, 0, 0]:
        return "Makas"
    return "Gecersiz"


def determine_result(oyuncu_secim: str, pc_secim: str) -> str:
    if oyuncu_secim == pc_secim:
        return "Berabere!"
    if (oyuncu_secim == "Tas" and pc_secim == "Makas") or \
       (oyuncu_secim == "Kagit" and pc_secim == "Tas") or \
       (oyuncu_secim == "Makas" and pc_secim == "Kagit"):
        return "Kazandin!"
    return "PC Kazandi!"


def main() -> None:
    global pc_secim, oyuncu_secim, sonuc, countdown_start, pending_choice, countdown_state

    with create_landmarker() as landmarker:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Kamera açılamadı. Lütfen kamera bağlantısını kontrol et.")

        while True:
            success, frame = cap.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_img = mp_image.Image(mp_image.ImageFormat.SRGB, rgb_frame)
            result = landmarker.detect(mp_img)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('b'):
                if countdown_state != "countdown":
                    countdown_state = "countdown"
                    countdown_start = time.time()
                    pending_choice = None
                    sonuc = ""
                    pc_secim = ""

            if countdown_state == "countdown":
                elapsed = time.time() - countdown_start
                if elapsed >= 3:
                    countdown_state = "result"
                    pc_secim = random.choice(secenekler)
                    if result.hand_landmarks:
                        oyuncu_secim = get_player_choice(result.hand_landmarks[0])
                    else:
                        oyuncu_secim = "Gecersiz"
                    sonuc = determine_result(oyuncu_secim, pc_secim)
            elif countdown_state == "result":
                if key == ord('b'):
                    countdown_state = "countdown"
                    countdown_start = time.time()
                    pending_choice = None
                    sonuc = ""
                    pc_secim = ""
                if result.hand_landmarks:
                    draw_hand_landmarks(frame, result.hand_landmarks[0])
                    oyuncu_secim = get_player_choice(result.hand_landmarks[0])
                else:
                    oyuncu_secim = "Gecersiz"
            else:
                if result.hand_landmarks:
                    draw_hand_landmarks(frame, result.hand_landmarks[0])
                    oyuncu_secim = get_player_choice(result.hand_landmarks[0])
                else:
                    oyuncu_secim = "Bekleniyor..."

            cv2.putText(frame, "Baslamak icin 'b' bas", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (220, 220, 220), 2)
            cv2.putText(frame, f"Sen: {oyuncu_secim}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            if countdown_state == "countdown":
                elapsed = time.time() - countdown_start
                say_text = "3" if elapsed < 1 else "2" if elapsed < 2 else "1"
                cv2.putText(frame, f"Say: {say_text}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 2)
                cv2.putText(frame, "PC: ", (10, 170), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                cv2.putText(frame, "Sonuc: ", (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            else:
                if pc_secim:
                    cv2.putText(frame, f"PC: {pc_secim}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                if sonuc:
                    renk = (0, 255, 0) if sonuc == "Kazandin!" else (0, 0, 255) if sonuc == "PC Kazandi!" else (0, 255, 255)
                    cv2.putText(frame, f"Sonuc: {sonuc}", (10, 170), cv2.FONT_HERSHEY_SIMPLEX, 1.2, renk, 2)

            cv2.imshow("Tas Kagit Makas - Cikmak icin 'q'ya bas", frame)
            if key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
