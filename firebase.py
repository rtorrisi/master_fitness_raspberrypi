import pyrebase

class Firebase:
    def __init__(self, config):
        firebase_config = {
            "apiKey": config['apiKey'],
            "authDomain": config['authDomain'],
            "databaseURL": config['databaseURL'],
            "storageBucket": config['storageBucket']
        }

        self.firebase = pyrebase.initialize_app(firebase_config)
        self.database = self.firebase.database()
        self.storage = self.firebase.storage()
        self.auth = self.firebase.auth()
        self.user = self.auth.sign_in_with_email_and_password(config['email'], config['password'])

    def downloadFile(self, source_path, destination_path):
        self.storage.child(source_path).download(destination_path)

    def get(self, source_path):
        return self.database.child(source_path).get()

    def update(self, source_path, data):
        self.database.child(source_path).update(data)
