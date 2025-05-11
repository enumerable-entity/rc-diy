from machine import Pin, SPI
from time import sleep
import utime
import struct
import _thread
from nrf24l01 import NRF24L01 # type: ignore
import servo  
from commons import constants as CONSTS

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
    NRF_SPI_BUS = SPI(0, sck=SCK_PIN, mosi=MOSI_PIN, miso=MISO_PIN, baudrate=8000000)
    nrf_module = NRF24L01(NRF_SPI_BUS, CSN_PIN, CE_PIN, channel=CONSTS.CHANNEL, payload_size=CONSTS.PAYLOAD_SIZE)
    nrf_module.reg_write(CONSTS.TRANSM_SPEED_REG, CONSTS.SPEED)
    nrf_module.reg_write(CONSTS.ACK_ENABLED_REG, CONSTS.ACK_ENABLED_VALUE)

    nrf_module.open_rx_pipe(1, CONSTS.TX_RX_PIPE)
    nrf_module.start_listening()
    print("NRF24L01 module setup complete. Ready to receive data.")    

# Серви та мотор
servo1 = servo.Servo(Pin(13))
#motor = machine.PWM(machine.Pin(12))
#motor.freq(1000)

# Лампочки
#led1 = machine.Pin(13, machine.Pin.OUT)
#led2 = machine.Pin(14, machine.Pin.OUT)

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
        if nrf_module.any():
            buf = nrf_module.recv()
            #print("Received:", buf)
            x1, x2, b1, b2, b3 = struct.unpack('BBBBB', buf)
            with lock:
                shared_data["x1"] = x1
                #shared_data["x2"] = x2
                #shared_data["b1"] = b1
                #shared_data["b2"] = b2
                #shared_data["last_packet"] = utime.ticks_ms()

# 🔵 ЯДРО 0: Серви, мотор і лампочки (гладке керування)
def control_loop():
    last_update = utime.ticks_ms()
    smooth_x1 = 128
    smooth_x2 = 128

    while True:
        now = utime.ticks_ms()

        with lock:
            target_x1 = shared_data["x1"]
        #   target_x2 = shared_data["x2"]
        #   b1 = shared_data["b1"]
        #   b2 = shared_data["b2"]
            last_packet = shared_data["last_packet"]

        # Плавне згладжування (слайдінг)
        smooth_x1 += (target_x1 - smooth_x1) * 0.1  # фактор згладжування
        #smooth_x2 += (target_x2 - smooth_x2) * 0.1

        # Серво
        angle1 = int((smooth_x1 / 255) * 180)
        #angle2 = int((smooth_x2 / 255) * 180)
        #servo1.write(angle1)
        servo1.write(target_x1)
        #servo2.write(angle2)

        # Лампочки
        #led1.value(b1)
        #led2.value(b2)

        # Мотор (тяга)
        #duty = int((smooth_x2 / 255) * 65535)
        #motor.duty_u16(duty)

        # Якщо пакетів нема вже 300 мс — аварійний режим
        #if utime.ticks_diff(now, last_packet) > 300:
        #    servo1.write(90)
        #    servo2.write(90)
        #    motor.duty_u16(0)

        #utime.sleep_ms(20)  # 50 Гц оновлення серв (реальний для сервоприводів)

powerOnLed()
startupSetup()
# Старт NRF прийому на ядрі 1
_thread.start_new_thread(nrf_loop, ())

# Головний цикл на ядрі 0
control_loop()

