def _crc_table():
  table = []

  for i in range(256):
    crc = 0
    c = i

    for j in range(8):
      if (crc ^ c) & 0x0001:
        crc = (crc >> 1) ^ 0x8408
      else:
        crc = crc >> 1
      c = c >> 1

    table.append(crc)

  return table

def crc(packet):
  array = _crc_table()
  crc = 0

  for byte in packet:
    tmp = crc ^ byte
    crc = (crc >> 8) ^ array[tmp & 0xff]

  return crc.to_bytes(2, 'little')
