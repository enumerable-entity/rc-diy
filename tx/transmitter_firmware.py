import machine
import utime
import struct
import _thread
from nrf24l01 import NRF24L01

# NRF24L01 ініціалізація
spi = machine.SPI(0, baudrate=8000000, sck=machine.Pin(2), mosi=machine.Pin(3), miso=machine.Pin(4))
csn = machine.Pin(5, machine.Pin.OUT)
ce = machine.Pin(6, machine.Pin.OUT)

nrf = NRF24L01(spi, csn, ce, payload_size=8)
nrf.open_tx_pipe(b'\xe1\xf0\xf0\xf0\xf0')
nrf.open_rx_pipe(1, b'\xd2\xf0\xf0\xf0\xf0')
nrf.stop_listening()

# Джойстики (ADC)
adc_x1 = machine.ADC(26)
adc_x2 = machine.ADC(27)

# Перемикачі (GPIO)
sw1 = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
sw2 = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

# Спільні дані
shared_data = {
    "x1": 128,
    "x2": 128,
    "b1": False,
    "b2": False
}

# Замок для потокобезпеки
lock = _thread.allocate_lock()

# 🟢 ЯДРО 1: Тільки передача по NRF24
def nrf_loop():
    while True:
        with lock:
            x1 = shared_data["x1"]
            x2 = shared_data["x2"]
            b1 = shared_data["b1"]
            b2 = shared_data["b2"]

        buf = struct.pack('BB??', x1, x2, b1, b2)
        try:
            nrf.send(buf)
        except OSError:
            pass  # Якщо буфер NRF забитий — ігноруємо

        # Максимально безперервна передача (нема sleep!)

# 🔵 ЯДРО 0: Зчитування джойстиків і перемикачів
def read_loop():
    while True:
        x1 = adc_x1.read_u16() >> 8  # 0-255
        x2 = adc_x2.read_u16() >> 8  # 0-255

        b1 = not sw1.value()  # активний 0 → натиснуто
        b2 = not sw2.value()

        with lock:
            shared_data["x1"] = x1
            shared_data["x2"] = x2
            shared_data["b1"] = b1
            shared_data["b2"] = b2

        utime.sleep_ms(10)  # 100 Гц опитування джойстиків

# Старт NRF передачі на ядрі 1
_thread.start_new_thread(nrf_loop, ())

# Головний цикл на ядрі 0
read_loop()
