config_file = open("config_file.txt", "r")
lines = config_file.readlines()

config = {
    "apiKey": lines[0][:-1],
    "authDomain": lines[1][:-1],
    "databaseURL": lines[2][:-1],
    "storageBucket": lines[3][:-1],
    "email": lines[4][:-1],
    "password": lines[5][:-1]
}