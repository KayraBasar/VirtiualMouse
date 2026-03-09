import cv2
import mediapipe as mp
import pyautogui
import math

# PyAutoGUI Optimizasyonları
pyautogui.PAUSE = 0
screen_width, screen_height = pyautogui.size()

# MediaPipe Kurulumu
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1, # Fare için sadece tek el kullanmak çok daha kararlıdır
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
smooth_factor = 5  # Bu değer ne kadar büyükse fare o kadar yavaş ve yumuşak hareket eder

# Tıklama durumlarını tutmak için
left_clicked = False
right_clicked = False

def get_distance(lm1, lm2, frame_w, frame_h):
    """İki landmark (nokta) arasındaki mesafeyi piksel cinsinden hesaplar."""
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
            
            # Önemli Parmak Uçları (Landmarks)
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]
            middle_tip = hand_landmarks.landmark[12]
            ring_tip = hand_landmarks.landmark[16]
            
            # Yumruk algılama için eklemler
            wrist = hand_landmarks.landmark[0]
            index_mcp = hand_landmarks.landmark[5]
            pinky_tip = hand_landmarks.landmark[20]

            # Mesafeleri hesapla
            dist_thumb_index = get_distance(thumb_tip, index_tip, w, h)
            dist_thumb_middle = get_distance(thumb_tip, middle_tip, w, h)
            dist_thumb_ring = get_distance(thumb_tip, ring_tip, w, h)

            pinch_threshold = 35 # Parmakların 'bitişik' sayılacağı piksel mesafesi

            # --- 1. SES KONTROLÜ (Yumruk Yapma) ---
            # Eğer işaret, orta ve serçe parmak uçları bileğe, kendi köklerinden daha yakınsa el yumruktur
            if index_tip.y > hand_landmarks.landmark[6].y and middle_tip.y > hand_landmarks.landmark[10].y and pinky_tip.y > hand_landmarks.landmark[18].y:
                
                # Bilek ile işaret parmağı kökü arasındaki X ekseni açısına/farkına bakıyoruz
                tilt = index_mcp.x - wrist.x
                
                if tilt > 0.05: # El sağa yatık
                    pyautogui.press('volumeup')
                    gesture_text = "Ses Artiriliyor"
                elif tilt < -0.05: # El sola yatık
                    pyautogui.press('volumedown')
                    gesture_text = "Ses Azaltiliyor"
                else:
                    gesture_text = "Yumruk - Ses Hazir"

            # --- 2. SOL TIK (Baş, İşaret, Orta Bitişik) ---
            elif dist_thumb_index < pinch_threshold and dist_thumb_middle < pinch_threshold:
                if not left_clicked:
                    pyautogui.mouseDown(button='left')
                    left_clicked = True
                gesture_text = "Sol Tik (Basili)"

            # --- 3. SAĞ TIK (Baş ve Yüzük Parmağı Bitişik) ---
            elif dist_thumb_ring < pinch_threshold:
                if not right_clicked:
                    pyautogui.click(button='right')
                    # Ya da çift tıklama istersen üst satırı silip bunu aç:
                    # pyautogui.doubleClick()
                    right_clicked = True
                gesture_text = "Sag Tiklandi"

            # --- 4. FARE HAREKETİ (Sadece Baş ve İşaret Bitişik) ---
            elif dist_thumb_index < pinch_threshold and dist_thumb_middle > pinch_threshold:
                # Fareyi hareket ettirmek için parmakların orta noktasını al
                mouse_x = int(thumb_tip.x * w)
                mouse_y = int(thumb_tip.y * h)

                # Kamera alanını ekrana oranla (Kameranın kenarlarına tam gitmeden ekranı kaplamak için)
                screen_x = np.interp(mouse_x, (100, w - 100), (0, screen_width))
                screen_y = np.interp(mouse_y, (100, h - 100), (0, screen_height))

                # Yumuşatma (Smoothing) uygula
                curr_x = prev_x + (screen_x - prev_x) / smooth_factor
                curr_y = prev_y + (screen_y - prev_y) / smooth_factor

                pyautogui.moveTo(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y
                
                # Tıklamaları serbest bırak
                if left_clicked:
                    pyautogui.mouseUp(button='left')
                    left_clicked = False
                right_clicked = False # Sağ tık kilidini aç
                
                gesture_text = "Fare Hareket Ediyor"
                
                # Hareket noktasını ekranda göster
                cv2.circle(frame, (mouse_x, mouse_y), 10, (255, 0, 255), cv2.FILLED)

            # --- 5. BOŞTA (El açık) ---
            else:
                if left_clicked:
                    pyautogui.mouseUp(button='left')
                    left_clicked = False
                right_clicked = False
                gesture_text = "El Acik - Bosta"

    import numpy as np # interp fonksiyonu için numpy gerekli

    # Durumu ekrana yazdır
    cv2.putText(frame, gesture_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Sihirli Fare", frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()