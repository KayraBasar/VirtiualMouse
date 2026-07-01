import cv2
import mediapipe as mp
import pyautogui
import math
import numpy as np  
import time        

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False     
# Farenin köşelere gidip programı çökertmesini engeller

screen_width, screen_height = pyautogui.size()

# MediaPipe Kurulumu
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    static_image_mode=False,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# Kamera Ayarları
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Fare yumuşatma (Smoothing) değişkenleri
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0
smooth_factor = 4  

# Tıklama ve bekleme durumları
left_clicked = False
right_clicked = False
last_vol_time = time.time()
vol_cooldown = 0.3 

def get_distance(lm1, lm2, frame_w, frame_h):
    x1, y1 = int(lm1.x * frame_w), int(lm1.y * frame_h)
    x2, y2 = int(lm2.x * frame_w), int(lm2.y * frame_h)
    return math.hypot(x2 - x1, y2 - y1)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Ekranı aynala ve boyutları al
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesture_text = "Mod: Bekleniyor"

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]
            middle_tip = hand_landmarks.landmark[12]
            ring_tip = hand_landmarks.landmark[16]
            pinky_tip = hand_landmarks.landmark[20]
            
            
            wrist = hand_landmarks.landmark[0]
            index_mcp = hand_landmarks.landmark[5]

           
            ref_length = get_distance(wrist, index_mcp, w, h)
            pinch_threshold = ref_length / 2.0 

            
            dist_thumb_index = get_distance(thumb_tip, index_tip, w, h)
            dist_thumb_middle = get_distance(thumb_tip, middle_tip, w, h)
            dist_thumb_ring = get_distance(thumb_tip, ring_tip, w, h)

            #1. SES KONTROLÜ (Yumruk Yapma)
            if index_tip.y > hand_landmarks.landmark[6].y and middle_tip.y > hand_landmarks.landmark[10].y and pinky_tip.y > hand_landmarks.landmark[18].y:
                tilt = index_mcp.x - wrist.x
                current_time = time.time()
                
                # Sadece cooldown süresi dolduğunda tuşa bas
                if current_time - last_vol_time > vol_cooldown:
                    if tilt > 0.05: 
                        pyautogui.press('volumeup')
                        gesture_text = "Ses Artiriliyor"
                        last_vol_time = current_time
                    elif tilt < -0.05: 
                        pyautogui.press('volumedown')
                        gesture_text = "Ses Azaltiliyor"
                        last_vol_time = current_time
                    else:
                        gesture_text = "Yumruk - Ses Hazir"

            # 2. SOL TIK (Baş, İşaret, Orta Bitişik) 
            elif dist_thumb_index < pinch_threshold and dist_thumb_middle < pinch_threshold:
                if not left_clicked:
                    pyautogui.mouseDown(button='left')
                    left_clicked = True
                gesture_text = "Sol Tik (Basili)"

            # 3. SAĞ TIK (Baş ve Yüzük Parmağı Bitişik) 
            elif dist_thumb_ring < pinch_threshold:
                if not right_clicked:
                    pyautogui.click(button='right')
                    right_clicked = True
                gesture_text = "Sag Tiklandi"

            # 4. FARE HAREKETİ (Sadece Baş ve İşaret Bitişik)
            elif dist_thumb_index < pinch_threshold and dist_thumb_middle > pinch_threshold:
                mouse_x = int(thumb_tip.x * w)
                mouse_y = int(thumb_tip.y * h)

                # Ekran köşelerine ulaşmayı kolaylaştırmak için interpole alanını daralttım (150 piksel margin)
                screen_x = np.interp(mouse_x, (150, w - 150), (0, screen_width))
                screen_y = np.interp(mouse_y, (150, h - 150), (0, screen_height))

                # Yumuşatma (Smoothing)
                curr_x = prev_x + (screen_x - prev_x) / smooth_factor
                curr_y = prev_y + (screen_y - prev_y) / smooth_factor

                pyautogui.moveTo(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y
                
                # Hareket halindeyken eski tıklamaları serbest bırak
                if left_clicked:
                    pyautogui.mouseUp(button='left')
                    left_clicked = False
                right_clicked = False 
                
                gesture_text = "Fare Hareket Ediyor"
                cv2.circle(frame, (mouse_x, mouse_y), 10, (255, 0, 255), cv2.FILLED)

            #  5. BOŞTA (El açık)
            else:
                if left_clicked:
                    pyautogui.mouseUp(button='left')
                    left_clicked = False
                right_clicked = False
                gesture_text = "El Acik - Bosta"

    # Çıkış yönergesini de ekrana yazdıralım
    cv2.putText(frame, gesture_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, "Cikmak icin 'q' ya basin", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.imshow("Sihirli Fare", frame)

    # q harfine basılırsa döngüyü kır
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
