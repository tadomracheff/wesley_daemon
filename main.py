import socket
import configparser
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import threading

from classes.postgres import Postgres


def listen_firestore():
    cred = credentials.Certificate(config["Firestore"]["service_account"])
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    callback_done = threading.Event()

    def on_snapshot(doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            send_to_client(doc)
        callback_done.set()

    doc_ref = db.collection(config["Firestore"]["listen_collection"])
    doc_watch = doc_ref.on_snapshot(on_snapshot)


def send_to_client(fs_doc):
    segment_id = postgres.get_location(fs_doc.to_dict(), config["common"]["rounding"])
    try:
        packet = "{user}:{segment};".format(user=config["users"][fs_doc.id], segment=segment_id)
        client_socket.send(str.encode(packet))
    except Exception as err:
        print("Error: ", err)
        client_socket.close()


config = configparser.ConfigParser()
config.read("config/settings.ini")

postgres = Postgres(config["PostgreSQL"])

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((config["SocketServer"]["host"], int(config["SocketServer"]["port"])))
server_socket.listen(1)
(client_socket, address) = server_socket.accept()

listen_firestore()

while True:
    pass
