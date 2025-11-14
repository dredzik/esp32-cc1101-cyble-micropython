from cc1101 import CC1101
import time

def get_data(rf):
  wbytes = bytes([0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55])
  rf.write_register(CC1101.MDMCFG2, 0x00)
  rf.write_register(CC1101.PKTCTRL0, 0x02)
  rf.write_burst(CC1101.TXFIFO, wbytes)
  rf.write_command(CC1101.STX)
  time.sleep(0.010)
  status = rf.read_register(CC1101.MARCSTATE, CC1101.STATUS_REGISTER) & CC1101.BITS_MARCSTATE
  print(status)

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

  time.sleep(0.005)

def main():
  rf = CC1101()
  set_frequency(rf, 433.820)

main()
