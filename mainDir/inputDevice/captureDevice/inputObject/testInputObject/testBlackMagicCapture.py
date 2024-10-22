import cv2

# Imposta il numero della sorgente video (0 per la prima webcam, 1 per la seconda, etc.)
# Se la Blackmagic è connessa, potrebbe essere 0, 1 o un numero diverso.
capture = cv2.VideoCapture("udp://127.0.0.1:12345")  # Prova 0, 1, 2, ecc. se non funziona
capture.set(cv2.CAP_PROP_FPS, 60)
# Verifica se la cattura video è stata aperta correttamente
if not capture.isOpened():
    print("Errore: impossibile aprire il dispositivo video")
else:
    print("Dispositivo video aperto correttamente")

# Imposta la risoluzione, se necessario
# capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Se vuoi impostare la larghezza
# capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # Se vuoi impostare l'altezza

while True:
    # Leggi il frame dalla cattura video
    ret, frame = capture.read()
    actual_fps = capture.get(cv2.CAP_PROP_FPS)
    print(f"Actual FPS: {actual_fps}")
    # Se il frame è stato letto correttamente, ret sarà True
    if not ret:
        print("Errore nella lettura del frame")
        break

    # Mostra il frame catturato
    cv2.imshow('BlackMagic Capture', frame)

    # Esci dal ciclo premendo il tasto 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Rilascia il dispositivo video e chiudi tutte le finestre
capture.release()
cv2.destroyAllWindows()
