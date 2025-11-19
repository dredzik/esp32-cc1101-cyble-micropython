# ESP32 + CC1101 + Everblu water meter + Micropython

This is a micropython implementation of the [genestealer/everblu-meters-esp8266-improved](https://github.com/genestealer/everblu-meters-esp8266-improved) project using cc1101 driver of the [erikdelange/ITHO-CVU-controller-in-MicroPython](https://github.com/erikdelange/ITHO-CVU-controller-in-MicroPython) project. The current state is as follows:

* The communication protocol between the device and the meter has been recreated in Micropython
* The packet creation has been recreated
* The response decoding has not been recreated
* The MQTT communication isn't there

I have realised slightly too late that the meter I have is not really compatible, but this did give me a lot of fun.

## Configuration

I have set the SPI settings in the cc1101.py to match what Xiao Seeed ESP32C6 board expects, because that's what I was working with. If you will be forking this and building something for public consumption, please make it configurable. In main.py there are METER_YEAR and METER_SERIAL variables that need setting. You're an adult, you'll figure it out.

## Research

The original author did an amazing job researching the protocol, there are however a few inconsistencies that I aimed to fix in this implementation.

### Packet structure

In the original code the author disables the preamble and the sync word `halRfWriteReg(MDMCFG2, MDMCFG2_NO_PREAMBLE_SYNC);` and then manually sends 0x55 0x55 packets over 2 seconds to wake up the water meter.

Instead we can utilise the built in functionality of the CC1101 chipset. As soon as you set the device in TX mode it will start sending a preamble (0x55 packets) for a set minimum. It will then continue sending the preamble until you provide it with data to send. Therefore if you enable the TX mode and sleep for 2 seconds, the radio will do the work for you.

Likewise the way the packet is constructed with just part of it being serialized with a prefix felt wrong. The synchronisation pattern defined like so:

```
uint8_t synch_pattern[] = {0x50, 0x00, 0x00, 0x00, 0x03, 0xFF, 0xFF, 0xFF, 0xFF};
```

Is actually just a manual implementation of the `0x00 0xff` sync word that can be produced directly with the CC1101 device. But before we get there let's clear out some things. The first byte is most likely wrong.

```
>>> bin(0x50)
'0b1010000'
```

If you shift left by 3 bits, you will get 0x00, with b101 being most likely part of the original preamble (0x55).

```
>>> bin(0x55)
'0b1010101'
```

Then if you look at 0x03 and shift it right by 2 bits, you'll just get start of 0xff. If we assume that the creators of the Everblu water meter are sane, then it is more likely that the 14ms of zeroes followed by 14ms of ones is just the sync word `0x00 0xff` in a sample rate that is slower than what the author assumed. I have therefore removed the custom implementation and instead set the CC1101 to what it needs to be.

That makes building of the original request packet significantly easier and less insane.
