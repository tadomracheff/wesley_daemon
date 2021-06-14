import socket
import configparser
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import exceptions as FirebaseException
from psycopg2 import Error as Psycopg2Error
import threading
import signal
import sys

from db.postgres import Postgres


def listen_firestore():
    try:
        cred = credentials.Certificate(config["Firestore"]["service_account"])
    except (IOError, ValueError) as error:
        print(error)
        raise FirebaseException.InvalidArgumentError()

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
    packet = "{user}:{segment};".format(user=config["users"][fs_doc.id], segment=segment_id)

    try:
        client_socket.send(str.encode(packet))
    except socket.error as error:
        print("Ошибка при отправке пакета клиенту: ", error)
        client_socket.close()
        signal.raise_signal(signal.SIGPIPE)


def sig_handler(signum, frame):
    if signum == signal.SIGPIPE:
        raise socket.error()
    else:
        print("Остановлено")
        sys.exit(0)


config = configparser.ConfigParser()
config.read("config/settings.ini")

signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)

try:
    signal.signal(signal.SIGPIPE, sig_handler)

    postgres = Postgres(config["PostgreSQL"])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((config["SocketServer"]["host"], int(config["SocketServer"]["port"])))
    server_socket.listen(1)
    (client_socket, address) = server_socket.accept()

    listen_firestore()

    while True:
        pass

except FirebaseException.InvalidArgumentError as error:
    print("Ошибка подключения к FS")
except Psycopg2Error as error:
    print("Ошибка базы данных")
except socket.error as error:
    server_socket.close()
    print("Ошибка сокета", error)
except Exception as error:
    print("Неотловленное исключение", error)
