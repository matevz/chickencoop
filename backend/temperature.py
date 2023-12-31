import adafruit_dht
import threading
import time

from config import DHT22_PIN

READ_TEMP = False
SENSOR = None

# Sliding window (humidity, temperature) latest measures.
sw = [(0,0)]*5

# Main temperature thread.
t: threading.Thread


def init_temperature_service():
    global READ_TEMP, SENSOR, t
    READ_TEMP = True
    SENSOR = adafruit_dht.DHT22(DHT22_PIN)

    t = threading.Thread(target=read_temp_and_humidity)
    t.start()


def stop_temperature_service():
    global READ_TEMP, SENSOR, t
    READ_TEMP = False  # stop the temperature thread
    SENSOR.exit()
    t.join()


def read_temp_and_humidity():
    global READ_TEMP, SENSOR, sw
    while READ_TEMP:
        try:
            t, h = SENSOR.temperature, SENSOR.humidity
            # Thread-safe appending the new measurement.
            sw2 = sw[0:]
            sw2.append( (h,t) )
            sw = sw2[1:]
        except RuntimeError as error:
            SENSOR.exit()
            time.sleep(2.0)
            SENSOR = adafruit_dht.DHT22(DHT22_PIN)
        time.sleep(2.0)


def compute_avg_humid_temp():
    global sw

    avgH = 0
    avgT = 0
    for (h, t) in sw:
        avgH += h
        avgT += t
    avgH /= len(sw)
    avgT /= len(sw)

    return (avgH, avgT - 1.9)