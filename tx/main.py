from machine import Pin, SPI
from time import sleep
from nrf24l01 import NRF24L01

# Піни для SPI
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
csn = Pin(17, Pin.OUT)
ce = Pin(20, Pin.OUT)
led = Pin(25, Pin.OUT)
nrf = NRF24L01(spi, csn, ce, channel=100, payload_size=5)
# Встановити 2 Mbps
nrf.reg_write(0x06, 0b00001010)

# Вимкнути автопідтвердження (ACK)
nrf.reg_write(0x01, 0b00000000)

nrf.open_tx_pipe(b'1Node')

while True:
    try:
        led.off()
        nrf.send(b'Hello')
        print("Sending Hello")
        sleep(0.001)
    except OSError as e:
        print("Помилка:", e)