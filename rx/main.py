from commons import constants as CONSTS
from machine import Pin, SPI
from time import sleep, ticks_ms, ticks_diff
from nrf24l01 import NRF24L01 # type: ignore

CSN_PIN = Pin(17, Pin.OUT)
CE_PIN = Pin(20, Pin.OUT)
SCK_PIN = Pin(18)
MOSI_PIN = Pin(19)
MISO_PIN = Pin(16)

BUILD_IN_LED_PIN = Pin(25, Pin.OUT)

nrf_module = None

def powerOnLed():
    BUILD_IN_LED_PIN.value(1) 
    sleep(0.5)  
    BUILD_IN_LED_PIN.value(0) 

def startupSetup():
    global nrf_module
    print("Setting up NRF24L01 module...")
    NRF_SPI_BUS = SPI(0, sck=SCK_PIN, mosi=MOSI_PIN, miso=MISO_PIN)
    nrf_module = NRF24L01(NRF_SPI_BUS, CSN_PIN, CE_PIN, channel=CONSTS.CHANNEL, payload_size=CONSTS.PAYLOAD_SIZE)
    nrf_module.reg_write(CONSTS.TRANSM_SPEED_REG, CONSTS.SPEED)
    nrf_module.reg_write(CONSTS.ACK_ENABLED_REG, CONSTS.ACK_ENABLED_VALUE)

    nrf_module.open_rx_pipe(1, CONSTS.TX_RX_PIPE)
    nrf_module.start_listening()
    print("NRF24L01 module setup complete. Ready to receive data.")    

powerOnLed()
startupSetup()

packet_count_per_sec = 0
last_time = ticks_ms()

def countPackets():
    global packet_count_per_sec
    global last_time
     # Every second print packets per second
    if ticks_diff(ticks_ms(), last_time) >= 1000:
        print("Packets per sec:", packet_count_per_sec)
        packet_count_per_sec = 0
        last_time = ticks_ms()

while True:
    if nrf_module.any():
        buf = nrf_module.recv()
        packet_count_per_sec += 1
    countPackets()