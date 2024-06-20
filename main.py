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
from lib.SendEmail import send_email_movment, send_email, test_send_email
from lib.seesaw import Seesaw
from lib.stemma_soil_sensor import StemmaSoilSensor

# Constants
MIN_MOISTURE_VALUE = 345 
MAX_MOISTURE_VALUE = 1500  # Sensorns värde i vatten (100% fuktighet)

#bright_value = 0
#dark_value = 7000
SLEEP_INTERVAL = 600  # Sleep interval in seconds

# Sensor Classes
class LightSensor:
    def __init__(self, pin):
        self.sensor = ADC(Pin(pin))
    
    def read_value(self):
        return self.sensor.read_u16()

class TempHumiditySensor:
    def __init__(self, pin):
        self.sensor = dht.DHT11(Pin(pin))
    
    def measure(self):
        self.sensor.measure()
    
    def temperature(self):
        return self.sensor.temperature()
    
    def humidity(self):
        return self.sensor.humidity()

class MovementSensor:
    def __init__(self, pin):
        self.sensor = Pin(pin, Pin.IN, Pin.PULL_UP)
    
    def is_detected(self):
        return self.sensor.value() == 0


# MQTT Functions
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

def connect_mqtt():
    client = MQTTClient(
        client_id=ubinascii.hexlify(machine.unique_id()),
        server=secrets["MQTT_SERVER"],
        port=secrets["MQTT_PORT"],
        user=secrets["MQTT_USER"],
        password=secrets["MQTT_KEY"]
    )
    time.sleep(0.1)
    client.connect()
    return client

# Initialization
# Defining sensors
i2c = machine.I2C(0, sda=machine.Pin(4), scl=machine.Pin(5), freq=400000)
# Light sensor
light_sensor = LightSensor(27)
# DHT temp and humidity
temp_humidity_sensor = TempHumiditySensor(17)
# Movement sensor
movement_sensor = MovementSensor(26)
# LED Lamp 
led = Pin("LED", Pin.OUT)
# Soil sensor
moisture_sensor = StemmaSoilSensor(i2c)

# WiFi Connection
try:
    ip = boot.connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")

# Connect to MQTT server
try:
    client = connect_mqtt()
    print(f"Connected to MQTT server at {secrets["MQTT_SERVER"]}")
except Exception as error:
    sys.print_exception(error, sys.stderr)
    print("Could not establish MQTT connection")
    boot.disconnect()
    print("Disconnected from WiFi.")
    sys.exit()

def read_sensors():
    try:
        temp_humidity_sensor.measure()
        temperature = temp_humidity_sensor.temperature()
        humidity = temp_humidity_sensor.humidity()
        light_value = light_sensor.read_value()
        darkness = round(light_value / 65535 * 100, 2)
        raw_moisture = moisture_sensor.get_moisture()
        moisture_percentage = round((raw_moisture - MIN_MOISTURE_VALUE) / (MAX_MOISTURE_VALUE - MIN_MOISTURE_VALUE) * 100, 2)

        print(f"Read Sensors - Temperature: {temperature}, Humidity: {humidity}, Light: {darkness}, Moisture: {moisture_percentage}%")

        return {
            "temperature": temperature,
            "humidity": humidity,
            "light": darkness,
            "moisture": moisture_percentage
        }
    except Exception as e:
        print(f"Error reading sensors: {e}")
        return None



def send_sensor_data(sensor_data):
    temp_json = build_json("temperature", sensor_data["temperature"])
    humidity_json = build_json("humidity", sensor_data["humidity"])
    light_json = build_json("light", sensor_data["light"])
    soil_json = build_json("soil", sensor_data["moisture"])
    
    if temp_json:
        send_topic(temp_json, secrets["MQTT_TEMPERATURE_FEED"])
    if humidity_json:
        send_topic(humidity_json, secrets["MQTT_HUMIDITY_FEED"])
    if light_json:
        send_topic(light_json, secrets["MQTT_LIGHT_FEED"])
    if soil_json:
        send_topic(soil_json, secrets["MQTT_SOIL_FEED"])

#temp_sensor.measure()
#tempValue = temp_sensor.temperature()
#humidValue = temp_sensor.humidity()

#raw_moisture = moistureSensor.get_moisture()

# Omvandla till procentandel (kalibrerad)
#moisture_percentage = round((raw_moisture - min_moisture_value) / (max_moisture_value - min_moisture_value) * 100, 2)
#light_value = led_pin.read_u16()

# Beräkna ljus i procent baserat på maximalt ljusvärde
#light_percentage = int((light_value / dark_value) * 100)

try:
    previous_day = None
    day_values = night_values = evening_values = {}
    while True:
        try:
            sensor_data = read_sensors()
            if sensor_data is None:
                print("Sensor data is None, skipping this loop iteration.")
                continue
            
            print(f"Sensor Data: {sensor_data}")
            
            current_time = time.localtime()
            hour = (current_time[3] + 2) % 24  # Adjust for timezone
            day = current_time[2]
            current_time_str = f"{hour:02}:{current_time[4]:02}"
            
            values = {
                "temp": sensor_data["temperature"],
                "humidity": sensor_data["humidity"],
                "groundmoist": sensor_data["moisture"],
                "light": sensor_data["light"],
                "time": current_time_str
            }

            #if movement_sensor.is_detected():
                #try:
                    #print("Movement detected")
                   # send_email_movment("nossfolonelly@gamil.com")
                    #send_email_movment("simonberg92@hotmail.se")
                    #print("Email sent successfully!")
                #except Exception as e:
                    #print(f"Email sending error: {e}")

            if hour == 3 and current_time[4] == 0 and day != previous_day:
                night_values = values.copy()
            if hour == 13 and current_time[4] == 0 and day != previous_day:
                day_values = values.copy()
            if hour == 18 and current_time[4] == 0 and day != previous_day:
                evening_values = values.copy()
                try:
                    send_email("nossfolonelly@gmail.com", day_values, night_values, evening_values)
                    previous_day = day
                    print("Email sent successfully")
                except Exception as e:
                    print(f"Email sending error: {e}")

            send_sensor_data(sensor_data)
            time.sleep(SLEEP_INTERVAL)
        except KeyboardInterrupt:
            print("Program interrupted by user")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)
except KeyboardInterrupt:
    print("Interrupted by user")
finally:
    boot.disconnect()
    print("Disconnected from WiFi.")