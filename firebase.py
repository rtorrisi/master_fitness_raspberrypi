import pyrebase

class Firebase:
    def __init__(self, config):
        firebase_config = {
            "apiKey": config['apiKey'],
            "authDomain": config['authDomain'],
            "databaseURL": config['databaseURL'],
            "storageBucket": config['storageBucket'],
            "serviceAccount": config['serviceAccount']
        }

        self.firebase = pyrebase.initialize_app(firebase_config)
        self.database = self.firebase.database()
        self.storage = self.firebase.storage()

    def deleteFile(self, node, file_to_delete):
        try:
            self.storage.delete(node+'/'+file_to_delete)
            return True
        except Exception as e:
            print(e)
            return False


    def downloadFile(self, node, destination_path):
        self.storage.child(node).download(destination_path)
        return destination_path

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

    def update(self, node, data):
        try:
            self.database.child(node).update(data)
            return True
        except Exception as e:
            print(e)
            return False