from commons import constants as CONSTS
from machine import Pin, SPI, ADC
from time import sleep
from nrf24l01 import NRF24L01 # type: ignore

CSN_PIN = Pin(17, Pin.OUT)
CE_PIN = Pin(20, Pin.OUT)
SCK_PIN = Pin(18)
MOSI_PIN = Pin(19)
MISO_PIN = Pin(16)

BUILD_IN_LED_PIN = Pin(25, Pin.OUT)

READ_PIN = Pin(28, Pin.IN)
adc_x1 = ADC(READ_PIN)
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

    nrf_module.open_tx_pipe(CONSTS.TX_RX_PIPE)
    print("NRF24L01 module setup complete. Ready to send data.")


def sendData(msg):
    global nrf_module
    buf = bytearray(CONSTS.PAYLOAD_SIZE)
    x1 = adc_x1.read_u16() >> 8  # 0-255
    buf[0] = x1
    buf[1] = 172

    nrf_module.send(buf)
    #print("Sending data:", buf)
    #print("Sent:", buf[0], buf[1])
    sleep(0.001)
    #sleep(0.01) 
    
powerOnLed()
startupSetup()

while True:
    try:
        sendData(128)
    except OSError as e:
        print("Error:", e)