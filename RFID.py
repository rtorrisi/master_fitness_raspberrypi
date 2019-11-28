import sys
import threading
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

class SerialParser:
    (OFF, ON) = range(2)

    def __init__(self, handler):
        self.handler = handler
        self.reset()

    def int2bytes(self, i, enc):
        return i.to_bytes((i.bit_length()+7) // 8, enc)

    def convert_hex(self, str, enc1, enc2):
        return self.int2bytes(int.from_bytes(bytes.fromhex(str), enc1), enc2).hex()

    def reset(self):
        self.state = self.OFF
        self.card_off_count = 0

    def input(self, data):
        if self.state == self.ON:
            if data:
                self.card_off_count = 0
            else:
                self.card_off_count += 1
            if self.card_off_count == 15:
                print("CARD OFF")
                self.state = self.OFF
                self.card_off_count = 0
            
        elif self.state == self.OFF and data:
            print("CARD ON")
            self.state = self.ON
            card_no = int(self.convert_hex(hex(data)[2:-2], 'big', 'little'), 16)
            self.handler(str(card_no).zfill(14))            
            
class RFIDReader:
    def __init__(self, handler_function):
        self.RC522 = SimpleMFRC522()
        self.parser = SerialParser(handler=handler_function)
        
    def start(self):
        self.alive = True
        self.thread = threading.Thread(target=self.reader)
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        print('stopping')
        if self.alive:
            self.alive = False
            self.thread.join()
            GPIO.cleanup()
        
    def reader(self):
        print('RFIDReader thread started')
        while self.alive:
            try:
                data = self.RC522.read_id_no_block()
                self.parser.input(data) # blocks on read
            except Exception as e:
                print(e)
        self.alive = False
        print('RFIDReader thread terminated')
