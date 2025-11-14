# Meater+ Temperature Reader for Arduino Nano ESP32 (micropython)

This project aims to serve as an alternative to a clunky mobile app requiring an user to create an account on a 3rd party system just to read the temperature of their brisket.

## Hardware used

* Arduino Nano ESP32
* DS3231 RTC module (I2C)
* SSD1306 128x64 OLED display (I2C)

## Software used

* Arduino Nano ESP32 Micropython Firmware
* dfu-util (to flash the firmware)
* ampy (to upload the micropython code)

## Drivers used

* DS3231 driver by Peter Hinch
* SSD1306 driver copied from development branch of micropython
