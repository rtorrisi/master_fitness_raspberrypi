from RFID import RFIDReader

if __name__ == "__main__":
    rfid_reader = RFIDReader('COM6')
    rfid_reader.start() 

    while True:
        try:
            pass
        except KeyboardInterrupt:
            break
    
    rfid_reader.stop()