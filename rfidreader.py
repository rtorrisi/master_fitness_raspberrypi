import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import sys
reader = SimpleMFRC522()

def int2bytes(i, enc):
	return i.to_bytes((i.bit_length()+7) // 8, enc)

def convert_hex(str, enc1, enc2):
	return int2bytes(int.from_bytes(bytes.fromhex(str), enc1), enc2).hex()

while True:
	try:
		id = reader.read_id()
		card_no = str(int(convert_hex(hex(id)[2:-2], 'big', 'little'), 16))
		print(card_no.zfill(14))
	except KeyboardInterrupt:
		GPIO.cleanup()
		sys.exit(0)
	except:
		pass
	
GPIO.cleanup()
