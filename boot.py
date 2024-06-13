# boot.py -- run on boot-up
from mysecrets import secrets
from time import sleep
import network
import ntptime


def connect():
    wlan = network.WLAN(network.STA_IF)         # Put modem on Station mode
    if not wlan.isconnected():                  # Check if already connected
        print('connecting to network...')
        wlan.active(True)                       # Activate network interface
        # set power mode to get WiFi power-saving off (if needed)
        wlan.config(pm = 0xa11140)
        wlan.connect(secrets["WIFI_SSID"], secrets["WIFI_PASSWORD"])  # Your WiFi Credential
        print('Waiting for connection...', end='')
        # Check if it is connected otherwise wait
        while not wlan.isconnected() and wlan.status() >= 0:
            print('.', end='')
            sleep(1)
    # Print the IP assigned by router
    ip = wlan.ifconfig()[0]
    print('\nConnected on {}'.format(ip))

     # Set the time using ntp
    try:
        ntptime.settime()
        print('Time synchronized successfully')
    except Exception as e:
        print('Failed to synchronize time:', e)
    return ip

def disconnect():
    wlan = network.WLAN(network.STA_IF)
    wlan.disconnect()
    wlan = None 
