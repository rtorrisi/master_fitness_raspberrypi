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

    def deleteFile(self, node, file_to_delete):
        try:
            self.storage.delete(node+'/'+file_to_delete)
            return True
        except Exception as e:
            print(e)
            return False

    def getNode(self, node):
        return self.storage.child(node)

    def downloadFile(self, node, destination_path):
        f = self.storage.child(node)
        f.download(destination_path)

    def uploadFile(self, node, source_path):
        try:
            self.storage.child(node).put(source_path)
            return True
        except Exception as e:
            print(e)
            return False

    def set(self, node, key, data):
        try:
            self.database.child(node).child(key).set(data)
            return True
        except Exception as e:
            print(e)
            return False
            
    def get(self, node):
        return self.database.child(node).get()

    def remove(self, node):
        try:
            self.database.child(node).remove()
            return True
        except Exception as e:
            print(e)
            return False

    def update(self, node, data):
        try:
            self.database.child(node).update(data)
            return True
        except Exception as e:
            print(e)
            return False