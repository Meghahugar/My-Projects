import serial
import time

data = serial.Serial(
                  'COM5',
                  baudrate = 9600,
                  parity=serial.PARITY_NONE,
                  stopbits=serial.STOPBITS_ONE,
                  bytesize=serial.EIGHTBITS,                  
                  timeout=1
                  )

def ReadFinger():
  print('Start........')
  while True:
    d = data.read(12)
    d = d.decode('utf-8', 'ignore')
    d = d.strip()
    if d:
      print(d)
      break
    time.sleep(1)
  return d