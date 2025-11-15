from cc1101 import CC1101

def get_crc_array():
  crc_array = []

  for i in range(256):
    crc = 0
    c = i

    for j in range(8):
      if (crc ^ c) & 0x0001:
        crc = (crc >> 1) ^ 0x8408
      else:
        crc = crc >> 1
      c = c >> 1

    crc_array.append(crc)

  return crc_array

def get_crc(packet):
  
def get_meter_request(year, serial):
  packet = [0x13, 0x10, 0x00, 0x45]
  packet.append(year)
  packet.extend(serial.to_bytes(3, 'big'))
  packet.extend([0x00, 0x45, 0x20, 0x0a, 0x50, 0x14, 0x00, 0x0a, 0x40])
  return packet

def get_data(rf):
  wake_up = bytes([0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55])
  meter_request = get_meter_request(25, 174915)
  rf.write_register(CC1101.MDMCFG2, 0x00)
  rf.write_register(CC1101.PKTCTRL0, 0x02)

  for i in range(77):
    rf.send_data(wake_up)

  rf.send_data(meter_request)

  rf.write_register(CC1101.MDMCFG2, 0x02)
  rf.write_register(CC1101.PKTCTRL0, 0x00)

def set_frequency(rf, mhz):
  freq2 = 0
  freq1 = 0
  freq0 = 0

  while mhz > 26:
    mhz -= 26
    freq2 += 1

  while mhz > 0.1015625:
    mhz -= 0.1015625
    freq1 += 1

  while mhz > 0.00039675:
    mhz -= 0.00039675
    freq0 += 1

  rf.write_register(CC1101.IOCFG2, 0x0d)
  rf.write_register(CC1101.IOCFG0, 0x06)
  rf.write_register(CC1101.FIFOTHR, 0x47)
  rf.write_register(CC1101.SYNC1, 0x55)
  rf.write_register(CC1101.SYNC0, 0x00)
  rf.write_register(CC1101.PKTCTRL1, 0x00)
  rf.write_register(CC1101.PKTCTRL0, 0x00)
  rf.write_register(CC1101.FSCTRL1, 0x08)

  rf.write_register(CC1101.FREQ2, freq2)
  rf.write_register(CC1101.FREQ1, freq1)
  rf.write_register(CC1101.FREQ0, freq0)

  rf.write_register(CC1101.MDMCFG4, 0xf6)
  rf.write_register(CC1101.MDMCFG3, 0x83)
  rf.write_register(CC1101.MDMCFG2, 0x02)
  rf.write_register(CC1101.MDMCFG1, 0x00)
  rf.write_register(CC1101.MDMCFG0, 0x00)
  rf.write_register(CC1101.DEVIATN, 0x15)
  rf.write_register(CC1101.MCSM1, 0x00)
  rf.write_register(CC1101.MCSM0, 0x18)
  rf.write_register(CC1101.FOCCFG, 0x1d)
  rf.write_register(CC1101.BSCFG, 0x1c)
  rf.write_register(CC1101.AGCCTRL2, 0xc7)
  rf.write_register(CC1101.AGCCTRL1, 0x00)
  rf.write_register(CC1101.AGCCTRL0, 0xb2)
  rf.write_register(CC1101.WORCTRL, 0xfb)
  rf.write_register(CC1101.FREND1, 0xb6)
  rf.write_register(CC1101.TEST2, 0x81)
  rf.write_register(CC1101.TEST1, 0x35)
  rf.write_register(CC1101.TEST0, 0x09)

  rf.write_burst(CC1101.PATABLE, bytes([0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

  rf.write_command(CC1101.SIDLE)
  rf.write_command(CC1101.SCAL)

def main():
  rf = CC1101()
  set_frequency(rf, 433.820)

main()
