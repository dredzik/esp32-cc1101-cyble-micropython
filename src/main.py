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

    while True:
      marcstate = self.read_register(CC1101.MARCSTATE, CC1101.STATUS_REGISTER) & CC1101.BITS_MARCSTATE
      if marcstate in [CC1101.MARCSTATE_IDLE, CC1101.MARCSTATE_TXFIFO_UNDERFLOW]:
        break

  def read(self):
    data = bytearray()
    size = self.read_register(CC1101.RXBYTES, CC1101.STATUS_REGISTER) & CC1101.BITS_RX_BYTES_IN_FIFO

    if size > 0:
      data = self.read_burst(CC1101.RXFIFO, size)

    return data

  def wait_ready(self):
    print(f'[+] wait_ready')

    for i in range(2000):
      print(f'.', end='')
      ready = self.ready()

      if ready: break
      time.sleep_ms(20)

    print(f'')
    return ready

  def wait_read(self, length):
    print(f'[+] wait_read length={length}')
    data = []

    for i in range(2000):
      print(f'.', end='')
      data.extend(self.read())

      if (len(data) >= length): break
      time.sleep_ms(20)

    print(f'')

    for b in data:
      print(f'0x{b:02x} ', end='')

    print(f'')

    return data

  def cmd_receive(self):
    print(f'[+] cmd_receive')
    self.write_command(CC1101.SIDLE)
    self.write_command(CC1101.SRX)

  def cmd_flush_receive(self):
    print(f'[+] cmd_flush_receive')
    self.write_command(CC1101.SIDLE)
    self.write_command(CC1101.SFRX)

  def cmd_transmit(self):
    print(f'[+] cmd_transmit')
    self.write_command(CC1101.SIDLE)
    self.write_command(CC1101.STX)

  def cmd_flush_transmit(self):
    print(f'[+] cmd_flush_transmit')
    self.write_command(CC1101.SIDLE)
    self.write_command(CC1101.SFTX)

def get_meter_request(year, serial):
  raw = [0x13, 0x10, 0x00, 0x45]
  raw.append(year)
  raw.extend(serial.to_bytes(3, 'big'))
  raw.extend([0x00, 0x45, 0x20, 0x0a, 0x50, 0x14, 0x00, 0x0a, 0x40])
  raw.extend(crc(raw))

  packet = [0x50, 0x00, 0x00, 0x00, 0x03, 0xff, 0xff, 0xff, 0xff]
  packet.extend(serialize(raw))
  return bytes(packet)

def write_packet(rf):
  print(f'[+] write_packet')

  wu_packet = bytes([0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55])
  meter_packet = get_meter_request(25, 174915)

  rf.write_register(CC1101.MDMCFG2, 0x00)
  rf.write_register(CC1101.PKTCTRL0, 0x02)

  rf.cmd_transmit()

  print(f'[+] write_packet wake up')
  end = time.time_ns() + 2*1000*1000*1000

  while time.time_ns() < end:
    rf.send(wu_packet)
    print(f'.', end='')

  print(f'')

  print(f'[+] write_packet meter')
#time.sleep_ms(150)
  rf.send(meter_packet)

  rf.cmd_flush_transmit()

  rf.write_register(CC1101.MDMCFG2, 0x02)
  rf.write_register(CC1101.PKTCTRL0, 0x00)

def read_packet(rf, length):
  print(f'[+] read_packet length={length}')

  rf.write_register(CC1101.MCSM1, 0x0f)
  rf.write_register(CC1101.MDMCFG4, 0xf6)
  rf.write_register(CC1101.MDMCFG3, 0x83)
  rf.write_register(CC1101.MDMCFG2, 0x02)
  rf.write_register(CC1101.PKTCTRL0, 0x00)
  rf.write_register(CC1101.PKTLEN, 1)
  rf.write_register(CC1101.SYNC1, 0x55)
  rf.write_register(CC1101.SYNC0, 0x50)

  rf.cmd_receive()

  ready = rf.wait_ready()
  if not ready:
    print(f'[-] timeout')
    return

  data = rf.wait_read(1)
  if not data:
    print(f'[-] no data')
    return

  rf.cmd_flush_receive()

  rf.write_register(CC1101.MDMCFG4, 0xf8)
  rf.write_register(CC1101.MDMCFG3, 0x83)
  rf.write_register(CC1101.PKTCTRL0, 0x02)
  rf.write_register(CC1101.SYNC1, 0xff)
  rf.write_register(CC1101.SYNC0, 0xf0)

  rf.cmd_receive()

  if not rf.wait_ready():
    print(f'[-] timeout')
    return

  data = rf.wait_read(length)

  rf.cmd_flush_receive()

  rf.write_register(CC1101.MDMCFG4, 0xf6)
  rf.write_register(CC1101.MDMCFG3, 0x83)
  rf.write_register(CC1101.PKTCTRL0, 0x00)
  rf.write_register(CC1101.PKTLEN, 38)
  rf.write_register(CC1101.SYNC1, 0x55)
  rf.write_register(CC1101.SYNC0, 0x00)

  return data

def set_frequency(rf, mhz):
  print(f"[+] set_frequency frequency={mhz}")

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

def main():
  rf = CC1101()
  partnum = rf.read_register(CC1101.PARTNUM)
  version = rf.read_register(CC1101.VERSION)

  print(f"[+] CC1101() partnum=0x{partnum:02x} version=0x{version:02x}")

  set_frequency(rf, 433.820)
  write_packet(rf)
  sync_packet = read_packet(rf, 100)
  reading_packet = read_packet(rf, 684)

main()
