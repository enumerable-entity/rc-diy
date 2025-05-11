import machine
import utime
import struct
import _thread
from nrf24l01 import NRF24L01
import servo  # це твій модуль для PWM серво

# NRF24L01 ініціалізація
spi = machine.SPI(0, baudrate=8000000, sck=machine.Pin(2), mosi=machine.Pin(3), miso=machine.Pin(4))
csn = machine.Pin(5, machine.Pin.OUT)
ce = machine.Pin(6, machine.Pin.OUT)

nrf = NRF24L01(spi, csn, ce, payload_size=8)
nrf.open_tx_pipe(b'\xd2\xf0\xf0\xf0\xf0')
nrf.open_rx_pipe(1, b'\xe1\xf0\xf0\xf0\xf0')
nrf.start_listening()

# Серви та мотор
servo1 = servo.Servo(machine.Pin(10))
servo2 = servo.Servo(machine.Pin(11))
motor = machine.PWM(machine.Pin(12))
motor.freq(1000)

# Лампочки
led1 = machine.Pin(13, machine.Pin.OUT)
led2 = machine.Pin(14, machine.Pin.OUT)

# Спільні змінні (будуть оновлюватися другим ядром)
shared_data = {
    "x1": 128,
    "x2": 128,
    "b1": 0,
    "b2": 0,
    "last_packet": utime.ticks_ms()
}

# Замок для потокобезпеки
lock = _thread.allocate_lock()

# 🟢 ЯДРО 1: Тільки прийом NRF24
def nrf_loop():
    while True:
        if nrf.any():
            buf = nrf.recv()
            x1, x2, b1, b2 = struct.unpack('BB??', buf)
            with lock:
                shared_data["x1"] = x1
                shared_data["x2"] = x2
                shared_data["b1"] = b1
                shared_data["b2"] = b2
                shared_data["last_packet"] = utime.ticks_ms()

# 🔵 ЯДРО 0: Серви, мотор і лампочки (гладке керування)
def control_loop():
    last_update = utime.ticks_ms()
    smooth_x1 = 128
    smooth_x2 = 128

    while True:
        now = utime.ticks_ms()

        with lock:
            target_x1 = shared_data["x1"]
            target_x2 = shared_data["x2"]
            b1 = shared_data["b1"]
            b2 = shared_data["b2"]
            last_packet = shared_data["last_packet"]

        # Плавне згладжування (слайдінг)
        smooth_x1 += (target_x1 - smooth_x1) * 0.1  # фактор згладжування
        smooth_x2 += (target_x2 - smooth_x2) * 0.1

        # Серво
        angle1 = int((smooth_x1 / 255) * 180)
        angle2 = int((smooth_x2 / 255) * 180)
        servo1.write(angle1)
        servo2.write(angle2)

        # Лампочки
        led1.value(b1)
        led2.value(b2)

        # Мотор (тяга)
        duty = int((smooth_x2 / 255) * 65535)
        motor.duty_u16(duty)

        # Якщо пакетів нема вже 300 мс — аварійний режим
        if utime.ticks_diff(now, last_packet) > 300:
            servo1.write(90)
            servo2.write(90)
            motor.duty_u16(0)

        utime.sleep_ms(20)  # 50 Гц оновлення серв (реальний для сервоприводів)

# Старт NRF прийому на ядрі 1
_thread.start_new_thread(nrf_loop, ())

# Головний цикл на ядрі 0
control_loop()

