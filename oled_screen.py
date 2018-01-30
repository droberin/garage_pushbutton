from machine import I2C, Pin
import ssd1306
from time import sleep


class OLEDScreen:
    oled = None
    i2c = None
    max_lines = 4
    version = "0.1"

    def __init__(self, width=128, height=64, max_lines=6):
        self.i2c = I2C(scl=Pin(4), sda=Pin(5))
        self.oled = ssd1306.SSD1306_I2C(width, height, self.i2c)
        self.max_lines = max_lines
        initial_message = [
            "================",
            "Garage Door (" + self.version + ")",
            "================",
            "Please, wait...",
            "===============",
        ]
        self.print(initial_message)
        sleep(2)

    def print(self, message=['Empty data print']):
        self.oled.fill(0)
        count = 0
        for data_message in message:
            if count < self.max_lines:
                self.oled.text(data_message, 0, (10 * count))
                count += 1
            else:
                break
        self.oled.show()


if __name__ == '__main__':
    print("Don't use this lib as main source, bruv")
