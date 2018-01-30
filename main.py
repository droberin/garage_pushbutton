from oled_screen import OLEDScreen
from network import WLAN
from time import sleep
from ubinascii import hexlify
from machine import unique_id, Pin
from umqtt.simple import MQTTClient
from umqtt.simple import MQTTException
from json import loads as json_loads
config_file = "mqtt.json"

mqtt_user = None
mqtt_pass = None
if stat(config_file):
    f = open(config_file, 'r')
    config_data = json_loads(f.read(1024))

if "mqtt_broker" in config_data:
    broker_address = config_data['mqtt_broker']
else:
    broker_address = "iot.eclipse.org"

if "client_id" in config_data:
    client_id = config_data['client_id']
else:
    client_id = ubinascii.hexlify(unique_id())

if "mqtt_user" in config_data:
    mqtt_user = config_data['mqtt_user']

if "mqtt_pass" in config_data:
    mqtt_pass = config_data['mqtt_pass']


if "topic" in config_data:
    mqtt_topic = config_data['topic']
else:
    mqtt_topic = b"ratoni/jail"

if "pin" in config_data and "pin_label" in config_data:
    pin_id = config_data['pin_id']
    pin_label = config_data['pin_label']
else:
    # This pin ID is almost a myth... check your device pin out
    pin_id = 10
    # Match pin_id data with pin_label so it can be shown on screen.
    pin_label = "SD3"


push_button_max_duration = 4

pin = Pin(pin_id, Pin.OUT, Pin.PULL_UP, value=1)
state = 0

screen = OLEDScreen()
wlan = WLAN()


def print_status():
    status_data = [
        "IP Address:",
        " " + wlan.ifconfig()[0],
        "Machine ID:",
        " " + str(hexlify(unique_id()))
    ]
    if screen.max_lines > 5:
        status_data += ["Pin:", str(pin_id) + " / " + pin_label]
    screen.print(status_data)


def sub_cb(topic, msg):
    print((topic, msg))
    if msg == b"push":
        print("Received push from MQTT")
        toggle_gate(2)


def toggle_gate(push_duration=1):
    if type(push_duration) is not int:
        print("toggle_gate: push_duration is not an integer...")
        return False
    if push_duration > push_button_max_duration:
        toggle_gate_data = [
            "==============="
            "LIMIT EXCEEDED:",
            "===============",
            "Time: " + str(push_duration) + " secs"
        ]
        screen.print(toggle_gate_data)
        return False
    toggle_gate_data = [
        "===============",
        " Toggling door ",
        "===============",
        "Time: " + str(push_duration) + " secs"
    ]
    screen.print(toggle_gate_data)
    # Do push button
    pin.off()
    sleep(push_duration)
    pin.on()
    if push_duration < 2:
        # So one can see screen for a sec!
        sleep(1)
    print_status()



while not wlan.isconnected():
    screen.print(["Waiting for WLAN", "Current state:", "Not connected"])
    sleep(1)

print_status()

if mqtt_pass and mqtt_user:
    c = MQTTClient(client_id, broker_address, user=mqtt_user, password=mqtt_pass)
    print("MQTTClient will use user and password")
else:
    c = MQTTClient(client_id, broker_address)
    print("MQTTClient set to anonymous mode")

try:
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(mqtt_topic)
except MQTTException:
    print("[CRITICAL] Error connecting to MQTT broker... May have a problem with credentials! (MQTTException")
    exit(1)
except TypeError:
    print("[CRITICAL] Error connecting to MQTT broker... May have a problem with credentials! (TypeError)")
    exit(1)

print("MQTTClient seems to be fine, waiting for the call...")
