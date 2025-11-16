def _bits(byte):
  return [(byte >> i) & 0x1 for i in range(8)]

def _byte(bits):
  byte = 0

  for bit in bits:
    byte <<= 1
    byte |= bit

  return byte

def serialize(packet):
  bits = []
  result = []

  for byte in packet:
    bits.extend([1, 1, 1, 0])
    bits.extend(_bits(byte))

  while len(bits) % 8:
    bits.append(1)

  while len(bits):
    result.append(_byte(bits[:8]))
    bits = bits[8:]

  return result
