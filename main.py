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
import logging
from time import sleep

from db.postgres import Postgres


def listen_firestore():
    try:
        cred = credentials.Certificate(config["Firestore"]["service_account"])
    except (IOError, ValueError) as error:
        logging.critical("Ошибка чтения сертификата Firestore:", error)
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
        logging.info("Пакет {0} отправлен".format(packet))
    except socket.error as error:
        logging.critical("Ошибка при отправке пакета '{0}' клиенту: {1}".format(packet, error))
        client_socket.close()
        logging.info("Клиентский сокет закрыт")
        signal.raise_signal(signal.SIGPIPE)


def sig_handler(signum, frame):
    if signum == signal.SIGPIPE:
        raise socket.error("Ошибка при отправке пакета клиенту")
    else:
        sys.exit(0)


config = configparser.ConfigParser()
config.read("config/settings.ini")

signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)

try:
    logging.basicConfig(**config["Logging"])
except Exception as error:
    print(error)
    sys.exit(1)

try:
    signal.signal(signal.SIGPIPE, sig_handler)

    postgres = Postgres(config["PostgreSQL"])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((config["SocketServer"]["host"], int(config["SocketServer"]["port"])))
    logging.info("Открыт сокет {0}".format(server_socket.__str__()))
    server_socket.listen(1)
    (client_socket, address) = server_socket.accept()
    logging.info("Установлено соединение с {0}".format(client_socket.__str__()))

    listen_firestore()

    while True:
        sleep(1)
        pass

except (FirebaseException.InvalidArgumentError, Psycopg2Error) as error:
    pass
except socket.error as error:
    logging.critical("Ошибка сокета: {0}".format(error))
    server_socket.close()
    logging.info("Серверный сокет закрыт")
except Exception as error:
    logging.exception(error)
finally:
    try:
        del postgres
    except NameError as error:
        logging.error("Ошибка вызова деструктора соединения с БД: {0}".format(error))
    logging.shutdown()
    logging.critical("Демон остановлен\n")
