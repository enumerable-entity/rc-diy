PAYLOAD_SIZE = 5 # bytes for one packet
TX_RX_PIPE = b'1Node' 
CHANNEL = 100

TRANSM_SPEED_REG = 0x06 # Register for transmission speed
ACK_ENABLED_REG = 0x01 # Register for ACK enabled
ACK_ENABLED_VALUE = 0b00000000
SPEED = 0b00001010 # 2 Mbps