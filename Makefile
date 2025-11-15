all: upload

flash-micropython:
	esptool --port /dev/tty.usbmodem* write_flash 0x0 firmware/ESP32C6_MicroPython.bin

upload:
	ampy -p /dev/tty.usbmodem* put src/cc1101.py
	ampy -p /dev/tty.usbmodem* put src/crc.py
	ampy -p /dev/tty.usbmodem* put src/main.py
	ampy -p /dev/tty.usbmodem* ls
	ampy -p /dev/tty.usbmodem* reset
