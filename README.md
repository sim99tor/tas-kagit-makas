# Taş-Kağıt-Makas Oyunu

Bu proje iki sürüme sahip:

1. `rock-paper-scissors.html` — tarayıcıda oynanan basit taş-kağıt-makas.
2. `rock_paper_scissors_hand.py` — kamera ile el hareketlerini algılayan Python oyun.

## Dosyalar

- `rock-paper-scissors.html`
- `rock_paper_scissors_hand.py`
- `serve_game.py`
- `hand_landmarker.task` (MediaPipe modeli, isteğe bağlı)
- `requirements.txt`

## Nasıl çalıştırılır

### Tarayıcı sürümü

1. `serve_game.py` dosyasını çalıştırın:
   ```
   py serve_game.py
   ```
2. Sonra tarayıcıda verilen URL'yi açın.

### Kamera sürümü

1. Gerekli paketleri yükleyin:
   ```
   py -m pip install opencv-python mediapipe
   ```
2. `rock_paper_scissors_hand.py` dosyasını çalıştırın:
   ```
   py rock_paper_scissors_hand.py
   ```
3. Ekranda `b` tuşuna basarak oyunu başlatın.

