config_file = open("app_data/config_file.txt", "r")
lines = config_file.readlines()

config = {
    "apiKey": lines[0][:-1],
    "authDomain": lines[1][:-1],
    "databaseURL": lines[2][:-1],
    "storageBucket": lines[3][:-1],
    "email": lines[4][:-1],
    "password": lines[5][:-1],
    "serviceAccount": lines[6][:-1],
    "filechooserpath": lines[7][:-1],
    "filedownloadpath": lines[8][:-1]
}