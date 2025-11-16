import time

import cc1101
from crc import crc
from serialize import serialize

class CC1101(cc1101.CC1101):
  def send(self, data):
    if self.read_register(CC1101.TXBYTES, CC1101.STATUS_REGISTER) & CC1101.BITS_TX_FIFO_UNDERFLOW:
      self.write_command(CC1101.SIDLE)
      self.write_command(CC1101.SFTX)

    self.write_command(CC1101.SIDLE)
    self.write_burst(CC1101.TXFIFO, data)

    self.write_command(CC1101.SIDLE)
    self.write_command(CC1101.STX)

    while True:
      marcstate = self.read_register(CC1101.MARCSTATE, CC1101.STATUS_REGISTER) & CC1101.BITS_MARCSTATE
      if marcstate in [CC1101.MARCSTATE_IDLE, CC1101.MARCSTATE_TXFIFO_UNDERFLOW]:
        break

def get_meter_request(year, serial):
  raw = [0x13, 0x10, 0x00, 0x45]
  raw.append(year)
  raw.extend(serial.to_bytes(3, 'big'))
  raw.extend([0x00, 0x45, 0x20, 0x0a, 0x50, 0x14, 0x00, 0x0a, 0x40])
  raw.extend(crc(raw))

  packet = [0x50, 0x00, 0x00, 0x00, 0x03, 0xff, 0xff, 0xff, 0xff]
  packet.extend(serialize(raw))
  return bytes(packet)

def get_data(rf):
  wake_up = bytes([0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55])
  meter_request = get_meter_request(25, 174915)

  print(f'[+] get_data()')

  print(f'[+] No preamble, infinite length')
  rf.write_register(CC1101.MDMCFG2, 0x00)
  rf.write_register(CC1101.PKTCTRL0, 0x02)

  print(f'[+] Sending wake_up request .', end='')

  for i in range(100):
    rf.send(wake_up)
    print(f'.', end='')
    time.sleep_ms(20)

  print(f'')

  print(f'[+] Sending meter request')
  rf.send(meter_request)

  print(f'[+] 2-FSK preamble, fixed length')
  rf.write_register(CC1101.MDMCFG2, 0x02)
  rf.write_register(CC1101.PKTCTRL0, 0x00)

  rf.write_register(CC1101.MCSM1, 0x0f)
  rf.write_register(CC1101.MDMCFG2, 0x02)
  rf.write_register(CC1101.SYNC1, 0x55)
  rf.write_register(CC1101.SYNC0, 0x50)
  rf.write_register(CC1101.MDMCFG4, 0xf6)
  rf.write_register(CC1101.MDMCFG3, 0x83)
  rf.write_register(CC1101.PKTLEN, 0x01)

  rf.write_command(CC1101.SIDLE)
  rf.write_command(CC1101.SRX)

  print(f'[+] Awaiting data.', end='')
  ready = 0

  for i in range(2000):
    ready = rf.ready()
    if ready:
      break

    print('.', end='')
    time.sleep_ms(20)

  print(f'')

  if not ready:
    print(f'[-] Timeout awaiting data')
    return

  print(f'[+] Reading data.', end='')
  data = []

  for i in range(2000):
    size = rf.read_register(CC1101.RXBYTES, CC1101.STATUS_REGISTER) & CC1101.BITS_RX_BYTES_IN_FIFO
    if size > 0:
      data = rf.read_burst(CC1101.RXFIFO, size)
      break
    print(f'.', end='')
    time.sleep_ms(20)

  print(f'')
  print(f'0x{data:02x}')
  
  lqi = rf.read_register(CC1101.LQI)
  rssi = rf.read_register(CC1101.RSSI)
  freqest = rf.read_register(CC1101.FREQEST)

  print(f'[+] get_data() lqi=0x{lqi:02x}, rssi=0x{rssi:02x}, freqest=0x{freqest:02x}')
  

def set_frequency(rf, mhz):
  print(f"[+] set_frequency() frequency={mhz}")

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
  time.sleep_ms(5)

  marcstate = rf.read_register(CC1101.MARCSTATE) & CC1101.BITS_MARCSTATE
  print(f"[+] set_frequency() marcstate=0x{marcstate:02x}")

def main():
  rf = CC1101()
  partnum = rf.read_register(CC1101.PARTNUM)
  version = rf.read_register(CC1101.VERSION)

  print(f"[+] CC1101() partnum=0x{partnum:02x} version=0x{version:02x}")

  set_frequency(rf, 433.820)
  get_data(rf)

main()
