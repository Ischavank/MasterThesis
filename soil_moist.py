import spidev
import time

# Setup SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0 (CE0)
spi.max_speed_hz = 1350000

# Read from MCP3008 channel (0–7)
def read_adc(channel):
    rounds = 5

    if not 0 <= channel <= 7:
        raise ValueError("Channel must be 0-7")
    adc = spi.xfer2([1, (8 + channel) << 4, 0])

    added_percentages = 0
    for i in range(rounds):
        raw = ((adc[1] & 3) << 8) + adc[2]
        added_percentages += (100 - ((raw / 1023.0) * 100))
        time.sleep(1)

    value = added_percentages / rounds
    return value

