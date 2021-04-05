import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import threading


def listen():
    cred = credentials.Certificate('config/serviceAccount.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    callback_done = threading.Event()

    def on_snapshot(doc_snapshot, changes, read_time):
        print('here')
        for doc in doc_snapshot:
            print(f'Received document snapshot: {doc.id}')
            print(doc.to_dict())
        callback_done.set()

    doc_ref = db.collection('location')

    doc_watch = doc_ref.on_snapshot(on_snapshot)
