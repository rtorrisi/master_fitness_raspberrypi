import pyrebase
from urllib.request import urlopen

class Firebase:
    def __init__(self, config):
        firebase_config = {
            "apiKey": config['apiKey'],
            "authDomain": config['authDomain'],
            "databaseURL": config['databaseURL'],
            "storageBucket": config['storageBucket'],
            "serviceAccount": config['serviceAccount']
        }

        try:
            self.firebase = pyrebase.initialize_app(firebase_config)
            self.database = self.firebase.database()
            self.storage = self.firebase.storage()
        except Exception as e:
            print(e)

    def checkConnection(self):
        try:
            response = urlopen('https://www.google.com/', timeout=10)
            return True
        except: 
            return False

    def deleteFile(self, node, file_to_delete):
        try:
            if self.checkConnection():
                self.storage.delete(node+'/'+file_to_delete)
                return True
            else: raise Exception("No connection")
        except Exception as e:
            print(e)
            return False

    def downloadFile(self, node, destination_path):
        if self.checkConnection():
            self.storage.child(node).download(destination_path)
            return destination_path
        else: raise Exception("No connection")

    def uploadFile(self, node, source_path):
        try:
            if self.checkConnection():
                self.storage.child(node).put(source_path)
                return True
            else: raise Exception("No connection")
        except Exception as e:
            print(e)
            return False

    def set(self, node, key, data):
        try:
            if self.checkConnection():
                self.database.child(node).child(key).set(data)
                return True
            else: raise Exception("No connection")
        except Exception as e:
            print(e)
            return False
            
    def get(self, node):
        if self.checkConnection():
            return self.database.child(node).get()
        else: raise Exception("No connection")

    def remove(self, node):
        try:
            if self.checkConnection():
                self.database.child(node).remove()
                return True
            else: raise Exception("No connection")
        except Exception as e:
            print(e)
            return False

    def update(self, node, data):
        try:
            if self.checkConnection():
                self.database.child(node).update(data)
                return True
            raise Exception("No connection")
        except Exception as e:
            print(e)
            return False