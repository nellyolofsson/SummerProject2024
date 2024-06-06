from mqtt import MQTTClient
import time
from machine import Pin
import dht
import ujson
import secrets
import sys
import boot
import machine
import ubinascii

# Function to build JSON data
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

# DHT11 sensor setup
sensor = dht.DHT11(Pin(17))
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
# Create an MQTT client


# Connect to MQTT server
try:
    client = MQTTClient(client_id=CLIENT_ID, server=MQTT_SERVER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_KEY)
    time.sleep(0.1)
    client.connect()
    print(f"Connected to MQTT server at {MQTT_SERVER}")
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
            sensor.measure()
            temperature = sensor.temperature()
            humidity = sensor.humidity()
            print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
            
            tempObj = build_json("temperature", temperature)
            humidityObj = build_json("humidity", humidity)
            
            if tempObj:
                send_topic(tempObj, MQTT_TEMPERATURE_FEED)
            if humidityObj:
                send_topic(humidityObj, MQTT_HUMIDITY_FEED)
            
            time.sleep(10)  # Wait for 10 seconds before next reading
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)  # Wait a bit before retrying
except KeyboardInterrupt:
    print("Interrupted by user")
finally:
    boot.disconnect()
    print("Disconnected from WiFi.")
