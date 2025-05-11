from machine import Pin, SPI
from time import sleep, ticks_ms, ticks_diff
from nrf24l01 import NRF24L01

# Піни для SPI
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
csn = Pin(17, Pin.OUT)
ce = Pin(20, Pin.OUT)
led = Pin(25, Pin.OUT)

# Ініціалізація NRF24L01
nrf = NRF24L01(spi, csn, ce, channel=100, payload_size=5)
nrf.open_rx_pipe(1, b'1Node')
# Встановити 2 Mbps
nrf.reg_write(0x06, 0b00001010)

# Вимкнути автопідтвердження (ACK)
nrf.reg_write(0x01, 0b00000000)

nrf.start_listening()

print("Очікую дані...")

packet_count_per_sec = 0
last_time = ticks_ms()

while True:
    if nrf.any():
        buf = nrf.recv()
        packet_count_per_sec += 1
      
    # Перевірка кожну секунду
    if ticks_diff(ticks_ms(), last_time) >= 1000:
        print("Пакетів за секунду:", packet_count_per_sec)
        packet_count_per_sec = 0
        last_time = ticks_ms()