from db.firestore import listen
import time

listen()

while True:
    time.sleep(100)
