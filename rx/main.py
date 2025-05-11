from machine import Pin, SPI
from time import sleep, ticks_ms, ticks_diff
from nrf24l01 import NRF24L01

# Pins for SPI
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
csn = Pin(17, Pin.OUT)
ce = Pin(20, Pin.OUT)
led = Pin(25, Pin.OUT)

# Initialization of the NRF24L01 module
nrf = NRF24L01(spi, csn, ce, channel=100, payload_size=5)
nrf.open_rx_pipe(1, b'1Node')
# Set speed 2 Mbps
nrf.reg_write(0x06, 0b00001010)

# Disable ACK
nrf.reg_write(0x01, 0b00000000)

nrf.start_listening()

print("Очікую дані...")

packet_count_per_sec = 0
last_time = ticks_ms()

while True:
    if nrf.any():
        buf = nrf.recv()
        packet_count_per_sec += 1
      
    # Every second print packets per second
    if ticks_diff(ticks_ms(), last_time) >= 1000:
        print("Packets per sec:", packet_count_per_sec)
        packet_count_per_sec = 0
        last_time = ticks_ms()