import socket
import cv2
import numpy as np
import pyautogui
import time
import threading
from PIL import Image
import pystray

# Настройки подключения
host = '192.168.0.102'  # Замените на IP-адрес сервера
port = 12345
secret_key = '192.168.0.102'  # Секретный ключ

# Функция для отправки данных экрана
def send_screen_data():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.sendall(secret_key.encode('utf-8'))

    try:
        while running:
            # Начало отсчета времени
            start_time = time.time()

            # Захват экрана
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Сжатие изображения для уменьшения размера данных
            _, buffer = cv2.imencode('.jpg', frame)
            image_data = buffer.tobytes()

            # Отправка размера изображения
            length = str(len(image_data)).ljust(16).encode('utf-8')
            client_socket.sendall(length)
            
            # Отправка самого изображения
            client_socket.sendall(image_data)
            
            # Контроль времени для достижения 60 кадров в секунду
            elapsed_time = time.time() - start_time
            time.sleep(max(1./60 - elapsed_time, 0))
    finally:
        client_socket.close()

# Функция для создания иконки в системном трее
def create_tray_icon():
    icon = Image.new('RGB', (64, 64), color='red')
    menu = pystray.Menu(
        pystray.MenuItem('Exit', on_exit)
    )
    tray_icon = pystray.Icon("ScreenSender", icon, "Screen Sender", menu)
    tray_icon.run()

# Функция для завершения программы
def on_exit(icon, item):
    global running
    running = False
    icon.stop()

# Запуск отправки данных экрана в отдельном потоке
running = True
threading.Thread(target=send_screen_data, daemon=True).start()

# Запуск иконки в системном трее
create_tray_icon()
