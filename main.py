import socket
import configparser
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import threading

from db.postgres import get_location


def listen_fs():
    cred = credentials.Certificate('config/serviceAccount.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    callback_done = threading.Event()

    def on_snapshot(doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            send(doc)
        callback_done.set()

    doc_ref = db.collection("location")
    doc_watch = doc_ref.on_snapshot(on_snapshot)


def send(fs_doc):
    segment_id = get_location(fs_doc.to_dict())
    try:
        packet = "{user}:{segment};".format(user=config["users"][fs_doc.id], segment=segment_id)
        client_socket.send(str.encode(packet))
    except Exception as err:
        print("Error: ", err)
        client_socket.close()


config = configparser.ConfigParser()
config.read("config/settings.ini")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5001))
server_socket.listen(1)
(client_socket, address) = server_socket.accept()

listen_fs()

while True:
    pass
