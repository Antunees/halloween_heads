import cv2
import serial
import time

arduino = serial.Serial('COM3', 9600)
time.sleep(2)

cap = cv2.VideoCapture(0)
_, frame1 = cap.read()
_, frame2 = cap.read()

def enviar_para_arduino(x, y):
    mensagem = f"{x},{y}\n"
    arduino.write(mensagem.encode('utf-8'))

while cap.isOpened():
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)

    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    frame_centers = []

    for contour in contours:
        if cv2.contourArea(contour) < 500:
            continue

        (x, y, w, h) = cv2.boundingRect(contour)
        cx = x + w // 2
        cy = y + h // 2
        frame_centers.append((cx, cy))

        cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame1, (cx, cy), 5, (0, 0, 255), -1)

        enviar_para_arduino(cx, cy)

    cv2.imshow("Detector de Movimento", frame1)
    frame1 = frame2
    _, frame2 = cap.read()

    if cv2.waitKey(10) == 27:
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
