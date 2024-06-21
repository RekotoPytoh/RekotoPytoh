import socket
import cv2
import numpy as np
import time
from pynput import keyboard, mouse

# Настройки подключения
host = '0.0.0.0' # Replace into IP-address server
port = 12345
secret_key = '192.168.0.102'  # Секретный ключ

# Создание сокета
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)

print("Ожидание подключения клиента...")
conn, addr = server_socket.accept()
print(f"Подключение установлено: {addr}")

# Проверка секретного ключа
received_key = conn.recv(1024).decode('utf-8')
if received_key != secret_key:
    print("Неверный ключ. Отключение.")
    conn.close()
    server_socket.close()
    exit()

# Функции для отправки команд на клиент
def send_command(command):
    try:
        conn.sendall(command.encode('utf-8'))
    except BrokenPipeError as e:
        print(f"Ошибка отправки команды: {e}")

def on_click(x, y, button, pressed):
    if pressed:
        send_command(f'click {x} {y}')

def on_move(x, y):
    send_command(f'move {x} {y}')

def on_press(key):
    try:
        send_command(f'type {key.char}')
    except AttributeError:
        send_command(f'key {key}')

# Настройка прослушивания событий клавиатуры и мыши
mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

try:
    while True:
        # Начало отсчета времени
        start_time = time.time()

        # Получение размера изображения
        length = conn.recv(16)
        if not length:
            break
        length = int(length.decode('utf-8'))

        # Получение изображения
        data = b""
        while len(data) < length:
            packet = conn.recv(length - len(data))
            if not packet:
                break
            data += packet
        
        # Преобразование данных в изображение
        image_data = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        
        # Отображение изображения
        cv2.imshow('Remote Screen', frame)
        if cv2.waitKey(1) == 27:  # Нажатие Esc для выхода
            break
        
        # Контроль времени для достижения 60 кадров в секунду
        elapsed_time = time.time() - start_time
        time.sleep(max(1./60 - elapsed_time, 0))
finally:
    conn.close()
    server_socket.close()
    cv2.destroyAllWindows()
    mouse_listener.stop()
    keyboard_listener.stop()
