import sys
import threading
import serial

class SerialParser:
    (S_WAIT_START, S_READING, S_CARDNO_READ) = range(3)
    (OFF, ON) = range(2)

    def __init__(self, handler):
        self.handler = handler
        self.reset()

    def reset(self):
        self.state = self.S_WAIT_START
        self.card_no = 0

    def input(self, byte):
        byte_hex = byte.hex()
        # '02' start of text 
        if self.state == self.S_WAIT_START and byte_hex == '02':
            self.state = self.S_READING       
        elif self.state == self.S_READING:
             # '0d' carriage return, '0a' line feed 
            if byte_hex != '0d' and byte_hex != '0a':
                self.card_no = (self.card_no * 10) + int(byte)
            else:
                self.handler(str(self.card_no).zfill(14), self.ON)
                self.state = self.S_CARDNO_READ        
        # '1b' ESC
        elif self.state == self.S_CARDNO_READ and byte_hex == '1b':
            self.handler(str(self.card_no).zfill(14), self.OFF)
            self.reset()
        return None

class RFIDReader:
    def __init__(self, serial_port, handler_function):
        self.serial = serial.Serial()
        self.serial.port = serial_port
        self.serial.timeout = 3

        try:
            self.serial.open()
        except serial.SerialException as e:
            print("Could not open serial port %s: %s" % (self.serial.portstr, e))
            sys.exit(1)

        print("Listening on serial port: ", self.serial.portstr)
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
            self.serial.close()
        
    def reader(self):
        print('RFIDReader thread started')
        while self.alive:
            data = self.serial.read(1)            
            self.parser.input(data) # blocks on read
        self.alive = False
        print('RFIDReader thread terminated')