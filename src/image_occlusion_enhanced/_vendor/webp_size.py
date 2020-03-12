import struct
import os

# much credit to https://wiki.tcl-lang.org/page/Reading+WEBP+image+dimensions
# documentation from https://developers.google.com/speed/webp/docs/riff_container

def getDimensions(img_path):
  ''' Returns the width, height of a .webp file. '''

  with open(img_path, 'rb') as f:
    # read only 40 bytes
    data = f.read(40)
  
  header = struct.unpack('4si4s', data[:12])

  if header[0] != b'RIFF' or header[2] != b'WEBP':
    print(header)
    raise ValueError('Invalid webp header.')

  vp8_type = struct.unpack('4s', data[12:16])[0]
  # print(vp8_type)

  if vp8_type == b'VP8 ': # lossy format
    return __VP8_dims(data)
  elif vp8_type == b'VP8L': # loseless
    return __VP8L_dims(data)
  elif vp8_type == b'VP8X': # extended file format
    return __VP8X_dims(data)
  else:
    raise ValueError('Could not recognise webp type.')

def __VP8X_dims(data):
  def toint(start):
    bit_lst = list(map(
      lambda a: bin(a)[2:].zfill(8),
      struct.unpack('B'*3, data[start:start + 3])
    ))

    return int("".join(bit_lst[::-1]), 2)
  
  width, height = toint(24) + 1, toint(27) + 1
  return width, height

def __VP8_dims(data):
  width, height = struct.unpack('HH', data[26:30])
  return width, height

def __VP8L_dims(data):
  size_lst = list(struct.unpack('B' * 4, data[21:25]))

  width = struct.unpack('H',
    bytearray(
      [size_lst[0], size_lst[1] & 0b111111]
  ))[0] + 1
  
  height_lst = [
    bin(size_lst[-3] >> 6)[2:],
    bin(size_lst[-2])[2:].zfill(8),
    bin(size_lst[-1] & 0b1111)[2:]
  ]
  height = int("".join(height_lst[::-1]), 2) + 1

  return width, height