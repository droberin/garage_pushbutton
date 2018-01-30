from oled_screen import OLEDScreen
from network import WLAN
from time import sleep
from ubinascii import hexlify
from machine import unique_id, Pin

# This pin ID is almost a myth... check your device pin out
pin_id = 10
# Match pin_id data with pin_label so it can be shown on screen.
pin_label = "SD3"


push_button_max_duration = 4

pin = Pin(pin_id, Pin.OUT, Pin.PULL_UP)
pin.on()

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
