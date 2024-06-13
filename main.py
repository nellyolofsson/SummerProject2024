# main.py -- put your code here!
from mqtt import MQTTClient
import time
from machine import ADC, Pin
import dht
import micropython   # Needed to run any MicroPython code
import ujson
from mysecrets import secrets
import sys
import boot
import machine
import ubinascii
from lib.SendEmail import send_email_movment
from lib.seesaw import Seesaw
from lib.stemma_soil_sensor import StemmaSoilSensor

# Defining sensors
i2c = machine.I2C(0, sda=machine.Pin(4), scl=machine.Pin(5), freq=400000)

# Light sensor
led_pin = ADC(Pin(27))

# DHT air temp and moisture
temp_sensor = dht.DHT11(Pin(17))

# Client ID, unique to the microcontroller
CLIENT_ID = ubinascii.hexlify(machine.unique_id())

# LED Lamp 
led = Pin("LED", Pin.OUT)

# Movement sensor
movment = Pin(26, Pin.IN, Pin.PULL_UP)

# Ground Moisture sensor
moiistureSensor = StemmaSoilSensor(i2c)

# Build jason format for MQTT 
def build_json(variable_1, value_1):
    try:
        data = {variable_1: value_1}
        retValue = ujson.dumps(data)
        return retValue
    except:
        return None

# Sensing message to MQTT server
def send_topic(topicObject, topicName):
    print(topicObject)
    try:
        client.publish(topic=topicName, msg=topicObject)
        print("DONE")
    except Exception as e:
        print("FAILED")
        # We must add error hadling here if WiFi being unavailable here

# WiFi Connection
try:
    ip = boot.connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")

# Connect to MQTT server
try:
    client = MQTTClient(client_id=CLIENT_ID, server=secrets["MQTT_SERVER"], port=secrets["MQTT_PORT"], user=secrets["MQTT_USER"], password=secrets["MQTT_KEY"])
    time.sleep(0.1)
    client.connect()
    print(f"Connected to MQTT server at {secrets["MQTT_SERVER"]}")
except Exception as error:
    sys.print_exception(error, sys.stderr)
    print("Could not establish MQTT connection")
    boot.disconnect()
    print("Disconnected from WiFi.")
    sys.exit()

# Main loop for reading sensor data
try:
    while True:
        try:
            movment_detected = movment.value()
            print(movment_detected)
            light_value = led_pin.read_u16()
            print(f"Light sensor value: {light_value}")
            mooisture = moiistureSensor.get_moisture()
            print(f"Moisture: {mooisture}")
            darkness = round(light_value / 65535 * 100, 2)
            print(f"Darkness: {darkness}%")
            if darkness >= 70:
                print("Darkness is {darkness}%, LED turned on".format(darkness))
                led.on()
            else:
                print("It is enough light, no need to turn the LED on")
                led.off()
            if movment_detected == 0:  
                print("Movement detected")
                send_email_movment("gamingbullarna@gmail.com")
                print("Mail was sent!")
            temp_sensor.measure()
            temperature = temp_sensor.temperature()
            humidity = temp_sensor.humidity()
            print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
            
            tempObj = build_json("temperature", temperature)
            humidityObj = build_json("humidity", humidity)
            lightObj = build_json("light", light_value)
            soilObj = build_json("soil", mooisture)
            
            
            if tempObj:
                send_topic(tempObj, secrets["MQTT_TEMPERATURE_FEED"])
            if humidityObj:
                send_topic(humidityObj, secrets["MQTT_HUMIDITY_FEED"])
            if lightObj:
                send_topic(lightObj, secrets["MQTT_LIGHT_FEED"])
            if soilObj:
                send_topic(soilObj, secrets["MQTT_SOIL_FEED"])
            
            time.sleep(15)  # Wait for 15 seconds before next reading
        except Exception as e:
          print(f"Error in main loop: {e}")
          time.sleep(5)  # Wait a bit before retrying
except KeyboardInterrupt:
    print("Interrupted by user")
finally:
    boot.disconnect()
    print("Disconnected from WiFi.")