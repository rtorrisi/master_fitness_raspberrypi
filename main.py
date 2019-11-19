from RFID import RFIDReader
from firebase import Firebase
from config import config

class WorkoutPlansManager:
    def __init__(self):
        self.firebase = Firebase(config)
        self.rfidReader = RFIDReader('COM6', handler_function=self.handler)

    def handler(self, card_no, state):
        if state:
            node = "users/"+card_no+"/untitled.jpg"
            self.firebase.downloadFile(node, "storage_data/"+card_no+".jpg")
        
        print("handler -> card %s (%u)" % (card_no, state))

    def run(self):    
        self.rfidReader.start() 

        while True:
            try:
                pass
            except KeyboardInterrupt:
                break
        
        self.rfidReader.stop()


if __name__ == "__main__":
    WPM = WorkoutPlansManager()
    WPM.run()