import sys
import threading
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

class SerialParser:
    (OFF, ON) = range(2)

    def __init__(self, handler):
        self.lastRFID = 0
        self.handler = handler
        self.state = self.OFF
        self.afk_count = 0

    def int2bytes(self, i, enc):
        return i.to_bytes((i.bit_length()+7) // 8, enc)

    def convert_hex(self, str, enc1, enc2):
        return self.int2bytes(int.from_bytes(bytes.fromhex(str), enc1), enc2).hex()

    def newUser(self, card_no):
        self.state = self.ON
        self.afk_count=0
        self.lastRFID = card_no
        self.handler(str(card_no).zfill(14))

    def input(self, data):
        if self.state == self.OFF:
            if data:
                card_no = int(self.convert_hex(hex(data)[2:-2], 'big', 'little'), 16)
                self.newUser(card_no)

        else: #self.state == self.ON:  
            if not data:
                self.afk_count += 1
            else:
                card_no = int(self.convert_hex(hex(data)[2:-2], 'big', 'little'), 16)
                if card_no != self.lastRFID:
                    self.newUser(card_no)
            
            if self.afk_count == 40:
                self.state = self.OFF            
            
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
        if self.alive:
            self.alive = False
            self.thread.join()
            GPIO.cleanup()
        
    def reader(self):
        while self.alive:
            try:
                data = self.RC522.read_id_no_block()
                self.parser.input(data) # blocks on read
            except Exception as e:
                print(e)
        self.alive = False
